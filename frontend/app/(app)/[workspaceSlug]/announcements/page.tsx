import { apiGet } from "@/lib/api";

import AnnouncementsClient from "./announcements-client";

type Workspace = { id: number; slug: string; name: string };
type Announcement = {
  id: number;
  workspace_id: number;
  title: string;
  body: string;
  status: string;
  is_pinned: boolean;
  published_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
};

export default async function AnnouncementsPage({ params }: { params: { workspaceSlug: string } }) {
  const workspace = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
  const announcements = await apiGet<Announcement[]>(`/workspaces/${workspace.id}/announcements`);

  return <AnnouncementsClient workspace={workspace} initialAnnouncements={announcements} />;
}
