"use client";

import { FormEvent, useState } from "react";

import { apiPatch, apiPost } from "@/lib/api";

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

export default function AnnouncementsClient({
  workspace,
  initialAnnouncements,
}: {
  workspace: Workspace;
  initialAnnouncements: Announcement[];
}) {
  const [announcements, setAnnouncements] = useState(initialAnnouncements);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [isPinned, setIsPinned] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function publishAnnouncement(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const announcement = await apiPost<
        Announcement,
        { title: string; body: string; status: string; is_pinned: boolean }
      >(`/workspaces/${workspace.id}/announcements`, {
        title: title.trim(),
        body: body.trim(),
        status: "published",
        is_pinned: isPinned,
      });
      setAnnouncements((current) => [announcement, ...current]);
      setTitle("");
      setBody("");
      setIsPinned(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to publish announcement.");
    } finally {
      setLoading(false);
    }
  }

  async function updateAnnouncement(announcementId: number, payload: Partial<Announcement>) {
    setLoading(true);
    setError(null);

    try {
      const updated = await apiPatch<Announcement, Partial<Announcement>>(
        `/workspaces/${workspace.id}/announcements/${announcementId}`,
        payload,
      );
      setAnnouncements((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to update announcement.");
    } finally {
      setLoading(false);
    }
  }

  const visibleAnnouncements = announcements.filter((announcement) => announcement.status !== "archived");
  const archivedCount = announcements.length - visibleAnnouncements.length;

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Announcements</p>
          <h1>Member updates</h1>
          <p>
            {workspace.name} · {visibleAnnouncements.length} visible · {archivedCount} archived
          </p>
        </div>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <section className="content-grid">
        <article className="panel-card">
          <div className="card-head compact">
            <h2>Published feed</h2>
            <span className="status-pill">{visibleAnnouncements.length} updates</span>
          </div>
          {visibleAnnouncements.length === 0 ? (
            <div className="empty-state">
              <span className="material-symbols-outlined" aria-hidden="true">
                campaign
              </span>
              <h2>No announcements yet</h2>
              <p>Publish a member update and it will appear on the dashboard and public portal.</p>
            </div>
          ) : (
            <div className="activity-list">
              {visibleAnnouncements.map((announcement) => (
                <div key={announcement.id} className="activity-item">
                  <div>
                    <h3>{announcement.title}</h3>
                    <p>{announcement.body}</p>
                  </div>
                  <div className="activity-meta">
                    <span>{announcement.is_pinned ? "Pinned" : announcement.status}</span>
                    <button
                      type="button"
                      className="btn-secondary"
                      disabled={loading}
                      onClick={() =>
                        updateAnnouncement(announcement.id, { is_pinned: !announcement.is_pinned })
                      }
                    >
                      {announcement.is_pinned ? "Unpin" : "Pin"}
                    </button>
                    <button
                      type="button"
                      className="btn-ghost"
                      disabled={loading}
                      onClick={() => updateAnnouncement(announcement.id, { status: "archived" })}
                    >
                      Archive
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <aside className="panel-card">
          <div className="card-head compact">
            <h2>New announcement</h2>
          </div>
          <form className="form-stack" onSubmit={publishAnnouncement}>
            <label>
              Title
              <input value={title} onChange={(event) => setTitle(event.target.value)} required />
            </label>
            <label>
              Body
              <textarea value={body} onChange={(event) => setBody(event.target.value)} required />
            </label>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={isPinned}
                onChange={(event) => setIsPinned(event.target.checked)}
              />
              Pin on dashboard and portal
            </label>
            <button type="submit" className="btn-primary" disabled={loading}>
              Publish
            </button>
          </form>
        </aside>
      </section>
    </section>
  );
}
