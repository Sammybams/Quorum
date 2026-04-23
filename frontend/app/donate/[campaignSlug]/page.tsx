import { apiGet } from "@/lib/api";
import { DonationForm } from "./donation-form";

type FundingStream = {
  id: number;
  name: string;
  stream_type: string;
  target_amount: number | null;
  raised_amount: number;
};

type CampaignPublic = {
  name: string;
  slug: string;
  target_amount: number;
  raised_amount: number;
  status: string;
  workspace: { name: string; slug: string };
  funding_streams: FundingStream[];
  contributor_count: number;
};

export default async function DonatePage({ params }: { params: { campaignSlug: string } }) {
  const campaign = await apiGet<CampaignPublic>(`/public/donate/${params.campaignSlug}`);
  const percent = campaign.target_amount > 0 ? Math.round((campaign.raised_amount / campaign.target_amount) * 100) : 0;

  return (
    <main className="donation-page">
      <nav className="donation-nav">
        <img src="/brand/quorum-wordmark-light.svg" alt="Quorum" />
        <span>{campaign.workspace.name}</span>
      </nav>

      <section className="donation-grid">
        <div className="donation-hero">
          <p className="eyebrow">Fundraising campaign</p>
          <h1>{campaign.name}</h1>
          <p>
            Help {campaign.workspace.name} reach its goal. Every contribution is tracked against the public campaign
            ledger.
          </p>

          <div className="donation-progress-card">
            <div>
              <span>Raised</span>
              <strong>NGN {campaign.raised_amount.toLocaleString()}</strong>
            </div>
            <div>
              <span>Target</span>
              <strong>NGN {campaign.target_amount.toLocaleString()}</strong>
            </div>
            <div>
              <span>Contributors</span>
              <strong>{campaign.contributor_count}</strong>
            </div>
            <div className="progress-track">
              <span style={{ width: `${Math.min(percent, 100)}%` }} />
            </div>
            <p>{Math.min(percent, 100)}% funded</p>
          </div>

          {campaign.funding_streams.length ? (
            <div className="stream-list">
              {campaign.funding_streams.map((stream) => {
                const streamTarget = stream.target_amount || campaign.target_amount;
                const streamPercent = Math.min(100, Math.round((stream.raised_amount / Math.max(streamTarget, 1)) * 100));
                return (
                  <article key={stream.id}>
                    <div>
                      <strong>{stream.name}</strong>
                      <span>{stream.stream_type}</span>
                    </div>
                    <p>NGN {stream.raised_amount.toLocaleString()}</p>
                    <div className="progress-track slim">
                      <span style={{ width: `${streamPercent}%` }} />
                    </div>
                  </article>
                );
              })}
            </div>
          ) : null}
        </div>

        <DonationForm campaignSlug={campaign.slug} fundingStreams={campaign.funding_streams} />
      </section>
    </main>
  );
}
