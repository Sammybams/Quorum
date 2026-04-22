import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type ShortLink = { id: number; slug: string; destination_url: string; click_count: number; is_active: boolean };

export default async function LinksPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const links = await apiGet<ShortLink[]>(`/workspaces/${workspace.id}/links`);

  return (
    <div className="card">
      <h2>Smart Links</h2>
      <table className="table">
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
              <td>{link.is_active ? "Active" : "Disabled"}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {links.length === 0 && <p className="muted">No links yet.</p>}
    </div>
  );
}
