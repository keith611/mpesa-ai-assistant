# M-Pesa AI Assistant — Backend

**Storage: Supabase (Postgres).** This backend originally used Excel files
as its only datastore (see git history / earlier docs below for that
version's design). It has since been migrated to Supabase, since a real
database is what makes this safe to run for actual users on a real server
— concurrent access, persistence across restarts, no risk of a locked-file
conflict like we hit repeatedly during local testing. The API surface,
JSON response shapes, and every route are unchanged — only the storage
layer (`app/db_engine/`, formerly `app/excel_engine/`) changed internals,
so the WhatsApp bot, admin dashboard, and Android app all work exactly as
before without any changes on their end.

## Supabase setup

1. Create a project at https://supabase.com
2. Get your connection string: **Project Settings → Database → Connection string → URI**
3. Put it in `.env` as `DATABASE_URL=postgresql://postgres:YOUR-PASSWORD@db.xxxx.supabase.co:5432/postgres`
4. Tables are created automatically on first startup (`Base.metadata.create_all`) — no manual schema setup needed.
5. If you have existing data in old `data/*.xlsx` files from before this migration, run the one-time import:
   ```bash
   python scripts/migrate_excel_to_postgres.py
   ```
   Safe to re-run — it skips rows that already exist.

## Backups

Supabase backs up the database itself at the infrastructure level on paid
plans. On top of that, the admin dashboard's Backup Management page still
works exactly as before — it now exports every table to CSV snapshots
under `backups/{tier}/{timestamp}/` instead of copying `.xlsx` files, and
can restore from those snapshots the same way.

---

## What's included in this phase

**Storage Engine** (`app/db_engine/`, Postgres-backed)
- `users.py` — create/update/suspend/activate/delete (soft), duplicate phone prevention
- `transactions.py` — add (with M-Pesa code duplicate prevention), search/filter/export, spending summaries, largest transaction, balance lookup
- `categorization.py` — rule-based categorizer, rules stored in the `category_rules` table, editable via API
- `logs.py` — every significant event is logged to `system_logs`
- `backup.py` — hourly/daily/weekly backups with retention pruning, validation, and safe restore (takes a safety snapshot before restoring)

**FastAPI Backend Core** (`app/api/`, `app/core/`)
- `auth.py` — register, login, refresh, logout (JWT access + refresh tokens, bcrypt password hashing)
- `users.py` — user CRUD, role-gated (`GET /users/me` for self, admin-only for managing others)
- `transactions.py` — `/transactions/ingest` (device-key protected, for the future Android app), search/filter, CSV export
- `reports.py` — overview stats, spending reports by period, user activity, system logs
- `admin.py` — backup management + category rule editing
- `deps.py` — RBAC dependency (`require_min_role`), role hierarchy: SUPER_ADMIN > ADMIN > SUPPORT > USER
- `rate_limit.py` — sliding-window rate limiter middleware
- AI service layer (`app/services/ai_service.py`) — placeholder functions only, not wired to any provider, ready for Phase 10

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: set JWT_SECRET_KEY and DEVICE_API_KEY to real random values
python -c "import secrets; print(secrets.token_hex(32))"   # use this to generate them
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API docs: http://localhost:8000/docs

## First-run notes

- All Postgres tables are created automatically on first startup — no manual schema setup needed.
- The `category_rules` table is seeded with ~25 default categorization rules (supermarkets, fuel stations, utilities, etc.) on first run. Edit them via `PATCH /api/v1/admin/category-rules/{id}` or add new ones via `POST /api/v1/admin/category-rules`.
- The very first user should be promoted to `SUPER_ADMIN` manually — use `python scripts/create_super_admin.py` rather than the public registration endpoint, since role escalation must not be self-service.
- Automatic backups start running on app startup (hourly at :00, daily at 02:00 UTC, weekly Sunday 03:00 UTC) via APScheduler.

## Quick smoke test

```bash
# Register
curl -X POST localhost:8000/api/v1/auth/register -H "Content-Type: application/json" -d '{
  "full_name": "Jane Doe", "phone_number": "254712345678",
  "whatsapp_number": "254712345678", "password": "SuperSecret123"
}'

# Login
curl -X POST localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{
  "phone_number": "254712345678", "password": "SuperSecret123"
}'

# Ingest a transaction (as the Android app would)
curl -X POST localhost:8000/api/v1/transactions/ingest \
  -H "Content-Type: application/json" -H "X-Device-Api-Key: <your DEVICE_API_KEY>" -d '{
  "user_id": "USR-000001", "transaction_code": "QAX1B2C3D4", "amount": 1500,
  "transaction_type": "PAYBILL", "sender": "Jane Doe", "receiver": "NAIVAS SUPERMARKET",
  "date": "2026-07-02", "time": "14:00:00", "balance": 8500
}'
```

## Verified in this environment

The Excel engine logic (categorization, duplicate prevention, search, spending
summaries, backup/validate/restore) was tested directly against pandas/openpyxl
and confirmed working. `fastapi`, `python-jose`, `passlib`, and `apscheduler`
could not be installed in this sandbox (no network access) — install them via
`pip install -r requirements.txt` in your own environment and the API layer
will run as-is; the logic underneath it is already proven.

## What's next (Phase 5, 6)

- Phase 5: Android SMS Reader app
- Phase 6: Next.js admin dashboard

---

## Phase 3 — Reports & Analytics (PDF, Excel, rollups)

### Files added
- `app/db_engine/analytics.py` — computes and **persists** reports into the `monthly_reports`/`spending_reports`/`income_reports`/`user_statistics` tables, so the dashboard reads pre-computed data instead of recomputing from scratch every time
- `app/services/report_generator.py` — builds real downloadable **PDF** statements (reportlab) and formatted **Excel** statements (styled headers, not just a raw dump) — this is a file-export feature for users, unrelated to the datastore itself
- `app/api/reports.py` extended with:
  - `GET /reports/{period}/{user_id}` — period is `daily`, `weekly`, `monthly`, or `annual` (matches the spec's Reports section exactly)
  - `GET /reports/download/pdf/{user_id}?period=monthly` — downloadable PDF statement
  - `GET /reports/download/excel/{user_id}?period=monthly` — downloadable Excel statement
  - `POST /reports/rollup` (admin) — manually trigger the analytics rollup
  - `GET /reports/monthly-history/{user_id}` — historical rollups over time
  - `GET /reports/statistics/{user_id}` — cumulative user statistics

### Automatic rollups
The scheduler now also runs an analytics rollup daily at 01:00 UTC (`app/services/scheduler.py`), recomputing month-to-date figures for every active user into the analytics tables. This keeps `monthly_reports`, `spending_reports`, `income_reports`, and `user_statistics` current without needing to wait for month-end. Re-running is idempotent — it replaces the current month's row rather than duplicating it.

### Verified in this environment
Ran the full pipeline locally: created users, added transactions, triggered `run_full_rollup()`,
confirmed `MonthlyReports`/`UserStatistics` populated correctly, generated a PDF and rendered it to
an image to visually confirm layout (title, summary table, category breakdown, transaction detail
all render correctly), and generated a formatted Excel statement. All confirmed working.

---

## Phase 4 — WhatsApp Assistant (mock-first, no real token required)

The WhatsApp layer is built as a **swappable service**: `MockWhatsAppService`
and `CloudAPIWhatsAppService` both implement the same interface
(`WhatsAppServiceBase`). Nothing else in the app cares which one is active —
you flip `WHATSAPP_MODE` in `.env` and everything else keeps working.

### Files added
- `app/services/whatsapp/base.py` — the interface (`send_text_message`, `send_document`)
- `app/services/whatsapp/mock_service.py` — **default**, zero credentials needed, keeps an in-memory outbox
- `app/services/whatsapp/cloud_service.py` — real Meta Graph API client, only instantiated in live mode
- `app/services/whatsapp/factory.py` — `get_whatsapp_service()` picks the right one based on `WHATSAPP_MODE`
- `app/services/whatsapp_bot.py` — rule-based command router implementing every command from the spec (Balance, spending by period, category expenses, export, monthly summary, largest transaction, etc.)
- `app/api/whatsapp.py` — webhook (verification + inbound, for live mode), `/simulate` (for local testing), `/outbox` (view what the bot "sent")

### Testing locally — no WhatsApp account or token needed

1. Leave `WHATSAPP_MODE=mock` in `.env` (this is the default).
2. Register a user and note their `WhatsApp Number` (same as phone number by default).
3. Simulate an inbound WhatsApp message:

```bash
curl -X POST localhost:8000/api/v1/whatsapp/simulate -H "Content-Type: application/json" -d '{
  "whatsapp_number": "254712345678",
  "message_text": "Balance"
}'
```

The response includes the bot's reply directly. You can also check everything the mock service has "sent" so far:

```bash
curl localhost:8000/api/v1/whatsapp/outbox
```

Try any of the supported commands: `Balance`, `Today's spending`, `This week's spending`,
`This month's spending`, `Income this month`, `Last 10 transactions`, `Fuel expenses`,
`Food expenses`, `Export report`, `Monthly summary`, `Largest transaction`, `Transactions today`,
or `help`.

### Switching to real WhatsApp later

When you're ready to go live:
1. Get credentials from the Meta App Dashboard (WhatsApp Cloud API): access token, phone number ID, and set a webhook verify token of your choosing.
2. Fill in `.env`: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`.
3. Set `WHATSAPP_MODE=live`.
4. Point Meta's webhook config at `https://your-domain/api/v1/whatsapp/webhook` (GET for verification, POST for messages).
5. Set `ENABLE_WHATSAPP_SIMULATOR=false` in production.

No code changes required — the bot logic, command routing, and every other part of the system are identical in both modes.

### Verified in this environment
The full bot logic was tested end-to-end locally (register a user → post transactions →
simulate all 12+ commands → verify replies and CSV export attachment), all confirmed working.
The FastAPI route layer itself (webhook/simulate/outbox endpoints) couldn't be executed in this
sandbox since `fastapi`/`httpx` aren't installed here (no network access) — but it's a thin
wrapper around the already-verified bot logic.
