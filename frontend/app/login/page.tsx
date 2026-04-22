"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { apiPost } from "@/lib/api";

type LoginResponse = {
  workspace_slug: string;
  workspace_name: string;
  member_id: number;
  member_name: string;
  member_role: string;
};

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
      const result = await apiPost<LoginResponse, { workspace_slug: string; email: string; password: string }>(
        "/auth/login",
        {
          workspace_slug: workspaceSlug.trim(),
          email: email.trim().toLowerCase(),
          password,
        },
      );

      router.push(`/${result.workspace_slug}/dashboard`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-split-shell">
      <section className="auth-split-left">
        <div className="auth-overlay" />
        <div className="auth-left-content">
          <Link className="auth-wordmark" href="/">
            Quorum
          </Link>
          <h1>Empowering student leadership through editorial management.</h1>
          <p>The Academic Atelier for modern student organizations.</p>
        </div>
      </section>

      <section className="auth-split-right">
        <div className="auth-panel">
          <h2>Welcome back</h2>
          <p>Please enter your details to sign in.</p>

          <form onSubmit={onSubmit} className="auth-form-stack">
            <label>
              Workspace slug
              <input
                type="text"
                placeholder="e.g. csc-body"
                value={workspaceSlug}
                onChange={(e) => setWorkspaceSlug(e.target.value)}
                required
              />
            </label>

            <label>
              Email or matric number
              <input
                type="text"
                placeholder="you@school.edu.ng"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </label>

            <label>
              Password
              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </label>

            {error ? <p className="auth-error">{error}</p> : null}

            <button className="auth-primary-btn" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in to Quorum"}
            </button>
          </form>

          <p className="auth-hint">
            New body? <Link href="/register">Create your workspace</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
