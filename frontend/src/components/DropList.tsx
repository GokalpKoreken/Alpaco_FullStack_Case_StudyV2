'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { ClaimResponse, Drop, dropApi } from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface WaitlistState {
  [dropId: string]: {
    already_joined: boolean;
    status: string;
    priority_score?: number;
  };
}

export function DropList() {
  const { token, user } = useAuthStore();
  const [drops, setDrops] = useState<Drop[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [waitlistState, setWaitlistState] = useState<WaitlistState>({});
  const [claim, setClaim] = useState<ClaimResponse | null>(null);

  const fetchDrops = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await dropApi.list(token ?? undefined);
      setDrops(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load drops');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchDrops();
  }, [token]);

  const handleJoin = async (dropId: string) => {
    if (!token) {
      setError('Please sign in first.');
      return;
    }
    try {
      const res = await dropApi.join(dropId, token);
      setWaitlistState((prev: WaitlistState) => ({
        ...prev,
        [dropId]: {
          already_joined: true,
          status: res.status
        }
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Join failed');
    }
  };

  const handleLeave = async (dropId: string) => {
    if (!token) {
      setError('Please sign in first.');
      return;
    }
    try {
      await dropApi.leave(dropId, token);
      setWaitlistState((prev: WaitlistState) => ({
        ...prev,
        [dropId]: {
          already_joined: false,
          status: 'left'
        }
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Leave failed');
    }
  };

  const handleClaim = async (dropId: string) => {
    if (!token) {
      setError('Please sign in first.');
      return;
    }
    try {
      const res = await dropApi.claim(dropId, token);
      setClaim(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Claim failed');
    }
  };

  const now = useMemo(() => new Date(), [drops.length]);

  return (
    <section>
      <header>
        <h1>Active Drops</h1>
        <button onClick={() => void fetchDrops()} disabled={loading}>
          Refresh
        </button>
      </header>
      {error ? <p role="alert" style={{ color: '#f87171' }}>{error}</p> : null}
      {!token ? (
        <p style={{ color: '#94a3b8' }}>
          Please <Link href="/auth/signin">sign in</Link> to join waitlists and claim codes.
        </p>
      ) : (
        <p style={{ color: '#94a3b8' }}>{user ? `Signed in as ${user.email}` : ''}</p>
      )}
      {loading ? <p>Loading...</p> : null}
      {drops.length === 0 && !loading ? <p>No active drops yet. Check back soon.</p> : null}
      {drops.map((drop: Drop) => {
        const joined = waitlistState[drop.id]?.already_joined;
        const claimOpen = new Date(drop.claim_open_at);
        const claimClose = new Date(drop.claim_close_at);
        const windowOpen = now >= claimOpen && now <= claimClose;

        return (
          <article key={drop.id} className="card">
            <h2>{drop.title}</h2>
            <p>{drop.description}</p>
            <p>
              Stock: {drop.stock} · Claim window: {claimOpen.toLocaleString()} → {claimClose.toLocaleString()}
            </p>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              <button onClick={() => void handleJoin(drop.id)} disabled={loading || joined}>
                {joined ? 'Joined' : 'Join waitlist'}
              </button>
              <button onClick={() => void handleLeave(drop.id)} disabled={loading || !joined}>
                Leave waitlist
              </button>
              <button onClick={() => void handleClaim(drop.id)} disabled={loading || !windowOpen}>
                Claim code
              </button>
            </div>
          </article>
        );
      })}
      {claim ? (
        <div className="card" style={{ borderColor: '#34d399' }}>
          <h3>Your claim code</h3>
          <p>{claim.claim_code}</p>
          <small>Generated at {new Date(claim.claimed_at).toLocaleString()}</small>
        </div>
      ) : null}
    </section>
  );
}
