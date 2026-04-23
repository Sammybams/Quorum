# API Endpoints — Built vs Spec

Legend: ✅ Built | ⚠️ Partial | ❌ Missing

---

## Current Backend Base: `/api/v1`
## Spec Base: `/api` (to be aligned)

---

## Authentication `/api/auth`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| POST | `/auth/register` | ✅ | Creates workspace + admin member |
| POST | `/auth/login` | ✅ | Email-based, workspace_slug optional |
| POST | `/auth/logout` | ❌ | No session invalidation |
| POST | `/auth/forgot-password` | ❌ | Spec requires password reset flow |
| POST | `/auth/reset-password` | ❌ | Token-based reset |
| POST | `/auth/verify-email` | ❌ | Email verification on signup |
| POST | `/auth/refresh-token` | ❌ | JWT refresh (no JWT in current build) |
| GET  | `/auth/oauth/google/callback` | ❌ | Google OAuth for Meet integration |
| GET  | `/auth/oauth/zoom/callback` | ❌ | Zoom OAuth |

**Current auth issues vs spec:**
- No JWT — session stored in localStorage as plain object, no token
- No password hashing visible in current code
- No email verification step
- Password is optional in current login (spec requires it)

---

## Workspaces `/api/workspaces`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| POST | `/workspaces` | ✅ | |
| GET  | `/workspaces` | ✅ | Lists all (no auth filter) |
| GET  | `/workspaces/{id}` | ✅ | |
| GET  | `/workspaces/slug/{slug}` | ✅ | |
| PATCH | `/workspaces/{id}` | ❌ | Update workspace settings |
| GET  | `/workspaces/slug/{slug}/overview` | ✅ | Dashboard overview |
| POST | `/workspaces/{id}/invite-link` | ❌ | Generate bulk invite link |
| DELETE | `/workspaces/{id}/invite-link` | ❌ | Revoke invite link |
| POST | `/workspaces/{id}/transfer-ownership` | ❌ | Transfer to new owner |

---

## Members `/api/members`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/members` | ✅ | List only |
| POST | `/workspaces/{id}/members` | ✅ | Direct create (no invite flow) |
| GET  | `/workspaces/{id}/members/{member_id}` | ❌ | Member profile |
| PATCH | `/workspaces/{id}/members/{member_id}` | ❌ | Update role, level, etc. |
| DELETE | `/workspaces/{id}/members/{member_id}` | ❌ | Remove from workspace |
| POST | `/workspaces/{id}/members/invite` | ❌ | Email invite with token |
| POST | `/workspaces/{id}/members/{id}/transfer-role` | ❌ | Role transfer flow |
| POST | `/invitations/{token}/accept` | ❌ | Accept email invitation |
| DELETE | `/invitations/{token}` | ❌ | Revoke invitation |
| POST | `/invitations/{token}/resend` | ❌ | Resend invite email |

---

## Roles `/api/roles`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/roles` | ❌ | List all roles + permissions |
| POST | `/workspaces/{id}/roles` | ❌ | Create custom role |
| PATCH | `/workspaces/{id}/roles/{role_id}` | ❌ | Edit name + permissions |
| DELETE | `/workspaces/{id}/roles/{role_id}` | ❌ | Delete custom role (if no holders) |

**Note:** Current `Member` model stores role as a plain string field. Spec requires a separate `Role` table with a JSONB permissions map.

---

