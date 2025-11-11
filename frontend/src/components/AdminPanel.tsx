'use client';

import { FormEvent, useEffect, useState } from 'react';
import type { ChangeEvent } from 'react';
import { Drop, dropApi } from '../lib/api';
import { useAuthStore } from '../store/authStore';

interface DraftDrop {
  title: string;
  description: string;
  stock: number;
  waitlist_open_at: string;
  claim_open_at: string;
  claim_close_at: string;
  base_priority: number;
}

const toInputValue = (value: string | Date): string => {
  const date = value instanceof Date ? value : new Date(value);
  return date.toISOString().slice(0, 16);
};

const emptyDraft = (): DraftDrop => {
  const now = new Date();
  return {
    title: '',
    description: '',
    stock: 1,
    waitlist_open_at: toInputValue(new Date(now.getTime() - 60 * 60 * 1000)),
    claim_open_at: toInputValue(now),
    claim_close_at: toInputValue(new Date(now.getTime() + 60 * 60 * 1000)),
    base_priority: 0
  };
};

const draftFromDrop = (drop: Drop): DraftDrop => ({
  title: drop.title,
  description: drop.description ?? '',
  stock: drop.stock,
  waitlist_open_at: toInputValue(drop.waitlist_open_at),
  claim_open_at: toInputValue(drop.claim_open_at),
  claim_close_at: toInputValue(drop.claim_close_at),
  base_priority: drop.base_priority
});

export function AdminPanel() {
  const { token, user } = useAuthStore();
  const [drops, setDrops] = useState<Drop[]>([]);
  const [draft, setDraft] = useState<DraftDrop>(emptyDraft);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadDrops = async () => {
    if (!token) return;
    setLoading(true);
    try {
  const data = await dropApi.list(token);
      setDrops(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load drops');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token && user?.is_admin) {
      void loadDrops();
    }
  }, [token, user?.is_admin]);

  if (!token || !user?.is_admin) {
    return (
      <div className="card" style={{ opacity: 0.6 }}>
        <h2>Admin tools</h2>
        <p>Sign in with an admin account to manage drops.</p>
      </div>
    );
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        ...draft,
        stock: Number(draft.stock),
        base_priority: Number(draft.base_priority),
        waitlist_open_at: new Date(draft.waitlist_open_at).toISOString(),
        claim_open_at: new Date(draft.claim_open_at).toISOString(),
        claim_close_at: new Date(draft.claim_close_at).toISOString()
      };
      if (editingId) {
        const updated = await dropApi.adminUpdate(editingId, payload, token);
        setDrops((prev: Drop[]) => prev.map((drop) => (drop.id === editingId ? updated : drop)));
        setEditingId(null);
      } else {
        const created = await dropApi.adminCreate(payload, token);
        setDrops((prev: Drop[]) => [created, ...prev]);
      }
      setDraft(emptyDraft());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save drop');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this drop?')) return;
    try {
      await dropApi.adminDelete(id, token);
      setDrops((prev: Drop[]) => prev.filter((drop: Drop) => drop.id !== id));
      if (editingId === id) {
        setEditingId(null);
        setDraft(emptyDraft());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete drop');
    }
  };

  const handleEdit = (drop: Drop) => {
    setEditingId(drop.id);
    setDraft(draftFromDrop(drop));
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setDraft(emptyDraft());
  };

  return (
    <section className="card">
      <h2>{editingId ? 'Edit drop' : 'Create drop'}</h2>
      <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '0.75rem' }}>
        <input
          type="text"
          placeholder="Title"
          value={draft.title}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setDraft((prev: DraftDrop) => ({ ...prev, title: e.target.value }))}
          required
        />
        <textarea
          placeholder="Description"
          value={draft.description}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setDraft((prev: DraftDrop) => ({ ...prev, description: e.target.value }))}
          rows={3}
        />
        <input
          type="number"
          min={1}
          value={draft.stock}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setDraft((prev: DraftDrop) => ({ ...prev, stock: Number(e.target.value) }))}
          required
        />
        <label>
          Waitlist opens
          <input
            type="datetime-local"
            value={draft.waitlist_open_at}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setDraft((prev: DraftDrop) => ({ ...prev, waitlist_open_at: e.target.value }))}
            required
          />
        </label>
        <label>
          Claim opens
          <input
            type="datetime-local"
            value={draft.claim_open_at}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setDraft((prev: DraftDrop) => ({ ...prev, claim_open_at: e.target.value }))}
            required
          />
        </label>
        <label>
          Claim closes
          <input
            type="datetime-local"
            value={draft.claim_close_at}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setDraft((prev: DraftDrop) => ({ ...prev, claim_close_at: e.target.value }))}
            required
          />
        </label>
        <label>
          Base priority
          <input
            type="number"
            value={draft.base_priority}
            onChange={(e: ChangeEvent<HTMLInputElement>) => setDraft((prev: DraftDrop) => ({ ...prev, base_priority: Number(e.target.value) }))}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Saving…' : editingId ? 'Update drop' : 'Create drop'}
        </button>
        {editingId ? (
          <button type="button" onClick={handleCancelEdit} disabled={loading}>
            Cancel editing
          </button>
        ) : null}
      </form>
      {error ? <p role="alert" style={{ color: '#f87171' }}>{error}</p> : null}

      <h3 style={{ marginTop: '2rem' }}>Existing drops</h3>
      {drops.length === 0 ? <p>No drops yet.</p> : null}
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {drops.map((drop) => (
          <li key={drop.id} style={{ marginBottom: '1rem', border: editingId === drop.id ? '1px solid #38bdf8' : undefined, borderRadius: editingId === drop.id ? '8px' : undefined, padding: editingId === drop.id ? '0.75rem' : undefined }}>
            <strong>{drop.title}</strong>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button type="button" onClick={() => handleEdit(drop)}>
                Edit
              </button>
              <button type="button" onClick={() => void loadDrops()}>
                Refresh data
              </button>
              <button type="button" onClick={() => handleDelete(drop.id)}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
