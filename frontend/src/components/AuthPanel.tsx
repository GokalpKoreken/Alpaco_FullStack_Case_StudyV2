'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';
import type { ChangeEvent } from 'react';
import { authApi } from '../lib/api';
import { useAuthStore } from '../store/authStore';

type AuthMode = 'signin' | 'signup';

interface AuthPanelProps {
  mode: AuthMode;
  heading?: string;
  subheading?: string;
  redirectTo?: string;
  showAdminToggle?: boolean;
}

export function AuthPanel({
  mode,
  heading,
  subheading,
  redirectTo = '/drops',
  showAdminToggle = true,
}: AuthPanelProps) {
  const router = useRouter();
  const { token, user, setSession, clear } = useAuthStore();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const effectiveHeading = heading ?? (mode === 'signin' ? 'Sign in to DropSpot' : 'Create your account');
  const defaultSubheading = mode === 'signin' ? 'Access drops, waitlists, and claim codes.' : 'Join the waitlist community in seconds.';
  const otherMode = mode === 'signin' ? 'signup' : 'signin';
  const otherHref = `/auth/${otherMode}`;

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === 'signup') {
        await authApi.signup({ email, password, is_admin: showAdminToggle ? isAdmin : false });
      }
      const accessToken = await authApi.login({ email, password });
      const profile = await authApi.currentUser(accessToken);
      setSession(accessToken, profile);
      router.push(redirectTo);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error');
    } finally {
      setLoading(false);
    }
  };

  if (token && user) {
    return (
      <div className="card" aria-live="polite">
        <h2>Welcome back, {user.email}</h2>
        <p>Role: {user.is_admin ? 'Admin' : 'Member'}</p>
        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
          <Link href="/drops" className="button-link">
            View drops
          </Link>
          <button onClick={clear}>Log out</button>
        </div>
      </div>
    );
  }

  return (
    <div className="card" aria-live="polite">
      <h1>{effectiveHeading}</h1>
      <p style={{ marginBottom: '1.5rem', color: '#94a3b8' }}>{subheading ?? defaultSubheading}</p>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem' }}>
        <label style={{ display: 'grid', gap: '0.25rem' }}>
          Email
          <input
            type="email"
            value={email}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="you@example.com"
          />
        </label>
        <label style={{ display: 'grid', gap: '0.25rem' }}>
          Password
          <input
            type="password"
            value={password}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            required
            autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
            placeholder="••••••••"
          />
        </label>
        {mode === 'signup' && showAdminToggle ? (
          <label style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <input
              type="checkbox"
              checked={isAdmin}
              onChange={(e: ChangeEvent<HTMLInputElement>) => setIsAdmin(e.target.checked)}
            />
            Create as admin (optional)
          </label>
        ) : null}
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting…' : mode === 'signin' ? 'Sign in' : 'Sign up'}
        </button>
        {error ? <p role="alert" style={{ color: '#f87171' }}>{error}</p> : null}
      </form>
      <p style={{ marginTop: '1rem' }}>
        {mode === 'signin' ? (
          <>
            Need an account? <Link href={otherHref}>Sign up</Link>
          </>
        ) : (
          <>
            Already a member? <Link href={otherHref}>Sign in</Link>
          </>
        )}
      </p>
    </div>
  );
}
