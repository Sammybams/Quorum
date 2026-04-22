import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="auth-shell auth-shell-centered">
      <section className="auth-card-compact">
        <div className="auth-brand">
          Quo<span>rum</span>
        </div>

        <h1 className="auth-title">Sign in to your workspace</h1>
        <p className="muted auth-subtitle">Use your account details to continue.</p>

        <form>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input id="email" type="email" placeholder="you@school.edu.ng" autoComplete="email" />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" placeholder="Enter your password" autoComplete="current-password" />
          </div>

          <div className="auth-row">
            <label className="remember-check">
              <input type="checkbox" />
              <span>Remember me</span>
            </label>
            <a href="#" className="auth-link">Forgot password?</a>
          </div>

          <button className="btn btn-primary" style={{ width: "100%", marginTop: 12 }} type="submit">
            Sign in
          </button>
        </form>

        <p className="auth-footnote">
          New to Quorum? <Link href="/register" className="auth-link">Create an account</Link>
        </p>
      </section>
    </main>
  );
}
