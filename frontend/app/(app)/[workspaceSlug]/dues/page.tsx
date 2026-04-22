import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type DuesCycle = { id: number; name: string; amount: number; deadline?: string };

export default async function DuesPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const cycles = await apiGet<DuesCycle[]>(`/workspaces/${workspace.id}/dues-cycles`);

  return (
    <div className="card">
      <h2>Dues Cycles</h2>
      {cycles.length === 0 ? (
        <p className="muted">No dues cycle yet.</p>
      ) : (
        <ul>
          {cycles.map((cycle) => (
            <li key={cycle.id}>
              {cycle.name} - {cycle.amount} {cycle.deadline ? `(Deadline: ${cycle.deadline})` : ""}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
