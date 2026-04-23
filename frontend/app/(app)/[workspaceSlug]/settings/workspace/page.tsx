"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import { apiGet, apiPatch } from "@/lib/api";

type Workspace = { id: number; name: string; slug: string; description?: string };

function slugify(value: string) {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

export default function WorkspaceSettingsPage({ params }: { params: { workspaceSlug: string } }) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const found = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
        setWorkspace(found);
        setName(found.name);
        setSlug(found.slug);
        setDescription(found.description || "");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load workspace.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [params.workspaceSlug]);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace) {
      return;
    }

    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const updated = await apiPatch<Workspace, { name: string; slug: string; description?: string }>(
        `/workspaces/${workspace.id}`,
        {
          name,
          slug: slugify(slug),
          description,
        },
      );
      setWorkspace(updated);
      setName(updated.name);
      setSlug(updated.slug);
      setDescription(updated.description || "");
      setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save workspace.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Settings</p>
          <h1>Workspace settings</h1>
          <p>Manage the public identity and URL for this student body.</p>
        </div>
        <Link href={`/${params.workspaceSlug}/settings/roles`} className="btn-secondary">
          Roles & permissions
        </Link>
      </header>

      <section className="content-grid">
        <article className="panel-card">
          <h2>Workspace profile</h2>
          <form className="form-stack" onSubmit={save}>
            <label>
              Workspace name
              <input value={name} onChange={(event) => setName(event.target.value)} required />
            </label>
            <label>
              Workspace slug
              <span className="slug-field">
                <span>quorum.ng/</span>
                <input value={slug} onChange={(event) => setSlug(slugify(event.target.value))} required />
              </span>
            </label>
            <label>
              Portal tagline / description
              <textarea rows={4} value={description} onChange={(event) => setDescription(event.target.value)} />
            </label>
            {error ? <p className="form-error">{error}</p> : null}
            {saved ? <p className="status-note">Workspace settings saved.</p> : null}
            <button type="submit" className="btn-primary" disabled={saving || loading}>
              {saving ? "Saving..." : "Save settings"}
            </button>
          </form>
        </article>

        <article className="panel-card">
          <p className="eyebrow">Public portal</p>
          <h2>{name || "Workspace name"}</h2>
          <p>{description || "Your public portal tagline will appear here."}</p>
          <div className="portal-preview">quorum.ng/{slug || "workspace"}</div>
        </article>
      </section>
    </section>
  );
}
