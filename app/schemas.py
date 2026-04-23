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


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    slug: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None


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


class RoleOut(BaseModel):
    id: int
    workspace_id: int
    key: str
    name: str
    description: str | None = None
    is_system_role: bool
    permissions: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    permissions: list[str] = []


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    permissions: list[str] | None = None


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str | None = None
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceMemberOut(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role_id: int
    full_name: str
    email: str
    role: str
    role_key: str
    level: str | None = None
    dues_status: str
    status: str
    is_general_member: bool
    created_at: datetime


class DuesCycleCreate(BaseModel):
    name: str
    amount: float
    deadline: str | None = None


class DuesCycleOut(DuesCycleCreate):
    id: int
    workspace_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DuesPaymentCreate(BaseModel):
    member_id: int | None = None
    amount: float
    method: str = "manual"
    gateway_ref: str | None = None
    receipt_url: str | None = None


class DuesPaymentCheckoutCreate(BaseModel):
    member_id: int | None = None
    email: str | None = None
    amount: float | None = Field(default=None, gt=0)


class DuesPaymentOut(BaseModel):
    id: int
    workspace_id: int
    cycle_id: int
    member_id: int | None = None
    member_name: str | None = None
    amount: float
    method: str
    gateway_ref: str | None = None
    receipt_url: str | None = None
    status: str
    confirmed_by_user_id: int | None = None
    confirmed_at: datetime | None = None
    created_at: datetime


class DuesPaymentCheckoutResponse(BaseModel):
    payment: DuesPaymentOut
    payment_reference: str
    checkout_url: str | None = None
    access_code: str | None = None
    provider: str = "paystack"


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


class FundingStreamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    stream_type: str = "general"
    target_amount: float | None = None


class FundingStreamOut(FundingStreamCreate):
    id: int
    workspace_id: int
    campaign_id: int
    raised_amount: float = 0
    created_at: datetime


class ContributionCreate(BaseModel):
    stream_id: int | None = None
    contributor_name: str | None = None
    contributor_email: str | None = None
    amount: float = Field(gt=0)
    method: str = "manual"
    gateway_ref: str | None = None
    receipt_url: str | None = None
    is_anonymous: bool = False


class ContributionOut(BaseModel):
    id: int
    workspace_id: int
    campaign_id: int
    stream_id: int | None = None
    stream_name: str | None = None
    contributor_name: str | None = None
    contributor_email: str | None = None
    amount: float
    method: str
    gateway_ref: str | None = None
    receipt_url: str | None = None
    is_anonymous: bool
    status: str
    confirmed_by_user_id: int | None = None
    confirmed_at: datetime | None = None
    created_at: datetime


class CampaignDetailOut(CampaignOut):
    funding_streams: list[FundingStreamOut] = Field(default_factory=list)
    contributions: list[ContributionOut] = Field(default_factory=list)
    contributor_count: int = 0


class PublicContributionCreate(BaseModel):
    stream_id: int | None = None
    contributor_name: str | None = None
    contributor_email: str | None = None
    amount: float = Field(gt=0)
    is_anonymous: bool = False


class PublicContributionResponse(BaseModel):
    contribution: ContributionOut
    payment_reference: str
    checkout_url: str | None = None
    access_code: str | None = None
    provider: str = "paystack"


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
    user_id: int | None = None
    role_key: str | None = None
    access_token: str | None = None
    token_type: str = "bearer"


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


class AuthMeWorkspace(BaseModel):
    workspace_slug: str
    workspace_name: str
    member_id: int
    role: str
    role_key: str
    permissions: list[str]


class AuthMeResponse(BaseModel):
    user: UserOut
    workspaces: list[AuthMeWorkspace]


class InvitationCreate(BaseModel):
    email: str
    role_id: int
    note: str | None = None


class InvitationOut(BaseModel):
    id: int
    workspace_id: int
    email: str
    role_id: int
    role_name: str
    token: str
    status: str
    expires_at: datetime | None = None
    created_at: datetime


class InviteLinkCreate(BaseModel):
    role_id: int
    expires_at: datetime | None = None


class InviteLinkOut(BaseModel):
    id: int
    workspace_id: int
    role_id: int
    role_name: str
    token: str
    is_active: bool
    expires_at: datetime | None = None
    created_at: datetime


class InvitePreview(BaseModel):
    workspace_name: str
    workspace_slug: str
    email: str | None = None
    role_name: str
    expires_at: datetime | None = None


class InvitationAccept(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6)
    phone_number: str | None = None


class InviteLinkAccept(InvitationAccept):
    email: str


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
