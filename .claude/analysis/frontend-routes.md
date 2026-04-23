# Frontend Routes & Pages — Built vs Spec

Legend: ✅ Built | ⚠️ Partial | ❌ Missing

---

## Route Map

```
/
├── login                              ✅ Login screen
├── register                           ⚠️ 3-step signup (missing email verification step)
├── forgot-password                    ❌ Forgot password screen
├── reset-password/[token]             ❌ Password reset (token from email)
├── invite/[token]                     ❌ Invite acceptance screen
│
├── e/[eventSlug]                      ✅ Public event page (no login)
├── donate/[campaignSlug]              ⚠️ Public donation page (view only, no checkout)
├── portal/[workspaceSlug]             ⚠️ Public portal (no logo/brand/announcements)
├── r/[slug]                           ✅ Short link redirect
│
└── [workspaceSlug]/
    ├── dashboard                      ⚠️ Overview metrics (missing tasks, announcements, activity feed)
    ├── members                        ⚠️ Member list (no invite panel, no profile modal, no filters)
    │   └── [memberId]                 ❌ Member profile page
    ├── events                         ⚠️ Event list only
    │   ├── new                        ⚠️ Create form (no thumbnail upload, no tags)
    │   └── [eventSlug]                ❌ Event detail + RSVP list + attendance tracker
    ├── dues                           ⚠️ Dues cycle list only
    │   ├── new                        ❌ Create dues cycle form
    │   └── [cycleId]                  ❌ Cycle detail (defaulter list, payment history, receipt queue)
    ├── meetings                       ❌ Entire module missing
    │   ├── new                        ❌
    │   └── [meetingId]                ❌
    │       └── minutes                ❌
    ├── campaigns                      ⚠️ Campaign list only
    │   ├── new                        ❌ Create campaign form (funding streams, cover image)
    │   └── [campaignId]               ❌ Campaign dashboard (contributions, stream breakdown)
    ├── budgets                        ❌ Entire module missing
    │   ├── new                        ❌
    │   └── [budgetId]                 ❌
    ├── tasks                          ❌ Entire module missing (kanban + list view)
    ├── announcements                  ❌ Entire module missing
    ├── links                          ⚠️ Link list only (no analytics, no QR download)
    └── settings                       ❌ Entire settings page missing
        ├── workspace                  ❌
        ├── roles                      ❌
        ├── members                    ❌
        ├── integrations               ❌
        ├── notifications              ❌
        └── billing                    ❌
```

---

## Page-by-Page Detail

### Auth Screens

| Screen | Route | Status | What's there | What's missing |
|--------|-------|--------|-------------|----------------|
| Login | `/login` | ✅ | workspace_slug, email, password fields | Forgot password link |
| Register step 1 | `/register` | ✅ | Org name, university, body type, faculty, slug | |
| Register step 2 | `/register` | ✅ | Name, email, phone, role title, password | |
| Register step 3 | `/register` | ⚠️ | Success screen | No email verification prompt |
| Forgot password | `/forgot-password` | ❌ | — | Entire screen |
| Password reset | `/reset-password/[token]` | ❌ | — | Entire screen |
| Invite acceptance | `/invite/[token]` | ❌ | — | Pre-filled form: name, password; shows body + role |
| Email verification | — | ❌ | — | Post-signup verification step |

---

### Dashboard `/[workspaceSlug]/dashboard`

| Component | Status | Notes |
|-----------|--------|-------|
| Total members card | ✅ | |
| Dues paid % card | ✅ | |
| Events this semester card | ✅ | |
| Active campaign progress card | ✅ | |
| Upcoming events widget | ✅ | Shows next 3 |
| Active campaign widget | ✅ | Progress bar, amount |
| Dues cycles list | ✅ | |
| Short links list | ✅ | |
| Setup checklist (first login) | ✅ | |
| My tasks widget | ❌ | Requires tasks module |
| Pinned announcements | ❌ | Requires announcements module |
| Recent activity feed | ❌ | Last 10 actions across workspace |
| Dues alert banner | ❌ | Deadline approaching / defaulters exist |
| AI analytics narrative | ❌ | Claude-generated paragraph |

---

### Members `/[workspaceSlug]/members`

