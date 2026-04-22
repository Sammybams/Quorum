import Link from "next/link";
import type { ReactNode } from "react";

export default function WorkspaceLayout({
  children,
  params,
}: {
  children: ReactNode;
  params: { workspaceSlug: string };
}) {
  const base = `/${params.workspaceSlug}`;

  return (
    <div className="atelier-shell">
      <aside className="atelier-sidenav">
        <div className="atelier-brand-wrap">
          <div className="atelier-brand-icon">Q</div>
          <div>
            <div className="atelier-brand">Quorum</div>
            <div className="atelier-brand-sub">Student Body Admin</div>
          </div>
        </div>

        <button className="atelier-btn-primary" type="button">
          New Campaign
        </button>

        <nav className="atelier-navlist">
          <Link className="atelier-nav-item" href={`${base}/dashboard`}>
            Dashboard
          </Link>
          <Link className="atelier-nav-item" href={`${base}/members`}>
            Members
          </Link>
          <Link className="atelier-nav-item" href={`${base}/events`}>
            Events
          </Link>
          <Link className="atelier-nav-item" href={`${base}/campaigns`}>
            Fundraising
          </Link>
          <Link className="atelier-nav-item" href={`${base}/dues`}>
            Dues
          </Link>
          <Link className="atelier-nav-item" href={`${base}/links`}>
            Links
          </Link>
        </nav>

        <div className="atelier-nav-foot">
          <a className="atelier-nav-item" href="#" aria-disabled="true">
            Settings
          </a>
          <a className="atelier-nav-item" href="#" aria-disabled="true">
            Support
          </a>
        </div>
      </aside>

      <div className="atelier-main-wrap">
        <header className="atelier-topbar">
          <div className="atelier-topbar-left">
            <div className="atelier-workspace-pill">{params.workspaceSlug}</div>
            <div className="atelier-search">
              <input type="text" placeholder="Search workspace" />
            </div>
          </div>

          <div className="atelier-topbar-right">
            <Link href={`${base}/events/new`} className="atelier-btn-secondary">
              Create Event
            </Link>
            <Link href="/" className="atelier-btn-ghost">
              Landing
            </Link>
          </div>
        </header>

        <main className="atelier-canvas">{children}</main>
      </div>
    </div>
  );
}
