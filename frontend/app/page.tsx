import Link from "next/link";

const valueCards = [
  {
    title: "For excos",
    text: "One dashboard to manage dues, events, meetings, campaigns, and member communication.",
  },
  {
    title: "For members",
    text: "Clear visibility into dues status, events, announcements, and fundraising progress.",
  },
  {
    title: "For student bodies",
    text: "A branded portal and short links that instantly upgrade your public presence.",
  },
  {
    title: "For competitions",
    text: "AI receipt verification reduces treasurer workload and increases trust.",
  },
];

export default function HomePage() {
  return (
    <main className="stitch-landing">
      <nav className="stitch-nav">
        <div className="stitch-nav-inner">
          <Link href="/" className="stitch-logo">
            Quorum
          </Link>
          <div className="stitch-links">
            <a href="#features">Features</a>
            <a href="#solutions">Solutions</a>
            <a href="#pricing">Pricing</a>
            <a href="#resources">Resources</a>
          </div>
          <div className="stitch-actions">
            <Link href="/login" className="stitch-login">
              Login
            </Link>
            <Link href="/register" className="stitch-join">
              Join Quorum
            </Link>
          </div>
        </div>
      </nav>

      <header className="stitch-hero" id="features">
        <div>
          <h1>
            Where student bodies <span>get things done.</span>
          </h1>
          <p>
            The premium platform for university leadership governance, seamless verification, and unified
            communication.
          </p>
          <div className="stitch-hero-ctas">
            <Link href="/register" className="stitch-hero-primary">
              Join Quorum
            </Link>
            <a href="#solutions" className="stitch-hero-secondary">
              Book a Demo
            </a>
          </div>
        </div>
        <div className="stitch-hero-art">
          <div className="stitch-hero-preview">
            <h3>Student Ops Overview</h3>
            <p>Unified panel for dues, events, campaigns, and communications.</p>
            <div className="stitch-bars">
              <span style={{ height: "45%" }} />
              <span style={{ height: "63%" }} />
              <span style={{ height: "78%" }} />
              <span style={{ height: "96%" }} />
              <span style={{ height: "70%" }} />
            </div>
            <small>+42% engagement</small>
          </div>
        </div>
      </header>

      <section className="stitch-proof" id="resources">
        <p>Trusted by visionary student leaders across</p>
        <div>
          <span>UNILAG</span>
          <span>OAU</span>
          <span>UI</span>
          <span>ABU</span>
          <span>COVENANT</span>
        </div>
      </section>

      <section className="stitch-values" id="solutions">
        <div className="stitch-intro">
          <h2>
            Designed for impact, not administration.
          </h2>
          <p>
            Step away from spreadsheets. Experience a curated toolkit that treats student management as an art form.
          </p>
        </div>

        <div className="stitch-value-grid">
          {valueCards.map((item) => (
            <article key={item.title} className="stitch-value-card">
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>

        <div className="stitch-bento" id="pricing">
          <article className="stitch-bento-large">
            <h3>AI Receipt Verification</h3>
            <p>Automate financial governance. Scan and validate receipts against expected values instantly.</p>
            <div className="stitch-chip">Receipt #8924 Verified</div>
          </article>

          <article className="stitch-bento-blue">
            <h3>Smart Link Shortener</h3>
            <p>Create custom, trackable links for every initiative.</p>
          </article>

          <article className="stitch-bento-card">
            <h3>Integrated Budgeting</h3>
            <p>Ledger updates connected to campaigns and events in real-time.</p>
          </article>

          <article className="stitch-bento-wide">
            <div>
              <h3>Editorial Analytics</h3>
              <p>See your session story clearly with engagement and participation trends.</p>
            </div>
            <div className="stitch-mini-chart">
              <span style={{ height: "36%" }} />
              <span style={{ height: "56%" }} />
              <span style={{ height: "74%" }} />
              <span style={{ height: "100%" }} />
              <span style={{ height: "68%" }} />
            </div>
          </article>
        </div>
      </section>

      <footer className="stitch-footer">
        <div>
          <strong>Quorum</strong>
          <p>© 2026 Quorum Student Systems. Empowering student leadership.</p>
        </div>
        <div>
          <a href="#">Terms</a>
          <a href="#">Privacy</a>
          <a href="#">Accessibility</a>
          <a href="#">Support</a>
        </div>
      </footer>
    </main>
  );
}
