# M-Pesa AI Assistant — Complete System

A platform that reads M-Pesa SMS from Android devices, stores transactions
in Excel files, and gives users access to their financial data only through
WhatsApp — plus a full admin dashboard for managing users, transactions,
analytics, and system health. No database, no AI in this build — Excel
files and rule-based logic only, with a dedicated AI service layer wired in
and ready for future use.

This folder contains everything built across all six phases.

## Folder map

```
mpesa-ai-assistant/
  backend/       Phases 1, 2, 3, 4 — Excel storage engine, FastAPI core,
                 reports/analytics, WhatsApp integration
  frontend/      Phase 6 — Next.js admin dashboard
  android-app/   Phase 5 — Android SMS Reader app (Kotlin)
  README.md      This file
```

Each folder has its own README with full setup instructions, testing steps,
and notes on what was verified in the build environment. This file is the
map connecting them and the order to bring them up.

## What's in each phase

| Phase | What it is | Folder |
|---|---|---|
| 1 | Excel Storage Engine — thread-safe atomic read/write, Users/Transactions/Analytics/SystemLogs.xlsx, duplicate prevention, backups | `backend/app/excel_engine/` |
| 2 | FastAPI Backend Core — JWT auth, RBAC, user & transaction CRUD, rate limiting | `backend/app/api/`, `backend/app/core/` |
| 3 | Reports & Analytics — persisted monthly/spending/income rollups, downloadable PDF/Excel statements | `backend/app/excel_engine/analytics.py`, `backend/app/services/report_generator.py` |
| 4 | WhatsApp Assistant — mock service (no credentials needed) + real Cloud API service, rule-based command bot | `backend/app/services/whatsapp/`, `backend/app/services/whatsapp_bot.py` |
| 5 | Android SMS Reader — parses M-Pesa SMS, offline queue, background sync | `android-app/` |
| 6 | Admin Dashboard — Next.js/TypeScript/Tailwind, all 8 required pages, RBAC-aware nav | `frontend/` |

An AI service layer (`backend/app/services/ai_service.py`) exists as a
placeholder throughout — every function it exposes returns a rule-based or
static response today, but the interface is what future AI features
(financial insights, smart categorization, NLU for WhatsApp) would plug
into without changing anything else in the system.

## Bring-up order

The pieces depend on each other in this order:

1. **Backend first, always.** Nothing else works without it.
2. **Admin dashboard** and **Android app** are independent of each other —
   bring up whichever you need. Both only need the backend running.
3. **WhatsApp** works in mock mode out of the box (no setup) — see
   `backend/README.md`'s Phase 4 section for going live with real
   credentials later.

Quick start (see `backend/README.md` for full detail):

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then edit JWT_SECRET_KEY and DEVICE_API_KEY
uvicorn app.main:app --reload --port 8000
```

In a second terminal, create your first admin:

```bash
cd backend && source venv/bin/activate
python scripts/create_super_admin.py
```

Then bring up the dashboard:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000` and sign in with the admin account you just created.

For the Android app, open `android-app/` in Android Studio — see
`android-app/README.md` for the emulator/physical-device setup and how to
test with a simulated M-Pesa SMS.

## What was verified vs. what needs your environment

This was built in a sandbox with no network access, so nothing here was
built/run in a real Node, Python venv, or Android Studio environment
end-to-end. Here's what was actually checked, and what's still on you:

- **Backend**: the Excel engine logic (categorization, duplicate
  prevention, search, spending summaries, backup/restore, analytics
  rollups) was executed directly and confirmed correct. PDF generation was
  rendered to an image and visually inspected. `fastapi`/`jose`/`passlib`/
  `apscheduler`/`httpx` aren't installed in this sandbox, so the route
  layer itself wasn't executed — but it's a thin wrapper around
  already-verified logic. Run `pip install -r requirements.txt` and it
  should run as-is.
- **Frontend**: every `.ts`/`.tsx` file passed a TypeScript syntax and
  undefined-reference check with zero errors. `npm install` / `next build`
  weren't run (no network). Run `npm run build` as your first check.
- **Android app**: every `.kt` file was checked for balanced braces and
  consistent imports; every `.xml` resource file was validated as
  well-formed (this caught and fixed one real bug — an invalid XML comment
  in the network security config). The SMS parsing regexes were ported to
  Python and tested against six realistic M-Pesa message samples, all
  parsing correctly. Gradle/Android Studio weren't available, so
  `./gradlew build` hasn't been run — do that first.

None of this replaces actually running each piece — treat the above as "the
logic has been exercised," not "this is production-tested."

## Launch prep — next steps

Once you've got all three pieces running locally and have poked at them,
the remaining work to actually launch is:

1. **Environment hardening** — real secrets (JWT key, device API key), HTTPS,
   CORS locked to your real domain, `ENABLE_WHATSAPP_SIMULATOR=false`.
2. **Deployment** — where the backend runs (a VM, a container platform),
   where the dashboard runs (Vercel or similar, or alongside the backend),
   and where Excel files + backups persist (a disk that survives restarts —
   this matters more than usual since Excel files are the only datastore).
3. **WhatsApp going live** — real Meta Cloud API credentials, webhook
   pointed at your public backend URL.
4. **Android distribution** — signing the app, and how it gets onto phones
   (internal testing track, direct APK, etc. — this isn't a consumer Play
   Store app in the traditional sense since it needs SMS permissions tied
   to a specific backend).
5. A go-live checklist and rollback plan.

Happy to work through all of this with you when you're ready.
