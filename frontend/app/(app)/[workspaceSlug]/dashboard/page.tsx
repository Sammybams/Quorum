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

  const activeCampaign = campaigns.find((c) => c.status === "active") || campaigns[0] || null;

  return (
    <section className="atelier-stack">
      <header className="atelier-pagehead">
        <h1>Good morning, Oluwaseun</h1>
        <p>Here is what is happening with {workspace.name} today.</p>
      </header>

      <section className="atelier-alert">
        <div>
          <h3>Dues Deadline Approaching</h3>
          <p>42 members have not paid their 2024/2025 dues. Deadline: Dec 15.</p>
        </div>
        <button type="button" className="atelier-inline-cta">
          View Defaulters
        </button>
      </section>

      <section className="atelier-metrics">
        <article className="metric-primary">
          <small>Total Members</small>
          <strong>187</strong>
        </article>

        <article className="metric-card">
          <small>Dues Paid</small>
          <strong>77%</strong>
          <span>+12% from last cycle</span>
        </article>

        <article className="metric-card">
          <small>Events this Session</small>
          <strong>{events.length}</strong>
          <span>Current semester count</span>
        </article>

        <article className="metric-card">
          <small>Campaign Progress</small>
          <strong>
            {activeCampaign
              ? `${Math.min(
                  100,
                  Math.round((activeCampaign.raised_amount / Math.max(activeCampaign.target_amount, 1)) * 100),
                )}%`
              : "0%"}
          </strong>
          <span>{activeCampaign ? activeCampaign.name : "No active campaign"}</span>
        </article>
      </section>

      <section className="atelier-grid-2-1">
        <article className="atelier-card">
          <div className="atelier-card-head">
            <h3>Upcoming Events</h3>
          </div>
          {events.length === 0 ? (
            <p className="atelier-empty">No events available yet.</p>
          ) : (
            <div className="event-list">
              {events.slice(0, 4).map((event) => (
                <div key={event.id} className="event-item">
                  <div>
                    <h4>{event.title}</h4>
                    <p>{event.venue || "Venue TBD"}</p>
                  </div>
                  <div className="event-meta">
                    <span>{event.starts_at}</span>
                    <strong>{event.rsvp_count} RSVPs</strong>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <div className="atelier-column">
          <article className="atelier-card campaign-spotlight">
            <h3>Annual Campaign Snapshot</h3>
            {activeCampaign ? (
              <>
                <p className="campaign-name">{activeCampaign.name}</p>
                <p className="campaign-amount">
                  NGN {activeCampaign.raised_amount.toLocaleString()} / NGN {activeCampaign.target_amount.toLocaleString()}
                </p>
                <div className="campaign-track">
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
            ) : (
              <p className="atelier-empty">No campaign created yet.</p>
            )}
          </article>

          <article className="atelier-card">
            <h3>Pinned Notes</h3>
            <div className="note-list">
              <div className="note-item">
                <strong>Annual Dinner Ticket Push</strong>
                <p>Reminder sent to all levels. Final deadline this Friday.</p>
              </div>
              <div className="note-item">
                <strong>Dues Extension Notice</strong>
                <p>Session dues deadline shifted to accommodate exams.</p>
              </div>
            </div>
          </article>
        </div>
      </section>
    </section>
  );
}