## Dues `/api/dues`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/dues-cycles` | ✅ | List only |
| POST | `/workspaces/{id}/dues-cycles` | ✅ | Create cycle |
| GET  | `/workspaces/{id}/dues-cycles/{cycle_id}` | ❌ | Cycle detail + defaulter list |
| PATCH | `/workspaces/{id}/dues-cycles/{cycle_id}` | ❌ | Update cycle |
| POST | `/workspaces/{id}/dues-cycles/{cycle_id}/pay` | ❌ | Initiate Paystack/Flutterwave checkout |
| GET  | `/workspaces/{id}/dues-cycles/{cycle_id}/payments` | ❌ | Payment ledger |
| GET  | `/workspaces/{id}/dues-cycles/{cycle_id}/defaulters` | ❌ | Defaulter list |
| POST | `/workspaces/{id}/dues-cycles/{cycle_id}/payments/{id}/confirm` | ❌ | Confirm manual payment |
| POST | `/workspaces/{id}/dues-cycles/{cycle_id}/payments/{id}/reject` | ❌ | Reject manual payment |
| POST | `/workspaces/{id}/dues-cycles/{cycle_id}/receipt-upload` | ❌ | Manual receipt upload |

---

## Events `/api/events`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/events` | ✅ | List only |
| POST | `/workspaces/{id}/events` | ✅ | Create |
| GET  | `/workspaces/{id}/events/{event_id}` | ❌ | Event detail |
| PATCH | `/workspaces/{id}/events/{event_id}` | ❌ | Edit |
| DELETE | `/workspaces/{id}/events/{event_id}` | ❌ | Delete |
| POST | `/workspaces/{id}/events/{event_id}/rsvp` | ❌ | Member RSVP |
| DELETE | `/workspaces/{id}/events/{event_id}/rsvp` | ❌ | Cancel RSVP |
| GET  | `/workspaces/{id}/events/{event_id}/attendees` | ❌ | RSVP + attendance list |
| POST | `/workspaces/{id}/events/{event_id}/check-in/{member_id}` | ❌ | Mark attendance |
| GET  | `/workspaces/{id}/events/analytics` | ❌ | Attendance analytics |

---

## Meetings `/api/meetings`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/meetings` | ❌ | All meetings absent |
| POST | `/workspaces/{id}/meetings` | ❌ | |
| GET  | `/workspaces/{id}/meetings/{meeting_id}` | ❌ | |
| PATCH | `/workspaces/{id}/meetings/{meeting_id}` | ❌ | |
| DELETE | `/workspaces/{id}/meetings/{meeting_id}` | ❌ | |
| POST | `/workspaces/{id}/meetings/{meeting_id}/transcript` | ❌ | Manual transcript upload |
| GET  | `/workspaces/{id}/meetings/{meeting_id}/minutes` | ❌ | |
| POST | `/workspaces/{id}/meetings/{meeting_id}/minutes/publish` | ❌ | |
| GET  | `/workspaces/{id}/meetings/{meeting_id}/action-items` | ❌ | |

---

## Fundraising Campaigns `/api/campaigns`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/campaigns` | ✅ | List only |
| POST | `/workspaces/{id}/campaigns` | ✅ | Create (no funding streams, no cover) |
| GET  | `/workspaces/{id}/campaigns/{campaign_id}` | ❌ | Campaign detail |
| PATCH | `/workspaces/{id}/campaigns/{campaign_id}` | ❌ | Edit |
| POST | `/workspaces/{id}/campaigns/{campaign_id}/streams` | ❌ | Add funding stream |
| POST | `/workspaces/{id}/campaigns/{campaign_id}/sponsorships` | ❌ | Log sponsorship |
| GET  | `/workspaces/{id}/campaigns/{campaign_id}/contributions` | ❌ | Contributor ledger |
| POST | `/workspaces/{id}/campaigns/{campaign_id}/donate` | ❌ | Initiate public donation |
| PATCH | `/workspaces/{id}/campaigns/{campaign_id}/status` | ❌ | Close campaign |

---

## Budget Planner `/api/budgets`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/budgets` | ❌ | Entire module absent |
| POST | `/workspaces/{id}/budgets` | ❌ | |
| GET  | `/workspaces/{id}/budgets/{budget_id}` | ❌ | |
| PATCH | `/workspaces/{id}/budgets/{budget_id}` | ❌ | |
| POST | `/workspaces/{id}/budgets/{budget_id}/lines` | ❌ | Add line item |
| PATCH | `/workspaces/{id}/budgets/{budget_id}/lines/{line_id}` | ❌ | Log actual spend |
| GET  | `/workspaces/{id}/budgets/{budget_id}/export` | ❌ | PDF export |

