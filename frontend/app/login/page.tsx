"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiPost } from "@/lib/api";
import { saveSession, type QuorumSession, type QuorumWorkspace } from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pendingSession, setPendingSession] = useState<QuorumSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await apiPost<QuorumSession, { workspace_slug?: string; email: string; password: string }>(
        "/auth/login",
        {
          email: email.trim().toLowerCase(),
          password,
        },
      );

      if (result.workspace_slug) {
        saveSession(result);
        router.push(`/${result.workspace_slug}/dashboard`);
        return;
      }

      setPendingSession(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  function chooseWorkspace(workspace: QuorumWorkspace) {
    if (!pendingSession) {
      return;
    }
    const session: QuorumSession = {
      ...pendingSession,
      workspace_slug: workspace.workspace_slug,
      workspace_name: workspace.workspace_name,
      member_id: workspace.member_id,
      member_role: workspace.role,
      role_key: workspace.role_key,
    };
    saveSession(session);
    router.push(`/${workspace.workspace_slug}/dashboard`);
  }

  return (
    <main className="auth-screen">
      <section className="auth-visual">
        <Link className="wordmark" href="/">
          <img src="/brand/quorum-wordmark-light.svg" alt="Quorum" />
        </Link>
        <div className="auth-product-preview" aria-hidden="true">
          <div className="auth-preview-topline">
            <span>Sample workspace</span>
            <strong>Preview</strong>
          </div>
          <div className="auth-preview-grid">
            <div>
              <span className="material-symbols-outlined">groups</span>
              <strong>124</strong>
              <small>Members</small>
            </div>
            <div>
              <span className="material-symbols-outlined">receipt_long</span>
              <strong>76%</strong>
              <small>Dues paid</small>
            </div>
            <div>
              <span className="material-symbols-outlined">event</span>
              <strong>4</strong>
              <small>Events</small>
            </div>
          </div>
          <div className="auth-preview-list">
            <div>
              <span></span>
              <p>Event registration</p>
              <strong>Open</strong>
            </div>
            <div>
              <span></span>
              <p>Dues collection</p>
              <strong>Tracking</strong>
            </div>
            <div>
              <span></span>
              <p>Fundraising campaign</p>
              <strong>Active</strong>
            </div>
          </div>
        </div>
        <div className="auth-visual-copy">
          <p className="eyebrow">Student body operations</p>
          <h1>Where student bodies get things done.</h1>
          <p>Coordinate members, events, dues, campaigns, and public links from one considered workspace.</p>
        </div>
      </section>

      <section className="auth-form-area">
        <div className="auth-card">
          <div className="auth-card-head">
            <p className="eyebrow">Secure access</p>
            <h2>{pendingSession ? "Choose a workspace" : "Welcome back"}</h2>
            <p>
              {pendingSession
                ? "Your account belongs to multiple communities. Pick where you want to work."
                : "Sign in once, then choose the workspace you want to manage."}
            </p>
          </div>

          {pendingSession ? (
            <div className="workspace-select-list">
              {pendingSession.workspaces?.map((workspace) => (
                <button
                  key={workspace.workspace_slug}
                  type="button"
                  className="workspace-select-item"
                  onClick={() => chooseWorkspace(workspace)}
                >
                  <span>
                    <strong>{workspace.workspace_name}</strong>
                    <small>{workspace.role}</small>
                  </span>
                  <span className="material-symbols-outlined" aria-hidden="true">
                    arrow_forward
                  </span>
                </button>
              ))}
              <button type="button" className="btn-ghost" onClick={() => setPendingSession(null)}>
                Use a different account
              </button>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="form-stack">
              <label>
                Email or matric number
                <span className="input-shell">
                  <span className="material-symbols-outlined" aria-hidden="true">
                    person
                  </span>
                  <input
                    type="text"
                    placeholder="you@school.edu.ng"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                  />
                </span>
              </label>

              <label>
                <span className="label-row">
                  Password
                  <Link href="/forgot-password">
                    Forgot password?
                  </Link>
                </span>
                <span className="input-shell">
                  <span className="material-symbols-outlined" aria-hidden="true">
                    lock
                  </span>
                  <input
                    type="password"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                  />
                </span>
              </label>

              {error ? <p className="form-error">{error}</p> : null}

              <button className="btn-primary wide" type="submit" disabled={loading}>
                {loading ? "Signing in..." : "Sign in"}
              </button>
            </form>
          )}

          <p className="auth-footnote">
            New student body? <Link href="/register">Create your workspace</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
