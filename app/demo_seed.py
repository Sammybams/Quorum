from datetime import datetime, timedelta

from . import models
from .database import MongoStore
from .rbac import ensure_default_roles


DEMO_WORKSPACE_SLUG = "engineering-faculty-council-demo"
DEMO_WORKSPACE_NAME = "Engineering Faculty Council"
DEMO_OWNER_EMAIL = "demo-chair@quorum.local"


def _ensure_user(db: MongoStore, *, full_name: str, email: str, phone: str | None = None) -> models.User:
    user = db.find_one("users", {"email": email})
    if user:
        if user.get("full_name") != full_name or user.get("phone") != phone or not user.get("email_verified"):
            user["full_name"] = full_name
            user["phone"] = phone
            user["email_verified"] = True
            db.save("users", user)
        return user

    return db.insert(
        "users",
        {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "password_hash": None,
            "email_verified": True,
        },
    )


def _ensure_workspace(db: MongoStore) -> models.Workspace:
    workspace = db.find_one("workspaces", {"slug": DEMO_WORKSPACE_SLUG})
    if workspace:
        return workspace
    return db.insert(
        "workspaces",
        {
            "name": DEMO_WORKSPACE_NAME,
            "slug": DEMO_WORKSPACE_SLUG,
            "description": "Faculty body demo workspace with seven executive members, live finance records, and active operations.",
        },
    )


def _ensure_member_record(
    db: MongoStore,
    *,
    workspace_id: int,
    full_name: str,
    email: str,
    role_name: str,
    level: str,
    dues_status: str,
) -> None:
    if db.find_one("members", {"workspace_id": workspace_id, "email": email}):
        return
    db.insert(
        "members",
        {
            "workspace_id": workspace_id,
            "full_name": full_name,
            "email": email,
            "role": role_name,
            "level": level,
            "dues_status": dues_status,
        },
    )


def _ensure_membership(
    db: MongoStore,
    *,
    workspace: models.Workspace,
    user: models.User,
    role_id: int,
    level: str,
    dues_status: str,
    is_general_member: bool,
    joined_at: datetime,
) -> models.WorkspaceMember:
    membership = db.find_one("workspace_members", {"workspace_id": workspace.id, "user_id": user.id})
    if membership:
        membership["role_id"] = role_id
        membership["level"] = level
        membership["dues_status"] = dues_status
        membership["is_general_member"] = is_general_member
        membership["status"] = "active"
        membership["joined_at"] = membership.get("joined_at") or joined_at
        return db.save("workspace_members", membership)

    return db.insert(
        "workspace_members",
        {
            "workspace_id": workspace.id,
            "user_id": user.id,
            "role_id": role_id,
            "level": level,
            "dues_status": dues_status,
            "is_general_member": is_general_member,
            "status": "active",
            "joined_at": joined_at,
        },
    )


def _seed_members(db: MongoStore, workspace: models.Workspace) -> tuple[models.WorkspaceMember, list[models.WorkspaceMember]]:
    roles = ensure_default_roles(db, workspace.id)
    owner_role = roles["owner"]
    secretary_role = roles["secretary"]
    core_role = roles["core_member"]

    member_specs = [
        ("Ayo Owolabi", DEMO_OWNER_EMAIL, owner_role, "President", "paid"),
        ("Nneka Bassey", "secretary@efc-demo.local", secretary_role, "General Secretary", "paid"),
        ("Tomiwa Adeyemi", "treasurer@efc-demo.local", core_role, "Treasurer", "paid"),
        ("Favour Okonkwo", "welfare@efc-demo.local", core_role, "Welfare Director", "paid"),
        ("Daniel Yusuf", "projects@efc-demo.local", core_role, "Projects Lead", "paid"),
        ("Amina Bello", "events@efc-demo.local", core_role, "Events Coordinator", "defaulter"),
        ("David Omotoso", "media@efc-demo.local", core_role, "Publicity Director", "defaulter"),
    ]

    memberships: list[models.WorkspaceMember] = []
    start = datetime.utcnow() - timedelta(days=28)
    for index, (full_name, email, role, level, dues_status) in enumerate(member_specs):
        user = _ensure_user(db, full_name=full_name, email=email, phone=f"+23480100000{index}")
        membership = _ensure_membership(
            db,
            workspace=workspace,
            user=user,
            role_id=role.id,
            level=level,
            dues_status=dues_status,
            is_general_member=role.key == "core_member",
            joined_at=start + timedelta(days=index),
        )
        _ensure_member_record(
            db,
            workspace_id=workspace.id,
            full_name=full_name,
            email=email,
            role_name=role.name,
            level=level,
            dues_status=dues_status,
        )
        memberships.append(membership)

    workspace["owner_user_id"] = memberships[0].user_id
    db.save("workspaces", workspace)
    return memberships[0], memberships