---

## Tasks `/api/tasks`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/tasks` | ❌ | Entire module absent |
| POST | `/workspaces/{id}/tasks` | ❌ | |
| GET  | `/workspaces/{id}/tasks/{task_id}` | ❌ | |
| PATCH | `/workspaces/{id}/tasks/{task_id}` | ❌ | Update status |
| DELETE | `/workspaces/{id}/tasks/{task_id}` | ❌ | |
| GET  | `/workspaces/{id}/tasks/my` | ❌ | Tasks for current user |

---

## Announcements `/api/announcements`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/announcements` | ❌ | Entire module absent |
| POST | `/workspaces/{id}/announcements` | ❌ | |
| GET  | `/workspaces/{id}/announcements/{id}` | ❌ | |
| PATCH | `/workspaces/{id}/announcements/{id}` | ❌ | Pin/unpin/archive |
| DELETE | `/workspaces/{id}/announcements/{id}` | ❌ | |

---

## Short Links `/api/links`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/links` | ✅ | |
| POST | `/workspaces/{id}/links` | ✅ | |
| PATCH | `/workspaces/{id}/links/{link_id}` | ❌ | Toggle active, update URL |
| DELETE | `/workspaces/{id}/links/{link_id}` | ❌ | |

---

## Integrations `/api/integrations`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/integrations` | ❌ | Entire domain absent |
| POST | `/workspaces/{id}/integrations/paystack` | ❌ | Connect Paystack |
| DELETE | `/workspaces/{id}/integrations/paystack` | ❌ | Disconnect |
| POST | `/workspaces/{id}/integrations/flutterwave` | ❌ | Connect Flutterwave |
| GET  | `/integrations/google/connect` | ❌ | Start Google OAuth |
| GET  | `/integrations/zoom/connect` | ❌ | Start Zoom OAuth |
| POST | `/workspaces/{id}/integrations/fireflies` | ❌ | Connect Fireflies by API key |
| DELETE | `/workspaces/{id}/integrations/{provider}` | ❌ | Disconnect any provider |

---

## Webhooks `/api/webhooks`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| POST | `/webhooks/paystack` | ❌ | Entire domain absent |
| POST | `/webhooks/flutterwave` | ❌ | |
| POST | `/webhooks/fireflies` | ❌ | |
| POST | `/webhooks/zoom` | ❌ | |
| POST | `/webhooks/google-drive` | ❌ | |

---

## AI `/api/ai`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| POST | `/ai/process-transcript` | ❌ | Entire domain absent |
| POST | `/ai/generate-report` | ❌ | Analytics narrative |
| POST | `/ai/draft-announcement` | ❌ | Announcement drafting |

---

## Notifications `/api/notifications`

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/workspaces/{id}/notifications` | ❌ | Entire domain absent |
| PATCH | `/workspaces/{id}/notifications/{id}/read` | ❌ | |
| PATCH | `/workspaces/{id}/notifications/read-all` | ❌ | |

---

## Public Endpoints `/public` (No Auth)

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/public/e/{event_slug}` | ✅ | Public event view |
| GET  | `/public/donate/{campaign_slug}` | ✅ | Public campaign page |
| GET  | `/public/portal/{workspace_slug}` | ✅ | Public portal |
| GET  | `/public/r/{slug}` | ✅ | Short link redirect (increments click_count) |
| POST | `/public/e/{event_slug}/rsvp` | ❌ | Public RSVP (no-login) |
| POST | `/public/donate/{campaign_slug}/pay` | ❌ | Initiate donation checkout |

---

## Health

| Method | Path | Built | Notes |
|--------|------|-------|-------|
| GET  | `/health` | ✅ | |

---

## Summary Count

| Status | Count |
|--------|-------|
| ✅ Built | 18 |
| ❌ Missing | ~70+ |

The current build covers roughly **20% of the spec's required endpoints**.
