import { redirect } from "next/navigation";
import { apiGet } from "@/lib/api";

type ResolveResponse = {
  destination_url: string;
  click_count: number;
};

export default async function ShortLinkResolverPage({ params }: { params: { slug: string } }) {
  const data = await apiGet<ResolveResponse>(`/public/r/${params.slug}`);
  redirect(data.destination_url);
}
