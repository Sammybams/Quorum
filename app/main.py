import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, campaigns, dues, events, health, invitations, links, members, public, roles, webhooks, workspaces

app = FastAPI(title=os.getenv("APP_NAME", "Quorum API"))

frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
allowed_origins = [frontend_origin] if frontend_origin != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


api_prefix = os.getenv("API_PREFIX", "/api/v1")

app.include_router(health.router, prefix=api_prefix)
app.include_router(workspaces.router, prefix=api_prefix)
app.include_router(auth.router, prefix=api_prefix)
app.include_router(members.router, prefix=api_prefix)
app.include_router(roles.router, prefix=api_prefix)
app.include_router(invitations.router, prefix=api_prefix)
app.include_router(invitations.public_router, prefix=api_prefix)
app.include_router(dues.router, prefix=api_prefix)
app.include_router(dues.payments_router, prefix=api_prefix)
app.include_router(events.router, prefix=api_prefix)
app.include_router(campaigns.router, prefix=api_prefix)
app.include_router(links.router, prefix=api_prefix)
app.include_router(public.router, prefix=api_prefix)
app.include_router(webhooks.router, prefix=api_prefix)
