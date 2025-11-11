import Link from 'next/link';

export default function HomePage() {
  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <section className="card">
        <h1 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>DropSpot</h1>
        <p style={{ marginBottom: '1.5rem', color: '#94a3b8' }}>
          Claim limited releases fairly. Join waitlists, track priority, and secure your spot when the claim window opens.
        </p>
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link href="/auth/signup" className="button-link">
            Get started
          </Link>
          <Link href="/auth/signin" className="button-outline">
            I already have an account
          </Link>
          <Link href="/drops" className="button-outline">
            View active drops
          </Link>
        </div>
      </section>

      <section className="card">
        <h2>Why DropSpot?</h2>
        <ul style={{ lineHeight: 1.8 }}>
          <li>Transparent priority scores derived from a reproducible project seed.</li>
          <li>Idempotent API for join/leave/claim—no double allocations.</li>
          <li>Real-time claim codes with admin oversight and AI extensions.</li>
        </ul>
      </section>

      <section className="card">
        <h2>Ready to manage drops?</h2>
        <p style={{ marginBottom: '1rem' }}>
          Admins can seed drops, open claim windows, and monitor waitlists from a dedicated console.
        </p>
        <Link href="/admin" className="button-outline">
          Go to admin dashboard
        </Link>
      </section>
    </div>
  );
}
