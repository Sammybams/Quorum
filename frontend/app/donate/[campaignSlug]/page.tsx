import { apiGet } from "@/lib/api";

type CampaignPublic = {
  name: string;
  slug: string;
  target_amount: number;
  raised_amount: number;
  status: string;
};

export default async function DonatePage({ params }: { params: { campaignSlug: string } }) {
  const campaign = await apiGet<CampaignPublic>(`/public/donate/${params.campaignSlug}`);
  const percent = campaign.target_amount > 0 ? Math.round((campaign.raised_amount / campaign.target_amount) * 100) : 0;

  return (
    <main>
      <div className="hero">
        <h1>{campaign.name}</h1>
        <p>{campaign.raised_amount} / {campaign.target_amount} raised ({percent}%)</p>
      </div>
      <div className="card" style={{ marginTop: 16 }}>
        <h3>Public Donation Flow</h3>
        <p className="muted">Submission UI can be wired next to the backend public donation endpoint.</p>
      </div>
    </main>
  );
}
