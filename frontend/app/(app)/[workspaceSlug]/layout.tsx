"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";

import { clearSession, readSession, saveSession, type QuorumSession, type QuorumWorkspace } from "@/lib/session";

const navItems = [
  { label: "Dashboard", icon: "dashboard", href: "dashboard" },
  { label: "Members", icon: "group", href: "members" },
  { label: "Events", icon: "event", href: "events" },
  { label: "Fundraising", icon: "payments", href: "campaigns" },
  { label: "Dues", icon: "receipt_long", href: "dues" },
  { label: "Links", icon: "link", href: "links" },
  { label: "Announcements", icon: "campaign", href: "announcements" },
  { label: "Settings", icon: "settings", href: "settings/roles" },
];

export default function WorkspaceLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: { workspaceSlug: string };
}) {
  const base = `/${params.workspaceSlug}`;
  const router = useRouter();
  const [session, setSession] = useState<QuorumSession | null>(null);
  const [workspaceOpen, setWorkspaceOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const workspaceMenuRef = useRef<HTMLDivElement | null>(null);
  const profileMenuRef = useRef<HTMLDivElement | null>(null);
  const workspaceName = session?.workspace_name || params.workspaceSlug;
  const workspaceLabel = workspaceName.split("-").join(" ");

  useEffect(() => {
    setSession(readSession());
  }, []);

  useEffect(() => {
    function onPointerDown(event: PointerEvent) {
      const target = event.target as Node;
      if (workspaceMenuRef.current && !workspaceMenuRef.current.contains(target)) {
        setWorkspaceOpen(false);
      }
      if (profileMenuRef.current && !profileMenuRef.current.contains(target)) {
        setProfileOpen(false);
      }
    }

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setWorkspaceOpen(false);
        setProfileOpen(false);
      }
    }

    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);

    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  function signOut() {
    clearSession();
    router.push("/login");
  }

  function switchWorkspace(workspace: QuorumWorkspace) {
    if (!session) {
      return;
    }
    const nextSession: QuorumSession = {
      ...session,
      workspace_slug: workspace.workspace_slug,
      workspace_name: workspace.workspace_name,
      member_id: workspace.member_id,
      member_role: workspace.role,
      role_key: workspace.role_key,
    };
    saveSession(nextSession);
    setSession(nextSession);
    setWorkspaceOpen(false);
    router.push(`/${workspace.workspace_slug}/dashboard`);
  }

  const initials = session?.member_name
    ? session.member_name
        .split(" ")
        .map((part) => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "Q";

  return (
    <div className="app-shell">
      <aside className="side-nav">
        <Link href={`${base}/dashboard`} className="brand-block">
          <img className="brand-logo-img" src="/brand/quorum-icon-circle.svg" alt="" />
          <span className="brand-copy">
            <strong>Quorum</strong>
            <small title={workspaceLabel || "Student Body Admin"}>{workspaceLabel || "Student Body Admin"}</small>
          </span>
        </Link>

        <nav className="nav-list" aria-label="Workspace">
          {navItems.map((item) => (
            <Link key={item.href} className="nav-item" href={`${base}/${item.href}`}>
              <span className="material-symbols-outlined" aria-hidden="true">
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="side-nav-actions">
          <Link href={`${base}/campaigns`} className="side-action primary">
            <span className="material-symbols-outlined" aria-hidden="true">
              add
            </span>
            <span>New Campaign</span>
          </Link>
          <button type="button" className="side-action" onClick={signOut}>
            <span className="material-symbols-outlined" aria-hidden="true">
              logout
            </span>
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      <div className="workspace-frame">
        <header className="topbar">
          <div className="workspace-switcher" ref={workspaceMenuRef}>
            <button
              type="button"
              className="workspace-pill"
              title={session?.workspace_name || params.workspaceSlug}
              aria-expanded={workspaceOpen}
              onClick={() => {
                setWorkspaceOpen((value) => !value);
                setProfileOpen(false);
              }}
            >
              <span className="material-symbols-outlined" aria-hidden="true">
                expand_more
              </span>
              <span className="workspace-pill-text">{workspaceLabel || params.workspaceSlug}</span>
            </button>
            {workspaceOpen ? (
              <div className="workspace-menu">
                {(session?.workspaces || []).length > 0 ? (
                  session?.workspaces?.map((workspace) => (
                    <button
                      key={workspace.workspace_slug}
                      type="button"
                      className={workspace.workspace_slug === params.workspaceSlug ? "active" : ""}
                      onClick={() => switchWorkspace(workspace)}
                    >
                      <span>
                        <strong>{workspace.workspace_name}</strong>
                        <small>{workspace.role}</small>
                      </span>
                      {workspace.workspace_slug === params.workspaceSlug ? (
                        <span className="material-symbols-outlined" aria-hidden="true">
                          check
                        </span>
                      ) : null}
                    </button>
                  ))
                ) : (
                  <p>Sign in again to load your communities.</p>
                )}
              </div>
            ) : null}
          </div>
          <div className="topbar-actions">
            <button type="button" className="icon-button" aria-label="Notifications">
              <span className="material-symbols-outlined" aria-hidden="true">
                notifications
              </span>
            </button>
            <Link href={`${base}/events/new`} className="btn-secondary">
              <span className="material-symbols-outlined" aria-hidden="true">
                add
              </span>
              Create Event
            </Link>
            <div className="profile-menu-wrap" ref={profileMenuRef}>
              <button
                type="button"
                className="avatar-chip"
                aria-label="Open profile menu"
                aria-expanded={profileOpen}
                onClick={() => {
                  setProfileOpen((value) => !value);
                  setWorkspaceOpen(false);
                }}
              >
                {initials}
              </button>
              {profileOpen ? (
                <div className="profile-menu">
                  <div>
                    <strong>{session?.member_name || "Quorum user"}</strong>
                    <span>{session?.member_role || "Workspace member"}</span>
                  </div>
                  <Link href={`${base}/dashboard`}>
                    <span className="material-symbols-outlined" aria-hidden="true">
                      person
                    </span>
                    Profile
                  </Link>
                  <Link href={`${base}/settings/workspace`}>
                    <span className="material-symbols-outlined" aria-hidden="true">
                      settings
                    </span>
                    Settings
                  </Link>
                  <button type="button" onClick={signOut}>
                    <span className="material-symbols-outlined" aria-hidden="true">
                      logout
                    </span>
                    Sign out
                  </button>
                </div>
              ) : null}
            </div>
          </div>
        </header>

        <main className="workspace-canvas">{children}</main>
      </div>
    </div>
  );
}
