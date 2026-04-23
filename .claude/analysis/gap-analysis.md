# Gap Analysis — Prioritised Build List

Based on the spec's own priority tiers (P0 → P3) cross-referenced with what's currently built.

---

## P0 — Must for Beta

These are blockers. Nothing else works correctly without them.

### 1. Auth overhaul (JWT + password hashing + email verification)

**What exists:** Email + optional password login, localStorage session object, no token.

**What's needed:**
- Password hashing with bcrypt on register
- JWT access + refresh token issuance on login
- `Authorization: Bearer <token>` header on all protected endpoints
- `POST /auth/verify-email` + email verification step post-signup
- `POST /auth/forgot-password` + `POST /auth/reset-password`
- Frontend: store JWT in `httpOnly` cookie or secure storage (not plain localStorage)

**Files to change:**
- `app/routers/auth.py` — add hashing, JWT logic
- `app/models.py` — User model needs `password_hash`, `email_verified`
- `frontend/lib/session.ts` — swap to token-based session
- All router files — add `Depends(get_current_user)` guard

---

### 2. User / WorkspaceMember split

**What exists:** A single `Member` table that conflates the user account with workspace membership. Role is a plain string.

**What's needed:**
- New `User` table: id, full_name, email, phone, password_hash, email_verified, created_at
- Rename `Member` → `WorkspaceMember`: workspace_id, user_id (FK), role_id (FK), is_general_member, dues_status, level, status, joined_at
- Migrate existing Member rows

**Why it matters:** Without this split, a person can't belong to multiple workspaces, and ownership transfer is impossible.

---

### 3. Role system

**What exists:** role is a string field ("member", "admin", etc.) — no permissions.

**What's needed:**
- `Role` table: id, workspace_id, name, is_system_role, permissions (JSONB), created_at
- Seed two system roles on workspace creation: Owner + Secretary
- Permission matrix enforcement on every protected endpoint
- `GET/POST /workspaces/{id}/roles`
- `PATCH/DELETE /workspaces/{id}/roles/{role_id}`
- Frontend: Settings → Roles & Permissions page

---

### 4. Invitation system

**What exists:** Members can be directly created via `POST /workspaces/{id}/members` (no email, no token).

**What's needed:**
- `Invitation` table: id, workspace_id, email, role_id, invited_by, token, expires_at, accepted_at
- `POST /workspaces/{id}/members/invite` — send invite email with unique token (72h expiry)
- `POST /invitations/{token}/accept` — validate token, create User + WorkspaceMember
- `DELETE /invitations/{token}` — revoke
- `POST /invitations/{token}/resend` — resend email
- Bulk invite link: generate a reusable link tied to a default role, revocable
- Frontend: `/invite/[token]` acceptance screen
- Frontend: Members page invite panel (by email + by link tabs)
- Email sending via SendGrid/Resend

---

### 5. Dashboard — missing widgets

**What exists:** Metric cards, events/campaigns/links lists, setup checklist.

**What's missing on the dashboard:**
- My tasks widget (blocked by tasks module)
- Pinned announcements (blocked by announcements module)
- Recent activity feed (last 10 actions: payments, joins, events, tasks)
- Dues alert banner (deadline approaching, defaulter count)

These can be partially added once dependent modules exist.

---

## P1 — High Priority

### 6. Dues payments + Paystack webhook

**What exists:** DuesCycle list + create. No payment initiation, no payment records.

**What's needed:**
- `DuesPayment` table (see data-models.md)
- Add `breakdown` (JSONB) and `applicable_levels` to DuesCycle
- `POST /workspaces/{id}/dues-cycles/{cycle_id}/pay` — initiate Paystack checkout, return payment URL
- `POST /webhooks/paystack` — verify signature, match `gateway_ref`, update DuesPayment status to paid, update member dues_status, trigger notification
- Manual fallback: `POST .../receipt-upload`, review queue endpoints
- Frontend: dues detail page with defaulter list, payment ledger, receipt review queue
- Frontend: Settings → Integrations → Paystack connection

---

### 7. Events — detail, RSVP, attendance

**What exists:** Events list + create form.

**What's needed:**
- `EventAttendee` table
- `GET /workspaces/{id}/events/{event_id}` — detail
- `PATCH/DELETE` for events
- `POST .../rsvp` + `DELETE .../rsvp`
- `GET .../attendees`
- `POST .../check-in/{member_id}` — manual check-in
- `GET /workspaces/{id}/events/analytics` — bar chart data
- Public RSVP: `POST /public/e/{slug}/rsvp`
- Add `thumbnail_url`, `external_link`, `tags`, `created_by` to Event model
- Frontend: event detail page, RSVP list, attendance tracker, QR check-in

---

### 8. Fundraising — full campaign flow

**What exists:** Campaign list + basic create. No funding streams, no contributions, no checkout.

**What's needed:**
- `FundingStream` + `Contribution` tables
- Add `deadline`, `cover_url`, `description`, `linked_budget_id` to Campaign
- `POST .../streams` — add funding stream
- `POST /public/donate/{slug}/pay` — initiate donation checkout
- `POST /webhooks/paystack` (shared handler) — match contribution by ref, update raised_amount
- `GET .../contributions` — contributor ledger
- `POST .../sponsorships` — manual sponsorship logger
- Frontend: create campaign form with funding streams, campaign dashboard, public donation page with Paystack embedded checkout

