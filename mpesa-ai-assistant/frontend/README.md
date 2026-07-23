# M-Pesa AI Assistant — Admin Dashboard (Phase 6)

Next.js 14 (App Router) + TypeScript + Tailwind CSS admin dashboard for the
M-Pesa AI Assistant platform. Talks to the Phase 1-4 FastAPI backend only —
never touches the Excel files directly.

## Design

- **Palette**: deep emerald (`#0F6659`) primary against a near-black sidebar
  (`#101F1B`) and a soft sage-white canvas (`#F5F8F6`) — distinct from both
  Safaricom's brand green and generic SaaS blue.
- **Type**: Sora for headings, IBM Plex Sans for UI text, IBM Plex Mono for
  every number — amounts, IDs, timestamps — so the ledger reads with
  financial precision (aligned figures, tabular numerals).
- **Signature element**: the "system pulse" rail in the topbar — small status
  dots for API / WhatsApp / SMS sync / Backup health, always visible. It's
  functional, not decorative: it's the same System Monitoring data the spec
  asks for, just always-on instead of buried in a settings page.

## Pages

| Route | Purpose | Min role |
|---|---|---|
| `/login` | Phone number + password sign-in | — |
| `/overview` | KPI cards, recent transactions | Support |
| `/users` | Search/filter, suspend/activate | Support (suspend needs Admin) |
| `/users/[id]` | Profile, statistics, recent transactions | Support |
| `/transactions` | Search, filter, CSV export | Support |
| `/analytics` | Income/expense chart, monthly rollup history, manual rollup trigger | Support |
| `/reports` | Download PDF/Excel statements per user/period | Support |
| `/system` | Backup management, error logs, activity log | Admin |
| `/settings/category-rules` | Add/edit/deactivate/delete categorization rules | Admin |

Navigation automatically hides items the signed-in role can't access, and the
API layer enforces the same rules server-side — the frontend hiding a link is
a convenience, not the security boundary.

## Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# edit .env.local if your backend isn't on localhost:8000
npm run dev
```

Open http://localhost:3000. Make sure the Phase 1-4 backend is running first
(`uvicorn app.main:app --reload --port 8000` from the `backend/` folder), and
that you've created at least one admin user (`python scripts/create_super_admin.py`).

## How auth works

JWT access + refresh tokens are stored in `localStorage` after login. Every
API request attaches the access token; a 401 response triggers an automatic
refresh-and-retry via an Axios interceptor (`lib/api.ts`). If the refresh
token itself is invalid or expired, the user is redirected to `/login`.

## Verified in this environment

This sandbox has no network access, so `npm install` / `next build` couldn't
be run here. Instead, every `.ts`/`.tsx` file was run through the TypeScript
compiler in syntax + undefined-reference check mode (`tsc --noEmit`) with no
errors — confirming the code is structurally sound. Run `npm run build`
yourself as a final check before deploying; that will also catch anything
that depends on the actual `next`/`react` type packages, which aren't
installed in this sandbox.

## What's next

Phase 5 (Android SMS Reader app) is the one remaining piece of the original
spec. After that, the system is feature-complete and we can move to launch:
environment hardening, deployment, and a go-live checklist.
