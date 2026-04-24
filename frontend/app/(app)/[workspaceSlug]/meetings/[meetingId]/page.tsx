"use client";

import { FormEvent, useEffect, useState } from "react";

import { apiGet, apiPost } from "@/lib/api";

type Workspace = { id: number; slug: string; name: string };
type Integration = { provider: string; status: string; configured: boolean };
type MeetingDetail = {
  id: number;
  title: string;
  meeting_type: string;
  scheduled_for: string;
  venue?: string | null;
  virtual_link?: string | null;
  agenda: string[];
  transcript?: string | null;
  minutes?: {
    summary?: string | null;
    content?: string | null;
    attendance_summary?: string | null;
    decisions: string[];
    ai_status: string;
    generated_by_model?: string | null;
    generation_error?: string | null;
    published_at?: string | null;
  } | null;
  action_items: Array<{ id: number; description: string; assigned_to_name?: string | null; due_date?: string | null; status: string; generated_by?: string | null }>;
};

export default function MeetingDetailPage({ params }: { params: { workspaceSlug: string; meetingId: string } }) {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [meeting, setMeeting] = useState<MeetingDetail | null>(null);
  const [transcript, setTranscript] = useState("");
  const [googleConnected, setGoogleConnected] = useState(false);
  const [firefliesConfigured, setFirefliesConfigured] = useState(false);
  const [firefliesTranscriptId, setFirefliesTranscriptId] = useState("");
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const found = await apiGet<Workspace>(`/workspaces/slug/${params.workspaceSlug}`);
        setWorkspace(found);
        const [meetingDetail, integrations] = await Promise.all([
          apiGet<MeetingDetail>(`/workspaces/${found.id}/meetings/${params.meetingId}`),
          apiGet<Integration[]>(`/workspaces/${found.id}/integrations`),
        ]);
        setMeeting(meetingDetail);
        setTranscript(meetingDetail.transcript || "");
        setGoogleConnected(integrations.some((item) => item.provider === "google_workspace" && item.status === "connected"));
        setFirefliesConfigured(integrations.some((item) => item.provider === "fireflies" && item.configured));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unable to load meeting.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [params.meetingId, params.workspaceSlug]);

  async function uploadTranscript(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || !meeting) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const updated = await apiPost<MeetingDetail, { transcript: string }>(
        `/workspaces/${workspace.id}/meetings/${meeting.id}/transcript`,
        { transcript },
      );
      setMeeting(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to upload transcript.");
    } finally {
      setWorking(false);
    }
  }

  async function generateMinutes() {
    if (!workspace || !meeting) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const updated = await apiPost<MeetingDetail, Record<string, never>>(
        `/workspaces/${workspace.id}/meetings/${meeting.id}/generate-minutes`,
        {},
      );
      setMeeting(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to generate minutes.");
    } finally {
      setWorking(false);
    }
  }

  async function publishMinutes() {
    if (!workspace || !meeting?.minutes) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const minutes = await apiPost<MeetingDetail["minutes"], Record<string, never>>(
        `/workspaces/${workspace.id}/meetings/${meeting.id}/minutes/publish`,
        {},
      );
      setMeeting((current) => (current ? { ...current, minutes } : current));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to publish minutes.");
    } finally {
      setWorking(false);
    }
  }

  async function attachGoogleMeet() {
    if (!workspace || !meeting) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const updated = await apiPost<{ virtual_link?: string | null }, Record<string, never>>(
        `/workspaces/${workspace.id}/meetings/${meeting.id}/google-meet`,
        {},
      );
      setMeeting((current) => (current ? { ...current, virtual_link: updated.virtual_link || current.virtual_link } : current));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create Google Meet link.");
    } finally {
      setWorking(false);
    }
  }

  async function syncGoogleTranscript() {
    if (!workspace || !meeting) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const updated = await apiPost<MeetingDetail, Record<string, never>>(
        `/workspaces/${workspace.id}/meetings/${meeting.id}/sync-transcript/google`,
        {},
      );
      setMeeting(updated);
      setTranscript(updated.transcript || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sync Google transcript.");
    } finally {
      setWorking(false);
    }
  }

  async function importFirefliesTranscript(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || !meeting || !firefliesTranscriptId.trim()) {
      return;
    }
    setWorking(true);
    setError(null);
    try {
      const updated = await apiPost<MeetingDetail, { transcript_id: string }>(
        `/workspaces/${workspace.id}/meetings/${meeting.id}/sync-transcript/fireflies`,
        { transcript_id: firefliesTranscriptId.trim() },
      );
      setMeeting(updated);
      setTranscript(updated.transcript || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to import Fireflies transcript.");
    } finally {
      setWorking(false);
    }
  }

  if (loading) {
    return <section className="page-stack"><article className="panel-card"><p>Loading meeting...</p></article></section>;
  }

  if (!workspace || !meeting) {
    return <section className="page-stack"><article className="panel-card"><p>{error || "Meeting not found."}</p></article></section>;
  }

  return (
    <section className="page-stack">
      <header className="page-head row">
        <div>
          <p className="eyebrow">Meeting</p>
          <h1>{meeting.title}</h1>
          <p>
            {meeting.scheduled_for}
            {meeting.venue ? ` · ${meeting.venue}` : ""}
          </p>
        </div>
        <div className="page-actions">
          {googleConnected ? (
            <button type="button" className="btn-secondary" onClick={attachGoogleMeet} disabled={working}>
              {meeting.virtual_link ? "Regenerate Meet link" : "Create Google Meet link"}
            </button>
          ) : null}
          {googleConnected && meeting.virtual_link ? (
            <button type="button" className="btn-secondary" onClick={syncGoogleTranscript} disabled={working}>
              {working ? "Working..." : "Sync Google transcript"}
            </button>
          ) : null}
          {meeting.minutes ? (
            <button type="button" className="btn-primary" onClick={publishMinutes} disabled={working}>
              {working ? "Working..." : meeting.minutes.published_at ? "Republish minutes" : "Publish minutes"}
            </button>
          ) : null}
        </div>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <section className="content-grid">
        <article className="panel-card">
          <h2>Agenda</h2>
          {meeting.agenda.length ? (
            <div className="mini-list">
              {meeting.agenda.map((item) => (
                <div key={item}>
                  <span>Agenda</span>
                  <strong>{item}</strong>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted-copy">No agenda items added yet.</p>
          )}
          {meeting.virtual_link ? (
            <div className="mini-list">
              <div>
                <span>Virtual link</span>
                <strong>{meeting.virtual_link}</strong>
              </div>
            </div>
          ) : null}
        </article>

        <article className="panel-card">
          <h2>Minutes</h2>
          {meeting.minutes ? (
            <div className="mini-list">
              <div>
                <span>Status</span>
                <strong>{meeting.minutes.ai_status}</strong>
              </div>
              <div>
                <span>Model</span>
                <strong>{meeting.minutes.generated_by_model || "Manual draft"}</strong>
              </div>
              <div>
                <span>Summary</span>
                <strong>{meeting.minutes.summary || "No summary yet"}</strong>
              </div>
              {meeting.minutes.attendance_summary ? (
                <div>
                  <span>Attendance</span>
                  <strong>{meeting.minutes.attendance_summary}</strong>
                </div>
              ) : null}
              {meeting.minutes.generation_error ? (
                <div>
                  <span>Error</span>
                  <strong>{meeting.minutes.generation_error}</strong>
                </div>
              ) : null}
            </div>
          ) : (
            <p className="muted-copy">Upload a transcript to draft minutes.</p>
          )}
          {meeting.minutes?.decisions?.length ? (
            <div className="mini-list">
              {meeting.minutes.decisions.map((decision, index) => (
                <div key={`${decision}-${index}`}>
                  <span>Decision</span>
                  <strong>{decision}</strong>
                </div>
              ))}
            </div>
          ) : null}
          {meeting.minutes?.content ? <pre className="meeting-minutes-preview">{meeting.minutes.content}</pre> : null}
        </article>
      </section>

      <section className="content-grid">
        <article className="panel-card">
          <div className="card-head compact">
            <h2>Transcript</h2>
            <button type="button" className="btn-secondary" onClick={generateMinutes} disabled={working || !transcript.trim()}>
              {working ? "Working..." : "Regenerate with Claude"}
            </button>
          </div>
          <form className="form-stack" onSubmit={uploadTranscript}>
            <label>
              Paste transcript
              <textarea rows={14} value={transcript} onChange={(event) => setTranscript(event.target.value)} />
            </label>
            <button className="btn-primary" disabled={working || !transcript.trim()} type="submit">
              {working ? "Saving..." : "Save transcript and generate minutes"}
            </button>
          </form>
          {firefliesConfigured ? (
            <form className="form-stack" onSubmit={importFirefliesTranscript}>
              <label>
                Fireflies transcript ID
                <input value={firefliesTranscriptId} onChange={(event) => setFirefliesTranscriptId(event.target.value)} placeholder="Enter transcript id" />
              </label>
              <button className="btn-secondary" disabled={working || !firefliesTranscriptId.trim()} type="submit">
                {working ? "Importing..." : "Import from Fireflies"}
              </button>
            </form>
          ) : null}
        </article>

        <article className="panel-card">
          <h2>Action items</h2>
          {meeting.action_items.length ? (
            <div className="table-wrap">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Assigned</th>
                    <th>Due</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {meeting.action_items.map((item) => (
                    <tr key={item.id}>
                      <td>
                        {item.description}
                        {item.generated_by === "anthropic" ? <div className="muted-copy">Generated by Claude</div> : null}
                      </td>
                      <td>{item.assigned_to_name || "-"}</td>
                      <td>{item.due_date || "-"}</td>
                      <td>{item.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-block">
              <span className="material-symbols-outlined" aria-hidden="true">
                checklist
              </span>
              <h3>No action items yet</h3>
              <p>Save a transcript and Claude will draft action items from the meeting.</p>
            </div>
          )}
        </article>
      </section>
    </section>
  );
}
