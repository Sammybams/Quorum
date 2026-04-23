import { apiGet } from "@/lib/api";

type PortalData = {
  workspace: {
    name: string;
    slug: string;
    description?: string;
  };
  links: Array<{ slug: string; destination_url: string; click_count: number }>;
  events: Array<{ title: string; slug: string; starts_at: string; venue?: string }>;
  announcements: Array<{ title: string; body: string; is_pinned: boolean; published_at?: string | null }>;
};

export default async function PortalPage({ params }: { params: { workspaceSlug: string } }) {
  const data = await apiGet<PortalData>(`/public/portal/${params.workspaceSlug}`);
  const featuredAnnouncement = data.announcements.find((announcement) => announcement.is_pinned) || data.announcements[0];

  return (
    <main className="portal-page">
      <header className="portal-hero">
        <div>
          <p className="eyebrow">Public portal</p>
          <h1>{data.workspace.name}</h1>
          <p>{data.workspace.description || "Links, events, fundraising, and updates from this workspace."}</p>
        </div>
        <span className="portal-badge">{data.workspace.slug}</span>
      </header>

      {featuredAnnouncement ? (
        <section className="portal-feature">
          <span>{featuredAnnouncement.is_pinned ? "Pinned announcement" : "Latest announcement"}</span>
          <h2>{featuredAnnouncement.title}</h2>
          <p>{featuredAnnouncement.body}</p>
        </section>
      ) : null}

      <section className="portal-grid">
        <article className="portal-card">
          <div className="card-head compact">
            <h2>Active links</h2>
            <span>{data.links.length}</span>
          </div>
          {data.links.length ? (
            <div className="portal-list">
              {data.links.map((link) => (
                <a key={link.slug} href={`/r/${link.slug}`}>
                  <span>/{link.slug}</span>
                  <strong>{link.click_count} clicks</strong>
                </a>
              ))}
            </div>
          ) : (
            <p className="portal-empty">No public links have been published yet.</p>
          )}
        </article>

        <article className="portal-card">
          <div className="card-head compact">
            <h2>Upcoming events</h2>
            <span>{data.events.length}</span>
          </div>
          {data.events.length ? (
            <div className="portal-list">
              {data.events.map((event) => (
                <a key={event.slug} href={`/e/${event.slug}`}>
                  <span>{event.title}</span>
                  <strong>{event.starts_at}</strong>
                </a>
              ))}
            </div>
          ) : (
            <p className="portal-empty">No public events are live yet.</p>
          )}
        </article>

        <article className="portal-card">
          <div className="card-head compact">
            <h2>Announcements</h2>
            <span>{data.announcements.length}</span>
          </div>
          {data.announcements.length ? (
            <div className="portal-announcements">
              {data.announcements.map((announcement) => (
                <div key={`${announcement.title}-${announcement.published_at || ""}`}>
                  <strong>{announcement.title}</strong>
                  <p>{announcement.body}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="portal-empty">No announcements have been posted yet.</p>
          )}
        </article>
      </section>
    </main>
  );
}
