"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { clearSession, readSession, type QuorumSession } from "@/lib/session";

const navItems = [
  { label: "Dashboard", icon: "dashboard", href: "dashboard" },
  { label: "Members", icon: "group", href: "members" },
  { label: "Events", icon: "event", href: "events" },
  { label: "Fundraising", icon: "payments", href: "campaigns" },
  { label: "Dues", icon: "receipt_long", href: "dues" },
  { label: "Links", icon: "link", href: "links" },
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
  const [profileOpen, setProfileOpen] = useState(false);

  useEffect(() => {
    setSession(readSession());
  }, []);

  function signOut() {
    clearSession();
    router.push("/login");
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
          <span className="brand-mark">Q</span>
          <span>
            <strong>Quorum</strong>
            <small>Student Body Admin</small>
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
          <div className="workspace-pill">
            <span className="material-symbols-outlined" aria-hidden="true">
              expand_more
            </span>
            {params.workspaceSlug}
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
            <div className="profile-menu-wrap">
              <button
                type="button"
                className="avatar-chip"
                aria-label="Open profile menu"
                aria-expanded={profileOpen}
                onClick={() => setProfileOpen((value) => !value)}
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
                  <Link href={`${base}/dashboard`}>
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
