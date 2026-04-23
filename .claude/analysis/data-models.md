# Data Models — Current ORM vs Spec Schema

Legend: ✅ Exists | ⚠️ Partial (missing fields) | ❌ Missing

---

## Workspace

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ✅ | int PK |
| name | ✅ | ✅ | |
| slug | ✅ | ✅ | unique, indexed |
| description | — | ✅ | extra field in current |
| logo_url | ✅ | ❌ | needed for portal + emails |
| brand_color | ✅ | ❌ | portal customisation |
| body_type | ✅ | ❌ | dept body / faculty / union / club |
| university | ✅ | ❌ | |
| department | ✅ | ❌ | |
| portal_tagline | ✅ | ❌ | public portal one-liner |
| owner_id | ✅ | ❌ | FK to User; critical for ownership transfer |
| plan | ✅ | ❌ | free / growth / pro |
| created_at | ✅ | ✅ | |

**Status: ⚠️ Partial — 7 fields missing**

---

## User (separate from Member)

The spec distinguishes between a **User** (account) and a **WorkspaceMember** (membership within a workspace). The current build collapses both into a single `Member` table, which won't support multi-workspace membership or proper ownership transfer.

### Spec: User table
| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ (merged into Member) | |
| full_name | ✅ | ✅ (on Member) | |
| email | ✅ | ✅ (on Member) | |
| phone | ✅ | ❌ | |
| password_hash | ✅ | ❌ | no hashing in current build |
| email_verified | ✅ | ❌ | |
| created_at | ✅ | ✅ (on Member) | |

**Status: ❌ Missing — User model needs to be split from Member**

---

## WorkspaceMember (membership join table)

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | — | |
| workspace_id | ✅ | ✅ (on Member) | |
| user_id | ✅ | ❌ | FK to User |
| role_id | ✅ | ❌ | FK to Role table; currently a string |
| is_general_member | ✅ | ❌ | admin vs general member flag |
| joined_at | ✅ | ✅ (created_at on Member) | |
| status | ✅ | ❌ | active / pending |
| dues_status | — | ✅ | currently on Member, fine to keep here |
| level | — | ✅ | year/level, fine to keep here |

**Status: ❌ Needs refactor — Member should become WorkspaceMember with User FK**

---

## Role

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| name | ✅ | ❌ | currently stored as string on Member |
| is_system_role | ✅ | ❌ | locks owner/secretary from deletion |
| permissions | ✅ | ❌ | JSONB — the permission matrix |
| created_at | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## Invitation

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| email | ✅ | ❌ | |
| role_id | ✅ | ❌ | |
| invited_by | ✅ | ❌ | FK to User |
| token | ✅ | ❌ | unique time-limited invite token |
| expires_at | ✅ | ❌ | 72h from creation |
| accepted_at | ✅ | ❌ | null until accepted |
| is_bulk_link | — | ❌ | to distinguish email vs link invite |

**Status: ❌ Missing entirely**

---

## DuesCycle

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ✅ | |
| workspace_id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| amount | ✅ | ✅ | |
| breakdown | ✅ | ❌ | JSONB: [{label, amount}] line items |
| deadline | ✅ | ✅ | string — could be datetime |
| applicable_levels | ✅ | ❌ | array: all / 100L / 200L etc. |
| created_at | ✅ | ✅ | |

**Status: ⚠️ Partial — 2 fields missing**

---

