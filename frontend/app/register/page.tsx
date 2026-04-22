"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useMemo, useState } from "react";

import { apiPost } from "@/lib/api";

type WorkspaceResponse = {
  id: number;
  name: string;
  slug: string;
};

type MemberResponse = {
  id: number;
  workspace_id: number;
};

function slugify(input: string) {
  return input
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .slice(0, 80);
}

export default function RegisterPage() {
  const router = useRouter();

  const [step, setStep] = useState(1);
  const [organizationName, setOrganizationName] = useState("");
  const [university, setUniversity] = useState("");
  const [faculty, setFaculty] = useState("");
  const [adminName, setAdminName] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [role, setRole] = useState("exco");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const workspaceSlug = useMemo(() => slugify(organizationName || university || "workspace"), [organizationName, university]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (step === 1) {
      setStep(2);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const descriptionParts = [university, faculty].filter(Boolean);
      const workspace = await apiPost<WorkspaceResponse, { name: string; slug: string; description?: string }>("/workspaces", {
        name: organizationName,
        slug: workspaceSlug,
        description: descriptionParts.length ? descriptionParts.join(" · ") : undefined,
      });

      await apiPost<MemberResponse, { full_name: string; email: string; role: string; level?: string }>(
        `/workspaces/${workspace.id}/members`,
        {
          full_name: adminName,
          email: adminEmail.trim().toLowerCase(),
          role,
          level: "Admin",
        },
      );

      router.push(`/${workspace.slug}/dashboard`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create workspace.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="signup-shell">
      <header className="signup-head">
        <Link className="auth-wordmark" href="/">
          Quorum
        </Link>
        <span>Need help?</span>
      </header>

      <section className="signup-content">
        <aside className="signup-context">
          <div className="signup-steps">
            <span className={step >= 1 ? "active" : ""}>1 Organization</span>
            <span className={step >= 2 ? "active" : ""}>2 Admin</span>
          </div>
          <h1>Set the stage for your student body.</h1>
          <p>
            Establishing your Quorum workspace takes less than two minutes. Start with organization details,
            then the admin account.
          </p>
        </aside>

        <section className="signup-form-panel">
          <h2>{step === 1 ? "Organization Details" : "Admin Details"}</h2>

          <form onSubmit={onSubmit} className="auth-form-stack">
            {step === 1 ? (
              <>
                <label>
                  Organization name
                  <input
                    type="text"
                    placeholder="e.g. Undergraduate Student Union"
                    value={organizationName}
                    onChange={(e) => setOrganizationName(e.target.value)}
                    required
                  />
                </label>

                <label>
                  University / Institution
                  <input
                    type="text"
                    placeholder="Search for your institution"
                    value={university}
                    onChange={(e) => setUniversity(e.target.value)}
                    required
                  />
                </label>

                <label>
                  Faculty / Department (optional)
                  <input
                    type="text"
                    placeholder="e.g. Faculty of Arts"
                    value={faculty}
                    onChange={(e) => setFaculty(e.target.value)}
                  />
                </label>
              </>
            ) : (
              <>
                <label>
                  Full name
                  <input
                    type="text"
                    placeholder="e.g. Oluwaseun Adeyemi"
                    value={adminName}
                    onChange={(e) => setAdminName(e.target.value)}
                    required
                  />
                </label>

                <label>
                  Email
                  <input
                    type="email"
                    placeholder="you@school.edu.ng"
                    value={adminEmail}
                    onChange={(e) => setAdminEmail(e.target.value)}
                    required
                  />
                </label>

                <label>
                  Role
                  <select value={role} onChange={(e) => setRole(e.target.value)}>
                    <option value="exco">Exco officer</option>
                    <option value="president">President</option>
                    <option value="secretary">Secretary</option>
                  </select>
                </label>

                <label>
                  Password (UI only for now)
                  <input
                    type="password"
                    placeholder="Create password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </label>

                <div className="signup-meta">Workspace slug: {workspaceSlug || "workspace"}</div>
              </>
            )}

            {error ? <p className="auth-error">{error}</p> : null}

            <div className="signup-actions">
              {step === 2 ? (
                <button type="button" className="atelier-btn-ghost" onClick={() => setStep(1)}>
                  Back
                </button>
              ) : (
                <Link href="/" className="atelier-btn-ghost">
                  Cancel setup
                </Link>
              )}

              <button type="submit" className="auth-primary-btn" disabled={loading}>
                {loading ? "Creating workspace..." : step === 1 ? "Continue to Admin" : "Create Workspace"}
              </button>
            </div>
          </form>

          <p className="auth-hint">
            Already have access? <Link href="/login">Sign in</Link>
          </p>
        </section>
      </section>
    </main>
  );
}
