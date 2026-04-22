import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type ShortLink = { id: number; slug: string; destination_url: string; click_count: number; is_active: boolean };

export default async function LinksPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const links = await apiGet<ShortLink[]>(`/workspaces/${workspace.id}/links`);

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Smart links</p>
          <h1>Trackable redirects</h1>
          <p>{workspace.name}</p>
        </div>
        <button type="button" className="btn-primary">
          <span className="material-symbols-outlined" aria-hidden="true">
            add_link
          </span>
          New Link
        </button>
      </header>

      <section className="panel-card">
        {links.length === 0 ? (
          <div className="empty-state">
            <span className="material-symbols-outlined" aria-hidden="true">
              link_off
            </span>
            <h2>No links yet</h2>
            <p>Create public short links for events, campaigns, forms, and announcements.</p>
          </div>
        ) : (
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Slug</th>
                  <th>Destination</th>
                  <th>Clicks</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {links.map((link) => (
                  <tr key={link.id}>
                    <td>/r/{link.slug}</td>
                    <td>{link.destination_url}</td>
                    <td>{link.click_count}</td>
                    <td>
                      <span className={`status-pill ${link.is_active ? "ok" : "pending"}`}>
                        {link.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}