| Component | Status | Notes |
|-----------|--------|-------|
| Member table (name, role, level, dues status) | ✅ | |
| Invite by email panel | ❌ | Needs invite token flow |
| Invite by link panel | ❌ | Generate/revoke bulk link |
| Member profile modal | ❌ | Dues history, task assignments, contact |
| Filter by role / level / dues status | ❌ | |
| Search by name / email | ❌ | |
| Bulk select → export CSV / announce | ❌ | |
| Pending invitations list | ❌ | |

---

### Events `/[workspaceSlug]/events`

| Component | Status | Notes |
|-----------|--------|-------|
| Events list (cards/table) | ✅ | |
| Filter by type / status | ❌ | |
| Create event form | ⚠️ | Missing: thumbnail upload, tags, external link |
| Event detail page | ❌ | |
| RSVP list | ❌ | |
| Attendance tracker (check-in) | ❌ | |
| Events analytics (bar chart, donut) | ❌ | |
| Shareable link + QR code download | ❌ | |
| Public event page | ✅ | `/e/[eventSlug]` |

---

### Dues `/[workspaceSlug]/dues`

| Component | Status | Notes |
|-----------|--------|-------|
| Dues cycle list | ✅ | |
| Metric cards (collected, outstanding, rate) | ❌ | |
| Create cycle form (with breakdown line items) | ❌ | Current list page has no create form |
| Defaulter list (filterable, export CSV) | ❌ | |
| Payment ledger | ❌ | |
| Manual receipt review queue | ❌ | |

---

### Meetings `/[workspaceSlug]/meetings`

| Component | Status | Notes |
|-----------|--------|-------|
| Meetings list | ❌ | Entire module missing |
| Create meeting + agenda builder | ❌ | |
| Live meeting view (roll call, quorum check) | ❌ | |
| Minutes draft (Claude output) | ❌ | |
| Published minutes | ❌ | |
| AI transcript upload | ❌ | |
| Integration status (Meet / Fireflies / Zoom) | ❌ | |

---

### Fundraising `/[workspaceSlug]/campaigns`

| Component | Status | Notes |
|-----------|--------|-------|
| Campaigns list with progress bars | ✅ | Basic only |
| Create campaign form | ❌ | No funding streams, no cover image, no budget link |
| Campaign dashboard (stream breakdown, ledger) | ❌ | |
| Sponsorship logger | ❌ | |
| Public donation page | ⚠️ | `/donate/[slug]` — shows data, no checkout |

---

### Budget `/[workspaceSlug]/budgets`

| Component | Status | Notes |
|-----------|--------|-------|
| Budget list | ❌ | Entire module missing |
| Create budget + line items | ❌ | |
| Budget detail (planned vs actual, variance) | ❌ | |
| Expenditure logger | ❌ | |
| PDF export | ❌ | |

---

### Tasks `/[workspaceSlug]/tasks`

| Component | Status | Notes |
|-----------|--------|-------|
| Kanban board | ❌ | Entire module missing |
| Task list view | ❌ | |
| Create task | ❌ | |
| Task detail + comments | ❌ | |
| My tasks view | ❌ | |

---

### Announcements `/[workspaceSlug]/announcements`

| Component | Status | Notes |
|-----------|--------|-------|
| Announcement feed | ❌ | Entire module missing |
| Create announcement (rich text, target audience, schedule) | ❌ | |
| Pinned / archived | ❌ | |

---

### Smart Links `/[workspaceSlug]/links`

| Component | Status | Notes |
|-----------|--------|-------|
| Link list (slug, destination, click count) | ✅ | |
| Create link | ❌ | No UI form (only API exists) |
| Link analytics (clicks over time) | ❌ | |
| QR code download | ❌ | |
| Toggle active/inactive | ❌ | |

---

### Settings `/[workspaceSlug]/settings`

| Section | Status | Notes |
|---------|--------|-------|
| Workspace settings (name, slug, logo, brand colour, tagline) | ❌ | Entire settings page missing |
| Roles & Permissions | ❌ | |
| Members & Invitations | ❌ | |
| Integrations (Paystack, Google, Fireflies, Zoom) | ❌ | |
| Notification preferences | ❌ | |
| Billing & Plan | ❌ | |

---

## Summary Count

| Status | Pages / Components |
|--------|--------------------|
| ✅ Built | ~12 |
| ⚠️ Partial | ~10 |
| ❌ Missing | ~50+ |

The current frontend covers approximately **20–25% of spec-required screens**.