## DuesPayment

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| cycle_id | ✅ | ❌ | FK to DuesCycle |
| member_id | ✅ | ❌ | FK to WorkspaceMember |
| amount | ✅ | ❌ | |
| method | ✅ | ❌ | gateway / manual |
| gateway_ref | ✅ | ❌ | Paystack/Flutterwave reference |
| receipt_url | ✅ | ❌ | manual upload fallback |
| status | ✅ | ❌ | pending / paid / rejected |
| confirmed_by | ✅ | ❌ | FK to User |
| confirmed_at | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## Event

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ✅ | |
| workspace_id | ✅ | ✅ | |
| title | ✅ | ✅ | |
| slug | ✅ | ✅ | unique |
| event_type | ✅ | ✅ | |
| starts_at | ✅ | ✅ | string — should be datetime |
| venue | ✅ | ✅ | |
| description | ✅ | ✅ | |
| thumbnail_url | ✅ | ❌ | for public event page OG preview |
| rsvp_enabled | ✅ | ✅ | |
| capacity | ✅ | ✅ | |
| rsvp_count | — | ✅ | computed, fine as denorm counter |
| external_link | ✅ | ❌ | optional external URL |
| tags | ✅ | ❌ | array |
| created_by | ✅ | ❌ | FK to User |
| created_at | ✅ | ✅ | |

**Status: ⚠️ Partial — 4 fields missing**

---

## EventAttendee

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| event_id | ✅ | ❌ | |
| member_id | ✅ | ❌ | |
| rsvp_at | ✅ | ❌ | |
| checked_in_at | ✅ | ❌ | null until physically checked in |

**Status: ❌ Missing entirely**

---

## Meeting

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| title | ✅ | ❌ | |
| type | ✅ | ❌ | general / AGM / emergency / exco |
| date | ✅ | ❌ | |
| venue | ✅ | ❌ | |
| virtual_link | ✅ | ❌ | Google Meet / Zoom URL |
| agenda | ✅ | ❌ | JSONB: ordered agenda items |
| quorum_threshold | ✅ | ❌ | min attendees for valid meeting |
| slug | ✅ | ❌ | for shareable invite page |
| transcript_source | ✅ | ❌ | google / fireflies / zoom / manual |
| status | — | ❌ | draft / scheduled / completed |

**Status: ❌ Missing entirely**

---

## MeetingMinutes

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| meeting_id | ✅ | ❌ | |
| content | ✅ | ❌ | structured text from Claude |
| summary | ✅ | ❌ | 2–3 sentence Claude summary |
| published_at | ✅ | ❌ | null until published |
| published_by | ✅ | ❌ | FK to User |

**Status: ❌ Missing entirely**

---

## ActionItem

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| meeting_id | ✅ | ❌ | |
| description | ✅ | ❌ | |
| assigned_to_member_id | ✅ | ❌ | fuzzy-matched from Claude output |
| due_date | ✅ | ❌ | extracted from transcript |
| status | ✅ | ❌ | open / done |

**Status: ❌ Missing entirely**

---

## Task

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| title | ✅ | ❌ | |
| description | ✅ | ❌ | |
| assigned_to | ✅ | ❌ | FK to WorkspaceMember |
| created_by | ✅ | ❌ | FK to User |
| due_date | ✅ | ❌ | |
| priority | ✅ | ❌ | low / medium / high |
| status | ✅ | ❌ | todo / in_progress / done |
| linked_module | ✅ | ❌ | event / meeting / campaign |
| linked_id | ✅ | ❌ | ID of linked record |

**Status: ❌ Missing entirely**

---

## Campaign

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ✅ | |
| workspace_id | ✅ | ✅ | |
| name | ✅ | ✅ | |
| slug | ✅ | ✅ | unique |
| target_amount | ✅ | ✅ | |
| raised_amount | ✅ | ✅ | denorm counter |
| deadline | ✅ | ❌ | |
| cover_url | ✅ | ❌ | campaign thumbnail |
| description | ✅ | ❌ | |
| linked_budget_id | ✅ | ❌ | FK to Budget |
| status | ✅ | ✅ | active / closed / draft |
| created_at | ✅ | ✅ | |

**Status: ⚠️ Partial — 4 fields missing**

---

## FundingStream

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| campaign_id | ✅ | ❌ | |
| type | ✅ | ❌ | sponsorship / donation / ticket / dues_levy / manual |
| name | ✅ | ❌ | |
| target_amount | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## Contribution

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| stream_id | ✅ | ❌ | FK to FundingStream |
| contributor_name | ✅ | ❌ | or "Anonymous" |
| amount | ✅ | ❌ | |
| method | ✅ | ❌ | gateway / manual |
| gateway_ref | ✅ | ❌ | Paystack/Flutterwave ref |
| is_anonymous | ✅ | ❌ | |
| confirmed_at | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## Budget

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| program_name | ✅ | ❌ | |
| created_by | ✅ | ❌ | FK to User |

