"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiPost } from "@/lib/api";
import { saveSession, type QuorumSession } from "@/lib/session";

export default function LoginPage() {
  const router = useRouter();
  const [workspaceSlug, setWorkspaceSlug] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
          workspace_slug: workspaceSlug.trim() || undefined,
          email: email.trim().toLowerCase(),
          password,
        },
      );

      saveSession(result);
      router.push(`/${result.workspace_slug}/dashboard`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-screen">
      <section className="auth-visual">
        <Link className="wordmark" href="/">
          Quorum
        </Link>
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
            <h2>Welcome back</h2>
            <p>Sign in with the email attached to your Quorum workspace.</p>
          </div>

          <form onSubmit={onSubmit} className="form-stack">
            <label>
              Workspace slug
              <span className="input-shell">
                <span className="material-symbols-outlined" aria-hidden="true">
                  domain
                </span>
                <input
                  type="text"
                  placeholder="e.g. csc-body"
                  value={workspaceSlug}
                  onChange={(event) => setWorkspaceSlug(event.target.value)}
                  required
                />
              </span>
            </label>

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
                <a href="#" aria-disabled="true">
                  Forgot password?
                </a>
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
              {loading ? "Signing in..." : "Sign in to Quorum"}
            </button>
          </form>

          <p className="auth-footnote">
            New student body? <Link href="/register">Create your workspace</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
