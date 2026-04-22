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
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          Quo<span>rum</span>
        </div>
        <div className="workspace-chip">Workspace: {params.workspaceSlug}</div>
        <Link className="nav-link" href={`${base}/dashboard`}>
          Dashboard
        </Link>
        <Link className="nav-link" href={`${base}/events`}>
          Events
        </Link>
        <Link className="nav-link" href={`${base}/events/new`}>
          Create Event
        </Link>
        <Link className="nav-link" href={`${base}/dues`}>
          Dues
        </Link>
        <Link className="nav-link" href={`${base}/campaigns`}>
          Campaigns
        </Link>
        <Link className="nav-link" href={`${base}/links`}>
          Links
        </Link>
      </aside>

      <div className="app-main">
        <div className="main-head">
          <div>
            <h1>Quorum Workspace</h1>
            <small className="muted">Student body operations dashboard</small>
          </div>
          <div>
            <Link href="/" className="btn btn-ghost">
              Landing
            </Link>
          </div>
        </div>
        {children}
      </div>
    </div>
  );
}