def _seed_dues(db: MongoStore, workspace: models.Workspace, memberships: list[models.WorkspaceMember]) -> None:
    cycle = db.find_one("dues_cycles", {"workspace_id": workspace.id, "name": "2026 Leadership Levy"})
    if cycle is None:
        cycle = db.insert(
            "dues_cycles",
            {
                "workspace_id": workspace.id,
                "name": "2026 Leadership Levy",
                "amount": 3500,
                "deadline": "2026-05-15",
            },
        )

    if db.find_many("dues_payments", {"workspace_id": workspace.id}, limit=1):
        return

    for membership in memberships[:5]:
        db.insert(
            "dues_payments",
            {
                "workspace_id": workspace.id,
                "cycle_id": cycle.id,
                "member_id": membership.id,
                "amount": 3500,
                "method": "manual",
                "gateway_ref": f"EFC-DUES-{membership.id}",
                "status": "paid",
                "confirmed_by_user_id": memberships[0].user_id,
                "confirmed_at": datetime.utcnow() - timedelta(days=6),
            },
        )


def _seed_events(db: MongoStore, workspace: models.Workspace, memberships: list[models.WorkspaceMember]) -> None:
    if db.find_many("events", {"workspace_id": workspace.id}, limit=1):
        return

    event_specs = [
        {
            "title": "Engineering Week Town Hall",
            "slug": "efc-engineering-week-town-hall",
            "event_type": "town_hall",
            "starts_at": "2026-05-04 16:00",
            "venue": "ETF Lecture Theatre",
            "description": "Leadership briefing for Engineering Week with open questions from class reps.",
            "rsvp_enabled": True,
            "capacity": 250,
            "thumbnail_url": None,
            "rsvp_count": 7,
            "created_by_user_id": memberships[0].user_id,
        },
        {
            "title": "Treasury and Welfare Review",
            "slug": "efc-treasury-welfare-review",
            "event_type": "review",
            "starts_at": "2026-05-11 18:00",
            "venue": "Council Chamber",
            "description": "Mid-session review of dues, welfare disbursements, and sponsor commitments.",
            "rsvp_enabled": True,
            "capacity": 80,
            "thumbnail_url": None,
            "rsvp_count": 5,
            "created_by_user_id": memberships[1].user_id,
        },
    ]

    created_events = [db.insert("events", {"workspace_id": workspace.id, **spec}) for spec in event_specs]

    for index, membership in enumerate(memberships):
        user = db.find_by_id("users", membership.user_id)
        db.insert(
            "event_attendees",
            {
                "event_id": created_events[0].id,
                "workspace_id": workspace.id,
                "member_id": membership.id,
                "full_name": user.full_name if user else f"Member {membership.id}",
                "email": user.email if user else f"member-{membership.id}@example.com",
                "status": "checked_in" if index < 5 else "registered",
                "rsvp_at": datetime.utcnow() - timedelta(days=4, hours=index),
                "checked_in_at": datetime.utcnow() - timedelta(days=4, minutes=30 - index) if index < 5 else None,
            },
        )


