import Link from "next/link";
import { apiGet } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Campaign = { id: number; name: string; slug: string; target_amount: number; raised_amount: number; status: string };

export default async function CampaignsPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const campaigns = await apiGet<Campaign[]>(`/workspaces/${workspace.id}/campaigns`);

  return (
    <div className="card">
      <h2>Campaigns</h2>
      {campaigns.length === 0 ? (
        <p className="muted">No campaigns yet.</p>
      ) : (
        <ul>
          {campaigns.map((campaign) => (
            <li key={campaign.id} style={{ marginBottom: 8 }}>
              <Link href={`/donate/${campaign.slug}`}>
                {campaign.name} - {campaign.raised_amount}/{campaign.target_amount} ({campaign.status})
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
