import Link from "next/link";

const modules = [
  { title: "Dues Tracker", text: "Collect dues, review receipts, and export defaulter reports quickly." },
  { title: "Events & Programs", text: "Create events, track attendance, and publish shareable pages with previews." },
  { title: "Meeting Hub", text: "Send invite links, manage agenda items, and keep structured minutes." },
  { title: "Campaigns", text: "Run fundraising campaigns with live target-vs-raised progress." },
  { title: "Budget Planner", text: "Track planned versus actual spend across categories in one place." },
  { title: "Smart Links + Portal", text: "Host branded links and a public portal for every student body." },
];

export default function HomePage() {
  return (
    <main className="landing-shell">
      <div className="landing-nav">
        <div className="brand">
          Quo<span>rum</span>
        </div>
        <div className="landing-links">
          <Link href="/login" className="btn btn-ghost">
            Sign in
          </Link>
          <Link href="/register" className="btn btn-primary">
            Get started free
          </Link>
        </div>
      </div>

      <section className="hero-card">
        <div>
          <div className="hero-badge">
            <span className="hero-badge-dot" />
            Now live for Nigerian student bodies
          </div>
          <h1 className="hero-title">Run your student body like a team.</h1>
          <p className="hero-sub">
            Quorum is the all-in-one platform for excos: dues collection, events, fundraising campaigns, meeting invites, and member management. One dashboard. Zero WhatsApp chaos.
          </p>
          <div className="hero-actions">
            <Link href="/register" className="btn btn-primary">
              Register your body
            </Link>
            <Link href="/csc-body/dashboard" className="btn btn-ghost">
              View demo dashboard
            </Link>
          </div>
        </div>

        <aside className="hero-panel">
          <h3 style={{ marginTop: 0, fontFamily: "Space Grotesk, sans-serif" }}>Live Snapshot</h3>
          <p className="muted" style={{ color: "rgba(255,255,255,0.75)" }}>
            CSC Department Body · 2024/2025
          </p>
          <div className="hero-kpis">
            <div className="hero-kpi">
              <small>Members</small>
              <br />
              <strong>187</strong>
            </div>
            <div className="hero-kpi">
              <small>Dues Paid</small>
              <br />
              <strong>77%</strong>
            </div>
            <div className="hero-kpi">
              <small>Events</small>
              <br />
              <strong>9</strong>
            </div>
            <div className="hero-kpi">
              <small>Campaign</small>
              <br />
              <strong>63%</strong>
            </div>
          </div>
        </aside>
      </section>

      <section className="stats-strip">
        <div className="stat-card">
          <strong>200+</strong>
          <small className="muted">Student bodies onboarded</small>
        </div>
        <div className="stat-card">
          <strong>₦48M</strong>
          <small className="muted">Dues tracked on Quorum</small>
        </div>
        <div className="stat-card">
          <strong>12K</strong>
          <small className="muted">Active student members</small>
        </div>
        <div className="stat-card">
          <strong>94%</strong>
          <small className="muted">Treasurer time saved</small>
        </div>
      </section>

      <section className="section-panel">
        <h3 className="section-title" style={{ marginTop: 0 }}>Without Quorum vs With Quorum</h3>
        <div className="split">
          <div className="tile">
            <h4>Without Quorum</h4>
            <p className="muted">Dues updates in noisy group chats, manual receipt checks, missing meeting minutes, and no fundraising transparency.</p>
          </div>
          <div className="tile">
            <h4>With Quorum</h4>
            <p className="muted">Live defaulter lists, AI-assisted verification queues, structured meeting archives, and public campaign progress links.</p>
          </div>
        </div>
      </section>

      <section>
        <h3 className="section-title">Core Modules</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          Built around the exact operational pain points your document describes.
        </p>
        <div className="module-grid">
          {modules.map((m) => (
            <div className="module" key={m.title}>
              <h4>{m.title}</h4>
              <p>{m.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section-panel">
        <h3 className="section-title" style={{ marginTop: 0 }}>What excos are saying</h3>
        <div className="quote-grid">
          <article className="quote">
            <p>"AI receipt verification alone saved our treasurer hours every dues cycle."</p>
            <small className="muted">Oluwaseun Adeyemi · CSC President</small>
          </article>
          <article className="quote">
            <p>"Our annual dinner campaign became trackable and transparent in one week."</p>
            <small className="muted">Kemi Adewole · Finance Secretary</small>
          </article>
          <article className="quote">
            <p>"The portal page made us look organized and professional instantly."</p>
            <small className="muted">Chinedu Ezeobi · PRO</small>
          </article>
        </div>
      </section>

      <section className="section-panel">
        <h3 className="section-title" style={{ marginTop: 0 }}>Create your workspace</h3>
        <div className="signup-card">
          <div className="form-grid">
            <div className="form-group">
              <label>First name</label>
              <input type="text" placeholder="Oluwaseun" />
            </div>
            <div className="form-group">
              <label>Last name</label>
              <input type="text" placeholder="Adeyemi" />
            </div>
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" placeholder="seun@school.edu.ng" />
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label>Body type</label>
              <select defaultValue="">
                <option value="" disabled>
                  Select type
                </option>
                <option>Department body</option>
                <option>Faculty body</option>
                <option>Student Union</option>
              </select>
            </div>
            <div className="form-group">
              <label>University</label>
              <input type="text" placeholder="e.g. UNILAG" />
            </div>
          </div>
          <Link href="/register" className="btn btn-primary" style={{ width: "100%" }}>
            Continue to full signup
          </Link>
        </div>
      </section>

      <footer className="footer">
        <span>© 2026 Quorum</span>
        <span>Built for Nigerian student bodies</span>
      </footer>
    </main>
  );
}