def _seed_campaigns(db: MongoStore, workspace: models.Workspace, memberships: list[models.WorkspaceMember]) -> None:
    campaign = db.find_one("campaigns", {"workspace_id": workspace.id, "slug": "efc-engineering-week-fund"})
    if campaign is None:
        campaign = db.insert(
            "campaigns",
            {
                "workspace_id": workspace.id,
                "name": "Engineering Week Fund",
                "slug": "efc-engineering-week-fund",
                "target_amount": 1200000,
                "raised_amount": 742000,
                "status": "active",
            },
        )

    if db.find_many("funding_streams", {"campaign_id": campaign.id}, limit=1):
        return

    streams = [
        db.insert(
            "funding_streams",
            {
                "workspace_id": workspace.id,
                "campaign_id": campaign.id,
                "name": "Corporate sponsors",
                "stream_type": "sponsorship",
                "target_amount": 700000,
            },
        ),
        db.insert(
            "funding_streams",
            {
                "workspace_id": workspace.id,
                "campaign_id": campaign.id,
                "name": "Alumni support",
                "stream_type": "donation",
                "target_amount": 350000,
            },
        ),
        db.insert(
            "funding_streams",
            {
                "workspace_id": workspace.id,
                "campaign_id": campaign.id,
                "name": "Merchandise presales",
                "stream_type": "sales",
                "target_amount": 150000,
            },
        ),
    ]

    contribution_specs = [
        (streams[0].id, "TekBridge Systems", "finance@tekbridge.ng", 320000, "bank_transfer"),
        (streams[0].id, "Ace Robotics", "hello@acerobotics.ng", 180000, "manual"),
        (streams[1].id, "Evelyn Ogunleye", "evelyn@example.com", 90000, "manual"),
        (streams[1].id, "Class of 2014", "alumni2014@example.com", 72000, "manual"),
        (streams[2].id, "Hoodie presales", "sales@efc-demo.local", 80000, "manual"),
    ]

    for index, (stream_id, contributor_name, contributor_email, amount, method) in enumerate(contribution_specs, start=1):
        db.insert(
            "contributions",
            {
                "workspace_id": workspace.id,
                "campaign_id": campaign.id,
                "stream_id": stream_id,
                "contributor_name": contributor_name,
                "contributor_email": contributor_email,
                "amount": amount,
                "method": method,
                "gateway_ref": f"EFC-CONTRIB-{index}",
                "receipt_url": None,
                "is_anonymous": False,
                "status": "confirmed",
                "confirmed_by_user_id": memberships[0].user_id,
                "confirmed_at": datetime.utcnow() - timedelta(days=3),
            },
        )


def _seed_links(db: MongoStore, workspace: models.Workspace) -> None:
    if db.find_many("short_links", {"workspace_id": workspace.id}, limit=1):
        return

    db.insert(
        "short_links",
        {
            "workspace_id": workspace.id,
            "slug": "efc-levy",
            "destination_url": "https://quorum.ng/portal/engineering-faculty-council-demo",
            "title": "Pay leadership levy",
            "click_count": 184,
            "is_active": True,
        },
    )
    db.insert(
        "short_links",
        {
            "workspace_id": workspace.id,
            "slug": "efc-sponsor",
            "destination_url": "https://quorum.ng/donate/efc-engineering-week-fund",
            "title": "Sponsor Engineering Week",
            "click_count": 96,
            "is_active": True,
        },
    )


def _seed_announcements(db: MongoStore, workspace: models.Workspace) -> None:
    if db.find_many("announcements", {"workspace_id": workspace.id}, limit=1):
        return

    now = datetime.utcnow()
    db.insert(
        "announcements",
        {
            "workspace_id": workspace.id,
            "title": "Engineering Week sponsor deck is live",
            "body": "Sponsor outreach has started. Use the new fundraising link in the campaigns module for outreach follow-up.",
            "status": "published",
            "is_pinned": True,
            "published_at": now - timedelta(days=2),
            "scheduled_for": None,
            "delivered_at": now - timedelta(days=2),
            "delivery_count": 7,
            "audience": "all_members",
            "channels": ["in_app", "email"],
            "target_role_ids": [],
            "target_levels": [],
            "archived_at": None,
            "updated_at": now - timedelta(days=2),
        },
    )
    db.insert(
        "announcements",
        {
            "workspace_id": workspace.id,
            "title": "Treasury review moved to Chamber B",
            "body": "Please note the venue change for the treasury and welfare review meeting on Monday evening.",
            "status": "published",
            "is_pinned": False,
            "published_at": now - timedelta(days=1),
            "scheduled_for": None,
            "delivered_at": now - timedelta(days=1),
            "delivery_count": 7,
            "audience": "all_members",
            "channels": ["in_app"],
            "target_role_ids": [],
            "target_levels": [],
            "archived_at": None,
            "updated_at": now - timedelta(days=1),
        },
    )


