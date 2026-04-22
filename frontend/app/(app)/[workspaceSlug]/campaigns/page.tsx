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
    <section className="atelier-stack">
      <header className="atelier-pagehead row">
        <div>
          <small>Fundraising Campaign</small>
          <h1>{campaign ? campaign.name : "No active campaign"}</h1>
          <p>{workspace.name}</p>
        </div>
      </header>

      {campaign ? (
        <>
          <section className="fund-grid">
            <article className="fund-hero">
              <div className="fund-hero-head">
                <div>
                  <small>Raised so far</small>
                  <strong>NGN {campaign.raised_amount.toLocaleString()}</strong>
                </div>
                <div>
                  <small>Target</small>
                  <strong>NGN {campaign.target_amount.toLocaleString()}</strong>
                </div>
              </div>
              <p>{progress}% of goal reached</p>
              <div className="campaign-track">
                <span style={{ width: `${progress}%` }} />
              </div>
            </article>

            <article className="atelier-card">
              <h3>Funding Streams</h3>
              <div className="stream-list">
                <div>
                  <span>Sponsorships</span>
                  <strong>60%</strong>
                </div>
                <div>
                  <span>Donations</span>
                  <strong>25%</strong>
                </div>
                <div>
                  <span>Tickets</span>
                  <strong>15%</strong>
                </div>
              </div>
            </article>
          </section>

          <section className="fund-grid two">
            <article className="atelier-card">
              <div className="atelier-card-head">
                <h3>AI Receipt Queue</h3>
                <small>Pending Verification (3)</small>
              </div>
              <div className="queue-list">
                <div className="queue-item">
                  <div>
                    <strong>Amara Obi</strong>
                    <p>NGN 5,000 - AI verified</p>
                  </div>
                  <div className="queue-actions">
                    <button type="button">Review</button>
                    <button type="button">Confirm</button>
                  </div>
                </div>
                <div className="queue-item warn">
                  <div>
                    <strong>Bayo Adesanya</strong>
                    <p>Mismatch: claimed 10,000 vs AI read 5,000</p>
                  </div>
                  <div className="queue-actions">
                    <button type="button">Inspect</button>
                    <button type="button">Flag</button>
                  </div>
                </div>
              </div>
            </article>

            <article className="atelier-card">
              <div className="atelier-card-head">
                <h3>Recent Ledger</h3>
              </div>
              <div className="ledger-list">
                <div>
                  <span>Seun Adeyemi</span>
                  <strong>NGN 25,000</strong>
                </div>
                <div>
                  <span>Class of 300L</span>
                  <strong>NGN 18,500</strong>
                </div>
                <div>
                  <span>Ticket Sales</span>
                  <strong>NGN 42,000</strong>
                </div>
              </div>
            </article>
          </section>
        </>
      ) : (
        <article className="atelier-card">
          <h3>No campaigns found</h3>
          <p className="atelier-empty">Create one from the sidebar button to populate this dashboard.</p>
        </article>
      )}
    </section>
  );
}
