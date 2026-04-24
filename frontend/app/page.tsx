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

const pricingPlans = [
  {
    name: "Starter",
    price: "Free",
    text: "For small student bodies setting up structure, member records, and announcements.",
  },
  {
    name: "Operations",
    price: "Demo-ready",
    text: "Adds dues, events, meetings, campaigns, and public portal workflows in one workspace.",
  },
  {
    name: "Scale",
    price: "Custom",
    text: "For larger unions and umbrella bodies that need integrations, AI workflows, and governance controls.",
  },
];

const resourceCards = [
  {
    title: "Demo workspace setup",
    text: "Create the organisation, connect Google, invite officers, and start from a clean admin workspace.",
  },
  {
    title: "Meetings to minutes",
    text: "Run a meeting, sync or paste a transcript, and publish Claude-generated minutes with action items.",
  },
  {
    title: "Treasury workflows",
    text: "Show dues, campaigns, budget lines, contribution records, and exports in one flow.",
  },
];

export default function HomePage() {
  return (
    <main className="stitch-landing">
      <nav className="stitch-nav">
        <div className="stitch-nav-inner">
          <Link href="/" className="stitch-logo">
            <img src="/brand/quorum-wordmark-light.svg" alt="Quorum" />
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

      <header className="stitch-hero stitch-section" id="features">
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

      <section className="stitch-values stitch-section" id="solutions">
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
      </section>

      <section className="stitch-pricing stitch-section" id="pricing">
        <div className="stitch-intro">
          <h2>Pricing that grows with the body.</h2>
          <p>
            Start clean for a demo, then scale into a full operating system as your leadership processes mature.
          </p>
        </div>
        <div className="stitch-pricing-grid">
          {pricingPlans.map((plan) => (
            <article key={plan.name} className="stitch-pricing-card">
              <p className="eyebrow">{plan.name}</p>
              <h3>{plan.price}</h3>
              <p>{plan.text}</p>
            </article>
          ))}
        </div>

        <div className="stitch-bento">
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

      <section className="stitch-proof stitch-section" id="resources">
        <p>Trusted by visionary student leaders across</p>
        <div>
          <span>UNILAG</span>
          <span>OAU</span>
          <span>UI</span>
          <span>ABU</span>
          <span>COVENANT</span>
        </div>
      </section>

      <section className="stitch-resources stitch-section">
        <div className="stitch-intro">
          <h2>Resources for a strong technical demo.</h2>
          <p>Walk judges through the exact flows that matter: setup, governance, finance, and AI-enabled meetings.</p>
        </div>
        <div className="stitch-resource-grid">
          {resourceCards.map((item) => (
            <article key={item.title} className="stitch-value-card">
              <h3>{item.title}</h3>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <footer className="stitch-footer">
        <div>
          <img className="footer-logo" src="/brand/quorum-wordmark-light.svg" alt="Quorum" />
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
