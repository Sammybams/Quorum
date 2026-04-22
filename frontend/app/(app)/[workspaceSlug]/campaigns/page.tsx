import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Campaign = { id: number; name: string; slug: string; target_amount: number; raised_amount: number; status: string };

export default async function CampaignsPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const campaigns = await apiGet<Campaign[]>(`/workspaces/${workspace.id}/campaigns`);
  const campaign = campaigns.find((item) => item.status === "active") || campaigns[0] || null;
  const progress = campaign
    ? Math.min(100, Math.round((campaign.raised_amount / Math.max(campaign.target_amount, 1)) * 100))
    : 0;

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Fundraising</p>
          <h1>{campaign ? campaign.name : "Campaigns"}</h1>
          <p>{workspace.name}</p>
        </div>
        <button type="button" className="btn-primary">
          <span className="material-symbols-outlined" aria-hidden="true">
            add
          </span>
          New Campaign
        </button>
      </header>

      {campaign ? (
        <>
          <section className="fund-grid">
            <article className="fund-hero">
              <div>
                <p className="eyebrow">Raised so far</p>
                <strong>NGN {campaign.raised_amount.toLocaleString()}</strong>
              </div>
              <div>
                <p>{progress}% of NGN {campaign.target_amount.toLocaleString()}</p>
                <div className="progress-track">
                  <span style={{ width: `${progress}%` }} />
                </div>
              </div>
            </article>

            <article className="panel-card">
              <h2>Campaign status</h2>
              <div className="mini-list">
                <div>
                  <span>Status</span>
                  <strong>{campaign.status}</strong>
                </div>
                <div>
                  <span>Public slug</span>
                  <strong>{campaign.slug}</strong>
                </div>
              </div>
            </article>
          </section>

          <article className="panel-card">
            <div className="empty-block">
              <span className="material-symbols-outlined" aria-hidden="true">
                receipt_long
              </span>
              <h3>No contribution ledger yet</h3>
              <p>Verified donations and receipt activity will appear here once contributions are recorded.</p>
            </div>
          </article>
        </>
      ) : (
        <article className="panel-card">
          <div className="empty-state">
            <span className="material-symbols-outlined" aria-hidden="true">
              payments
            </span>
            <h2>No campaigns yet</h2>
            <p>Create a fundraising campaign when your student body is ready to receive contributions.</p>
          </div>
        </article>
      )}
    </section>
  );
}
