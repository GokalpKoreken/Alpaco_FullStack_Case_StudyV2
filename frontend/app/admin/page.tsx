'use client';

import Link from 'next/link';
import { AdminPanel } from '../../src/components/AdminPanel';

export default function AdminPage() {
  return (
    <div>
      <div className="card">
        <Link href="/">← Back to drops</Link>
      </div>
      <AdminPanel />
    </div>
  );
}