**Status: ❌ Missing entirely**

---

## BudgetLine

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| budget_id | ✅ | ❌ | |
| category | ✅ | ❌ | |
| description | ✅ | ❌ | |
| planned_amount | ✅ | ❌ | |
| actual_amount | ✅ | ❌ | logged after spend |
| receipt_url | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## ShortLink

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ✅ | |
| workspace_id | ✅ | ✅ | |
| slug | ✅ | ✅ | unique |
| destination_url | ✅ | ✅ | |
| expires_at | ✅ | ❌ | optional expiry |
| click_count | ✅ | ✅ | |
| is_active | ✅ | ✅ | |
| created_at | ✅ | ✅ | |

**Status: ⚠️ Partial — expires_at missing**

---

## Announcement

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| title | ✅ | ❌ | |
| body | ✅ | ❌ | rich text |
| attachment_url | ✅ | ❌ | PDF or image |
| target_type | ✅ | ❌ | all / by_level / admin_only / role_specific |
| target_value | ✅ | ❌ | e.g. "100L" or role_id |
| is_pinned | ✅ | ❌ | |
| publish_at | ✅ | ❌ | null = immediate |
| archived_at | ✅ | ❌ | null = active |

**Status: ❌ Missing entirely**

---

## Integration

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| provider | ✅ | ❌ | google / fireflies / zoom / paystack / flutterwave |
| access_token | ✅ | ❌ | encrypted at rest |
| refresh_token | ✅ | ❌ | |
| config | ✅ | ❌ | JSONB: API keys, watched folder ID, webhook IDs |
| connected_at | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## Notification

| Field | Spec | Current | Notes |
|-------|------|---------|-------|
| id | ✅ | ❌ | Entire table missing |
| workspace_id | ✅ | ❌ | |
| user_id | ✅ | ❌ | FK to User |
| type | ✅ | ❌ | payment_confirmed / task_assigned / etc. |
| title | ✅ | ❌ | |
| body | ✅ | ❌ | |
| read_at | ✅ | ❌ | null = unread |
| created_at | ✅ | ❌ | |

**Status: ❌ Missing entirely**

---

## Model Summary

| Model | Status | Missing Fields |
|-------|--------|----------------|
| Workspace | ⚠️ Partial | logo_url, brand_color, body_type, university, department, portal_tagline, owner_id, plan |
| User | ❌ Missing | Split from Member; needs phone, password_hash, email_verified |
| WorkspaceMember | ⚠️ Partial | Needs user_id FK, role_id FK, is_general_member, status |
| Role | ❌ Missing | Entire table |
| Invitation | ❌ Missing | Entire table |
| DuesCycle | ⚠️ Partial | breakdown (JSONB), applicable_levels |
| DuesPayment | ❌ Missing | Entire table |
| Event | ⚠️ Partial | thumbnail_url, external_link, tags, created_by |
| EventAttendee | ❌ Missing | Entire table |
| Meeting | ❌ Missing | Entire table |
| MeetingMinutes | ❌ Missing | Entire table |
| ActionItem | ❌ Missing | Entire table |
| Task | ❌ Missing | Entire table |
| Campaign | ⚠️ Partial | deadline, cover_url, description, linked_budget_id |
| FundingStream | ❌ Missing | Entire table |
| Contribution | ❌ Missing | Entire table |
| Budget | ❌ Missing | Entire table |
| BudgetLine | ❌ Missing | Entire table |
| ShortLink | ⚠️ Partial | expires_at |
| Announcement | ❌ Missing | Entire table |
| Integration | ❌ Missing | Entire table |
| Notification | ❌ Missing | Entire table |

**6 of 22 models exist (partially). 16 are entirely absent.**
