const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export interface User {
  id: string;
  email: string;
  is_admin: boolean;
  created_at: string;
}

export interface Drop {
  id: string;
  title: string;
  description?: string | null;
  stock: number;
  waitlist_open_at: string;
  claim_open_at: string;
  claim_close_at: string;
  base_priority: number;
  created_at: string;
  updated_at: string;
}

export interface ClaimResponse {
  claim_code: string;
  claimed_at: string;
}

export interface JoinResponse {
  status: string;
  already_joined: boolean;
}

async function apiFetch<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || response.statusText);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

export const authApi = {
  signup(body: { email: string; password: string; is_admin?: boolean }) {
    return apiFetch<User>('/auth/signup', { method: 'POST', body: JSON.stringify(body) });
  },
  login(body: { email: string; password: string }) {
    const formData = new URLSearchParams();
    formData.set('username', body.email);
    formData.set('password', body.password);
    return fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData
    })
      .then(async (response) => {
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || response.statusText);
        }
        return response.json() as Promise<{ access_token: string }>;
      })
      .then((data) => data.access_token);
  },
  currentUser(token: string) {
    return apiFetch<User>('/auth/me', {}, token);
  }
};

export const dropApi = {
  list(token?: string) {
    return apiFetch<Drop[]>('/drops', {}, token);
  },
  detail(id: string, token?: string) {
    return apiFetch<Drop>(`/drops/${id}`, {}, token);
  },
  join(id: string, token: string) {
    return apiFetch<JoinResponse>(`/drops/${id}/join`, { method: 'POST' }, token);
  },
  leave(id: string, token: string) {
    return apiFetch<JoinResponse>(`/drops/${id}/leave`, { method: 'POST' }, token);
  },
  claim(id: string, token: string) {
    return apiFetch<ClaimResponse>(`/drops/${id}/claim`, { method: 'POST' }, token);
  },
  adminCreate(payload: Partial<Drop>, token: string) {
    return apiFetch<Drop>('/admin/drops', { method: 'POST', body: JSON.stringify(payload) }, token);
  },
  adminUpdate(id: string, payload: Partial<Drop>, token: string) {
    return apiFetch<Drop>(`/admin/drops/${id}`, { method: 'PUT', body: JSON.stringify(payload) }, token);
  },
  adminDelete(id: string, token: string) {
    return apiFetch<void>(`/admin/drops/${id}`, { method: 'DELETE' }, token);
  }
};
