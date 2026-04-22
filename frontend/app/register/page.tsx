import Link from "next/link";

export default function RegisterPage() {
  return (
    <main className="auth-shell">
      <section className="auth-card">
        <aside className="auth-promo">
          <h2 style={{ marginTop: 0 }}>Launch Your Body Workspace</h2>
          <p>
            Setup a dedicated dashboard for your department, faculty, or union with role-based access and public sharing pages.
          </p>
          <div style={{ marginTop: 14, padding: 12, border: "1px solid rgba(255,255,255,0.22)", borderRadius: 12 }}>
            <strong style={{ fontSize: "0.9rem" }}>What you get in v1:</strong>
            <p style={{ marginBottom: 0, marginTop: 6 }}>Dues tracking, meetings, events analytics, campaign progress, and smart links.</p>
          </div>
        </aside>

        <div className="auth-form">
          <h1 style={{ marginTop: 0 }}>Create Account</h1>
          <p className="muted">Step 1 of 2: account + workspace setup</p>

          <div className="field-row">
            <div className="field">
              <label htmlFor="first-name">First name</label>
              <input id="first-name" type="text" placeholder="Samuel" />
            </div>
            <div className="field">
              <label htmlFor="last-name">Last name</label>
              <input id="last-name" type="text" placeholder="Bamgbola" />
            </div>
          </div>

          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" placeholder="you@school.edu.ng" />
          </div>

          <div className="field-row">
            <div className="field">
              <label htmlFor="password">Password</label>
              <input id="password" type="password" placeholder="Create password" />
            </div>
            <div className="field">
              <label htmlFor="role">Role</label>
              <select id="role" defaultValue="exco">
                <option value="exco">Exco Officer</option>
                <option value="member">General Member</option>
              </select>
            </div>
          </div>

          <hr style={{ border: 0, borderTop: "1px solid #e6e9f0", margin: "8px 0 14px" }} />

          <div className="field-row">
            <div className="field">
              <label htmlFor="workspace-name">Workspace name</label>
              <input id="workspace-name" type="text" placeholder="CSC Student Body" />
            </div>
            <div className="field">
              <label htmlFor="workspace-slug">Workspace slug</label>
              <input id="workspace-slug" type="text" placeholder="csc-body" />
            </div>
          </div>

          <button className="btn btn-primary" style={{ width: "100%" }}>
            Create Workspace
          </button>

          <p className="muted" style={{ marginTop: 14 }}>
            Already have an account? <Link href="/login" style={{ color: "#1a56db", fontWeight: 600 }}>Sign in</Link>
          </p>
        </div>
      </section>
    </main>
  );
}