def _seed_meetings_and_tasks(db: MongoStore, workspace: models.Workspace, memberships: list[models.WorkspaceMember]) -> None:
    if db.find_many("meetings", {"workspace_id": workspace.id}, limit=1):
        return

    meeting = db.insert(
        "meetings",
        {
            "workspace_id": workspace.id,
            "title": "Engineering Week Planning Council",
            "meeting_type": "executive",
            "scheduled_for": "2026-05-01 17:00",
            "venue": "Dean's Board Room",
            "virtual_link": "https://meet.google.com/efc-demo-week",
            "agenda": ["Sponsorship pipeline", "Volunteer assignments", "Welfare logistics"],
            "quorum_threshold": 5,
            "status": "minutes_published",
            "transcript": "Planning session for Engineering Week covering sponsor follow-ups, volunteer assignments, and logistics.",
            "transcript_source": "demo_seed",
            "attendee_count": 7,
            "created_by_user_id": memberships[1].user_id,
        },
    )

    db.insert(
        "meeting_minutes",
        {
            "meeting_id": meeting.id,
            "summary": "Council aligned on sponsor follow-up, volunteer coordination, and the welfare checklist for Engineering Week.",
            "content": "Decisions were taken on sponsor escalation, booth logistics, volunteer coordination, and welfare disbursement timing.",
            "attendance_summary": "7 of 7 executive members present.",
            "decisions": [
                "Treasurer to finalize sponsor follow-up sheet by Friday.",
                "Events coordinator to publish volunteer rota after Sunday briefing.",
                "Welfare lead to lock refreshment vendors before next review.",
            ],
            "ai_status": "published",
            "generated_by_model": "claude-sonnet-4-20250514",
            "generated_at": datetime.utcnow() - timedelta(days=3),
            "generation_error": None,
            "published_at": datetime.utcnow() - timedelta(days=3),
            "published_by_user_id": memberships[1].user_id,
            "updated_at": datetime.utcnow() - timedelta(days=3),
        },
    )

    action_specs = [
        ("Prepare sponsor escalation tracker", memberships[2].id, "2026-05-03"),
        ("Publish volunteer rota", memberships[5].id, "2026-05-04"),
        ("Confirm welfare vendor quotes", memberships[3].id, "2026-05-04"),
    ]

    for index, (description, assigned_to_member_id, due_date) in enumerate(action_specs, start=1):
        db.insert(
            "action_items",
            {
                "meeting_id": meeting.id,
                "description": description,
                "assigned_to_member_id": assigned_to_member_id,
                "due_date": due_date,
                "status": "open" if index < 3 else "in_progress",
                "generated_by": "claude",
            },
        )
        assignee = db.find_by_id("workspace_members", assigned_to_member_id)
        db.insert(
            "tasks",
            {
                "workspace_id": workspace.id,
                "title": description,
                "description": "Demo follow-up task created from published meeting minutes.",
                "assigned_to_member_id": assigned_to_member_id,
                "due_date": due_date,
                "priority": "high" if index == 1 else "medium",
                "status": "in_progress" if index == 1 else "todo",
                "linked_module": "meeting",
                "linked_id": meeting.id,
                "created_by_user_id": assignee.user_id if assignee else memberships[1].user_id,
            },
        )


def _seed_budgets(db: MongoStore, workspace: models.Workspace) -> None:
    budget = db.find_one("budgets", {"workspace_id": workspace.id, "name": "Engineering Week 2026"})
    if budget is None:
        budget = db.insert(
            "budgets",
            {
                "workspace_id": workspace.id,
                "name": "Engineering Week 2026",
                "description": "Session budget for sponsor-funded Engineering Week operations.",
                "period_label": "2026 Session",
                "status": "active",
                "planned_total": 540000,
                "actual_total": 168000,
            },
        )

    if db.find_many("budget_lines", {"budget_id": budget.id}, limit=1):
        return

    lines = [
        ("Venue and stage", 180000, 90000),
        ("Media and design", 120000, 28000),
        ("Welfare and refreshments", 90000, 22000),
        ("Volunteer logistics", 150000, 28000),
    ]

    for name, planned_amount, actual_amount in lines:
        line = db.insert(
            "budget_lines",
            {
                "budget_id": budget.id,
                "name": name,
                "planned_amount": planned_amount,
                "actual_amount": actual_amount,
                "notes": "Demo seeded line item",
            },
        )
        if actual_amount:
            db.insert(
                "expenditures",
                {
                    "budget_line_id": line.id,
                    "amount": actual_amount,
                    "notes": "Demo seeded expenditure",
                    "spent_at": "2026-04-20",
                },
            )


def ensure_demo_workspace(db: MongoStore) -> tuple[models.Workspace, models.WorkspaceMember]:
    workspace = _ensure_workspace(db)
    owner_membership, memberships = _seed_members(db, workspace)
    _seed_dues(db, workspace, memberships)
    _seed_events(db, workspace, memberships)
    _seed_campaigns(db, workspace, memberships)
    _seed_links(db, workspace)
    _seed_announcements(db, workspace)
    _seed_meetings_and_tasks(db, workspace, memberships)
    _seed_budgets(db, workspace)
    return workspace, owner_membership
