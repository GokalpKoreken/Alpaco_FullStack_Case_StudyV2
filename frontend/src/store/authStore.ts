import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../lib/api';

interface AuthState {
  token: string | null;
  user: User | null;
  setSession: (token: string, user: User) => void;
  clear: () => void;
}

type SetState<T> = (partial: T | Partial<T> | ((state: T) => T | Partial<T>), replace?: boolean) => void;

export const useAuthStore = create<AuthState>()(
  persist<AuthState>(
    (set: SetState<AuthState>) => ({
      token: null,
      user: null,
  setSession: (token: string, user: User) => set(() => ({ token, user })),
      clear: () => set(() => ({ token: null, user: null }))
    }),
    {
      name: 'dropspot-auth'
    }
  )
);
