import { apiGet } from "@/lib/api";

type Workspace = {
  id: number;
  name: string;
  slug: string;
  description?: string;
};

type Event = {
  id: number;
  title: string;
  starts_at: string;
  venue?: string;
  rsvp_count: number;
};

type Campaign = {
  id: number;
  name: string;
  target_amount: number;
  raised_amount: number;
  status: string;
};

export default async function DashboardPage({
  params,
}: {
  params: { workspaceSlug: string };
}) {
  let workspace: Workspace | null = null;
  let events: Event[] = [];
  let campaigns: Campaign[] = [];

  try {
    workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
    events = await apiGet<Event[]>(`/workspaces/${workspace.id}/events`);
    campaigns = await apiGet<Campaign[]>(`/workspaces/${workspace.id}/campaigns`);
  } catch {
    return (
      <section className="panel">
        <h3>Workspace Not Found Yet</h3>
        <p className="muted">
          Create a workspace using the backend endpoint, then reload this page with the correct slug.
        </p>
        <code>POST /api/v1/workspaces</code>
      </section>
    );
  }

  const activeCampaign = campaigns.find((c) => c.status === "active") || null;
  const totalRaised = campaigns.reduce((sum, c) => sum + c.raised_amount, 0);

  return (
    <>
      <div className="panel" style={{ marginBottom: 12 }}>
        <strong style={{ color: "#a16207" }}>Attention:</strong>{" "}
        <span className="muted">42 members still marked as unpaid in this demo view.</span>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="label">Workspace</div>
          <div className="value" style={{ fontSize: "1.2rem" }}>
            {workspace.name}
          </div>
          <small className="muted">{workspace.description || "No description yet."}</small>
        </div>

        <div className="kpi-card">
          <div className="label">Events This Session</div>
          <div className="value">{events.length}</div>
          <small className="muted">Tracked from events module</small>
        </div>

        <div className="kpi-card">
          <div className="label">Campaigns</div>
          <div className="value">{campaigns.length}</div>
          <small className="muted">{activeCampaign ? "Active campaign running" : "No active campaign"}</small>
        </div>

        <div className="kpi-card">
          <div className="label">Total Raised</div>
          <div className="value">₦{totalRaised.toLocaleString()}</div>
          <small className="muted">Across all campaigns</small>
        </div>
      </div>

      <div className="content-grid">
        <div className="panel">
          <h3>Upcoming Events</h3>
          {events.length === 0 ? (
            <p className="muted">No events yet.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Date</th>
                  <th>RSVPs</th>
                </tr>
              </thead>
              <tbody>
                {events.slice(0, 5).map((event) => (
                  <tr key={event.id}>
                    <td>{event.title}</td>
                    <td>{event.starts_at}</td>
                    <td>{event.rsvp_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="mini-list">
          <div className="panel campaign-block">
            <h3 style={{ marginTop: 0 }}>Annual Campaign Snapshot</h3>
            {!activeCampaign ? (
              <p style={{ margin: 0, opacity: 0.92 }}>No active campaign yet.</p>
            ) : (
              <>
                <p style={{ marginBottom: 8 }}>
                  <strong>{activeCampaign.name}</strong>
                </p>
                <p style={{ marginTop: 0 }}>
                  ₦{activeCampaign.raised_amount.toLocaleString()} / ₦{activeCampaign.target_amount.toLocaleString()}
                </p>
                <div className="campaign-progress">
                  <span
                    style={{
                      width: `${Math.min(
                        100,
                        Math.round((activeCampaign.raised_amount / Math.max(activeCampaign.target_amount, 1)) * 100),
                      )}%`,
                    }}
                  />
                </div>
              </>
            )}
          </div>

          <div className="panel">
            <h3 style={{ marginTop: 0 }}>Pinned Notes</h3>
            <div className="mini-item">
              <strong>Annual Dinner - Final Ticket Push</strong>
              <p className="muted" style={{ marginBottom: 0 }}>
                Reminder sent to all levels. Deadline this Friday.
              </p>
            </div>
            <div className="mini-item">
              <strong>Dues Extension Notice</strong>
              <p className="muted" style={{ marginBottom: 0 }}>
                Session dues deadline shifted to accommodate exams.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
