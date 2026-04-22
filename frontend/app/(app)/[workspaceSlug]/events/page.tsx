import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Event = { id: number; title: string; event_type: string; starts_at: string; venue?: string };

export default async function EventsPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const events = await apiGet<Event[]>(`/workspaces/${workspace.id}/events`);

  return (
    <div className="card">
      <h2>Events</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Title</th>
            <th>Type</th>
            <th>Starts</th>
            <th>Venue</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={event.id}>
              <td>{event.title}</td>
              <td>{event.event_type}</td>
              <td>{event.starts_at}</td>
              <td>{event.venue || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {events.length === 0 && <p className="muted">No events created yet.</p>}
    </div>
  );
}
