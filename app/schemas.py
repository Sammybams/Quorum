from datetime import datetime
from pydantic import BaseModel, Field


class WorkspaceBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=120)
    description: str | None = None


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceOut(WorkspaceBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberBase(BaseModel):
    full_name: str
    email: str
    role: str = "member"
    level: str | None = None


class MemberCreate(MemberBase):
    pass


class MemberOut(MemberBase):
    id: int
    workspace_id: int
    dues_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class DuesCycleCreate(BaseModel):
    name: str
    amount: float
    deadline: str | None = None


class DuesCycleOut(DuesCycleCreate):
    id: int
    workspace_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EventCreate(BaseModel):
    title: str
    slug: str
    event_type: str = "social"
    starts_at: str
    venue: str | None = None
    description: str | None = None
    rsvp_enabled: bool = True
    capacity: int | None = None


class EventOut(EventCreate):
    id: int
    workspace_id: int
    rsvp_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignCreate(BaseModel):
    name: str
    slug: str
    target_amount: float


class CampaignOut(CampaignCreate):
    id: int
    workspace_id: int
    raised_amount: float
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LinkCreate(BaseModel):
    slug: str
    destination_url: str


class LinkOut(LinkCreate):
    id: int
    workspace_id: int
    click_count: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthLoginRequest(BaseModel):
    workspace_slug: str | None = None
    email: str
    password: str | None = None


class AuthLoginResponse(BaseModel):
    workspace_slug: str
    workspace_name: str
    member_id: int
    member_name: str
    member_role: str


class AuthRegisterRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=120)
    workspace_slug: str = Field(min_length=2, max_length=120)
    university: str | None = None
    body_type: str | None = None
    faculty: str | None = None
    admin_name: str = Field(min_length=2, max_length=120)
    admin_email: str
    phone_number: str | None = None
    admin_role: str = "super_admin"
    password: str | None = None


class DashboardCounts(BaseModel):
    members: int
    dues_cycles: int
    events: int
    campaigns: int
    links: int
    paid_members: int
    pending_members: int


class WorkspaceOverview(BaseModel):
    workspace: WorkspaceOut
    counts: DashboardCounts
    recent_events: list[EventOut]
    active_campaigns: list[CampaignOut]
    dues_cycles: list[DuesCycleOut]
    links: list[LinkOut]
