import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type DuesCycle = { id: number; name: string; amount: number; deadline?: string };

export default async function DuesPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const cycles = await apiGet<DuesCycle[]>(`/workspaces/${workspace.id}/dues-cycles`);

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Dues</p>
          <h1>Dues cycles</h1>
          <p>{workspace.name}</p>
        </div>
        <button type="button" className="btn-primary">
          <span className="material-symbols-outlined" aria-hidden="true">
            add
          </span>
          New Cycle
        </button>
      </header>

      <article className="panel-card">
        {cycles.length === 0 ? (
          <div className="empty-state">
            <span className="material-symbols-outlined" aria-hidden="true">
              receipt_long
            </span>
            <h2>No dues cycle yet</h2>
            <p>Create a cycle before collecting or tracking member dues.</p>
          </div>
        ) : (
          <div className="mini-list roomy">
            {cycles.map((cycle) => (
              <div key={cycle.id}>
                <span>{cycle.name}</span>
                <strong>
                  NGN {cycle.amount.toLocaleString()} {cycle.deadline ? `· ${cycle.deadline}` : ""}
                </strong>
              </div>
            ))}
          </div>
        )}
      </article>
    </section>
  );
}
