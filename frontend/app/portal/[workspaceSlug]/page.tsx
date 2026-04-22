import { apiGet } from "@/lib/api";

type PortalData = {
  workspace: {
    name: string;
    slug: string;
    description?: string;
  };
  links: Array<{ slug: string; destination_url: string; click_count: number }>;
  events: Array<{ title: string; slug: string; starts_at: string; venue?: string }>;
};

export default async function PortalPage({ params }: { params: { workspaceSlug: string } }) {
  const data = await apiGet<PortalData>(`/public/portal/${params.workspaceSlug}`);

  return (
    <main>
      <div className="hero">
        <h1>{data.workspace.name}</h1>
        <p>{data.workspace.description || "Student body portal"}</p>
      </div>

      <div className="grid grid-2" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>Active Links</h3>
          <ul>
            {data.links.map((link) => (
              <li key={link.slug}>/r/{link.slug} ({link.click_count} clicks)</li>
            ))}
          </ul>
          {data.links.length === 0 && <p className="muted">No links yet.</p>}
        </div>

        <div className="card">
          <h3>Upcoming Events</h3>
          <ul>
            {data.events.map((event) => (
              <li key={event.slug}>{event.title} - {event.starts_at}</li>
            ))}
          </ul>
          {data.events.length === 0 && <p className="muted">No events yet.</p>}
        </div>
      </div>
    </main>
  );
}