---

### 9. Meetings module + Claude transcript processing

**What exists:** Nothing.

**What's needed:**
- `Meeting`, `MeetingMinutes`, `ActionItem` tables
- Full CRUD: `GET/POST /workspaces/{id}/meetings`, `GET/PATCH/DELETE .../meetings/{id}`
- `POST .../transcript` — manual upload/paste
- Background job: send transcript to Claude API → parse JSON → create MeetingMinutes record + Task records (with fuzzy name matching against workspace members)
- `POST .../minutes/publish`
- Claude integration: `POST /api/ai/process-transcript`
- Frontend: meetings list, create form + agenda builder, minutes draft review, published minutes page, transcript upload modal

---

### 10. Tasks module

**What exists:** Nothing.

**What's needed:**
- `Task` table
- `GET/POST /workspaces/{id}/tasks`
- `GET/PATCH/DELETE .../tasks/{task_id}`
- `GET /workspaces/{id}/tasks/my` — personal task list for current user
- Auto-creation from ActionItems (meeting flow)
- Overdue detection background job + notifications
- Frontend: kanban board (drag-to-update), list view, task detail + comments, my tasks view

---

## P2 — Medium Priority

### 11. Meetings integrations (Google Meet, Fireflies, Zoom)

**What's needed:**
- `Integration` table
- Google OAuth flow: connect, store access/refresh token, watch Drive folder
- `POST /webhooks/google-drive` — detect new transcript file, queue Claude job
- Fireflies: API key connect, register webhook, `POST /webhooks/fireflies` handler
- Zoom OAuth: connect, `POST /webhooks/zoom` handler
- Frontend: Settings → Integrations page with per-provider connect/disconnect UI

---

### 12. Budget Planner

**What's needed:**
- `Budget` + `BudgetLine` tables
- Full CRUD: `GET/POST /workspaces/{id}/budgets`, line items, expenditure logger
- PDF export endpoint
- Frontend: budget list, create form, detail table (planned vs actual, variance colour-coding), expenditure logger

---

### 13. Announcements

**What's needed:**
- `Announcement` table
- `GET/POST /workspaces/{id}/announcements`
- `PATCH .../announcements/{id}` — pin, archive
- Scheduled publish: background job checks `publish_at` and dispatches
- Target audience filtering (all / by level / admin / role-specific)
- `POST /api/ai/draft-announcement` — Claude-assisted drafting
- Frontend: announcement feed, create form with rich text + audience picker, pin/archive actions

---

### 14. Settings page (full)

**What's needed:**
- `PATCH /workspaces/{id}` — update name, slug, logo, brand colour, tagline, body_type, university
- Logo upload (file storage: S3 / Cloudflare R2)
- Frontend: Settings layout with 6 sections: Workspace / Roles / Members / Integrations / Notifications / Billing

---

### 15. Notifications system

**What's needed:**
- `Notification` table
- `GET /workspaces/{id}/notifications` — in-app feed
- `PATCH .../notifications/{id}/read` + read-all
- Email dispatch via SendGrid/Resend triggered by: payment confirmed, task assigned, meeting minutes published, campaign milestone, dues deadline approaching, member joined
- Notification preference toggles (in Settings)

---

### 16. Ownership & role transfer

**What's needed:**
- `POST /workspaces/{id}/transfer-ownership` — password re-entry, email confirmation to new owner
- `POST /workspaces/{id}/members/{id}/transfer-role` — reassign open tasks, update role
- Frontend: Settings → Workspace → Transfer ownership flow, Members → Transfer role modal

---

## P3 — Later

### 17. AI analytics narrative
- `POST /api/ai/generate-report` — aggregate workspace stats → Claude → narrative paragraph
- Display in dashboard analytics section

### 18. Portal page customisation
- Logo, brand colour, tagline, section visibility toggles
- These fields already listed in Workspace model gaps above

### 19. Zoom integration
- Lower priority per spec (less common in Nigerian context)
- Same pattern as Google Meet/Fireflies once those are done

### 20. Billing & plan management
- Plan table / Stripe or Paystack subscription
- View/upgrade plan, payment history, AI credit balance
- Accessible only to workspace owner

---

## Critical Architecture Changes Required

These are structural changes that should happen **before** building any P1+ features, to avoid painful rewrites:

| Change | Why | Impact |
|--------|-----|--------|
| Split `Member` → `User` + `WorkspaceMember` | Multi-workspace support, ownership transfer, proper auth | High — touches every endpoint |
| Add JWT auth middleware | Protect all workspace endpoints properly | High — replace localStorage session |
| Add `Role` table with permissions JSONB | Permission-gated endpoints throughout | High — required for all admin actions |
| Switch `starts_at` (Event) to datetime | Sorting, filtering, deadline logic | Medium |
| Add `password_hash` + bcrypt | Security baseline | High — auth is currently insecure |

---

## What's in Good Shape

These parts of the current build are solid foundations:

- FastAPI project structure (routers, schemas, models pattern)
- Next.js App Router layout + public/protected route groups
- `WorkspaceOverview` endpoint design (single call for dashboard)
- Public endpoints pattern (`/public/...`) — clean separation
- Short link click tracking (`GET /public/r/{slug}`)
- Multi-step register form UX
- `lib/api.ts` wrapper (just needs auth header injection)
