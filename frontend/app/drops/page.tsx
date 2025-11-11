import Link from 'next/link';
import { DropList } from '../../src/components/DropList';

export default function DropsPage() {
  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div>
          <h1>Active drops</h1>
          <p style={{ color: '#94a3b8' }}>Join waitlists and be ready when the claim window opens.</p>
        </div>
        <Link href="/" className="button-outline">
          ← Back to landing
        </Link>
      </div>
      <DropList />
    </div>
  );
}
