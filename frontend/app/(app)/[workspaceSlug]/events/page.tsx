import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Event = { id: number; title: string; event_type: string; starts_at: string; venue?: string };

export default async function EventsPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const events = await apiGet<Event[]>(`/workspaces/${workspace.id}/events`);

  return (
    <section className="atelier-stack">
      <header className="atelier-pagehead row">
        <div>
          <small>Events</small>
          <h1>Events Calendar</h1>
          <p>{workspace.name}</p>
        </div>
      </header>

      <article className="atelier-card">
        {events.length === 0 ? (
          <p className="atelier-empty">No events created yet.</p>
        ) : (
          <div className="event-list">
            {events.map((event) => (
              <div key={event.id} className="event-item">
                <div>
                  <h4>{event.title}</h4>
                  <p>{event.event_type}</p>
                </div>
                <div className="event-meta">
                  <span>{event.starts_at}</span>
                  <strong>{event.venue || "Venue TBD"}</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
