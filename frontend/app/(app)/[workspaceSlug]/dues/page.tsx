import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type DuesCycle = { id: number; name: string; amount: number; deadline?: string };
type DuesPayment = {
  id: number;
  member_name?: string;
  amount: number;
  method: string;
  status: string;
  created_at: string;
};

export default async function DuesPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const cycles = await apiGet<DuesCycle[]>(`/workspaces/${workspace.id}/dues-cycles`);
  const payments = await apiGet<DuesPayment[]>(`/workspaces/${workspace.id}/dues-payments`);
  const totalPaid = payments
    .filter((payment) => payment.status === "paid")
    .reduce((sum, payment) => sum + payment.amount, 0);

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

      <section className="metrics-grid">
        <article className="metric-card primary">
          <span className="material-symbols-outlined" aria-hidden="true">
            payments
          </span>
          <small>Total collected</small>
          <strong>NGN {totalPaid.toLocaleString()}</strong>
        </article>
        <article className="metric-card">
          <span className="material-symbols-outlined" aria-hidden="true">
            receipt_long
          </span>
          <small>Cycles</small>
          <strong>{cycles.length}</strong>
          <p>Published dues cycles</p>
        </article>
        <article className="metric-card">
          <span className="material-symbols-outlined" aria-hidden="true">
            pending_actions
          </span>
          <small>Pending review</small>
          <strong>{payments.filter((payment) => payment.status === "pending").length}</strong>
          <p>Manual receipts</p>
        </article>
        <article className="metric-card">
          <span className="material-symbols-outlined" aria-hidden="true">
            check_circle
          </span>
          <small>Confirmed</small>
          <strong>{payments.filter((payment) => payment.status === "paid").length}</strong>
          <p>Payments confirmed</p>
        </article>
      </section>

      <section className="content-grid">
        <article className="panel-card">
          <h2>Active cycles</h2>
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

        <article className="panel-card">
          <h2>Payment ledger</h2>
          {payments.length === 0 ? (
            <div className="empty-block">
              <span className="material-symbols-outlined" aria-hidden="true">
                account_balance_wallet
              </span>
              <h3>No payments yet</h3>
              <p>Paystack confirmations and manual receipts will appear here.</p>
            </div>
          ) : (
            <div className="mini-list">
              {payments.slice(0, 8).map((payment) => (
                <div key={payment.id}>
                  <span>{payment.member_name || "Unassigned payment"}</span>
                  <strong>
                    NGN {payment.amount.toLocaleString()} · {payment.status}
                  </strong>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </section>
  );
}
