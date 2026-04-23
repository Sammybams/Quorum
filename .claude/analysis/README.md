# Quorum — Product Spec Analysis

Cross-reference of `Quorum_Product_Specification.docx` against the current codebase.

## Files

| File | Contents |
|------|----------|
| [endpoints.md](endpoints.md) | All API endpoints — what's built vs what the spec requires |
| [frontend-routes.md](frontend-routes.md) | All frontend pages/routes — built vs spec |
| [data-models.md](data-models.md) | DB model comparison — current ORM vs spec schema |
| [gap-analysis.md](gap-analysis.md) | Prioritised gap list — what needs to be built |

## Quick Summary

### What's been built so far

The current implementation covers the **MVP scaffolding** for a subset of the platform:

- Auth (register + login, localStorage session, no JWT)
- Workspaces CRUD + overview dashboard
- Members (list + create only)
- Dues cycles (list + create only)
- Events (list + create only)
- Campaigns (list + create only)
- Short links (list + create only)
- Public endpoints: event page, donation page, portal, link redirect
- Next.js frontend with all corresponding pages

### What the spec requires beyond the current build

13 additional API domains are fully absent:
- Roles & Permissions system
- Meetings + AI transcript processing
- Tasks module
- Budget Planner
- Announcements
- Integrations (Paystack, Flutterwave, Google Meet, Fireflies, Zoom)
- Webhooks (payment + meeting transcript)
- AI (Claude integration)
- Notifications
- Invitation system (token-based invite by email + invite link)
- RSVP / Attendance tracking
- Payment flows (dues payments, donations)
- Settings page (full)

Full detail in [gap-analysis.md](gap-analysis.md).
