import '@testing-library/jest-dom';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { AuthPanel } from '../AuthPanel';
import { useAuthStore } from '../../store/authStore';

const pushMock = jest.fn();

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: pushMock })
}));

jest.mock('../../lib/api', () => ({
  authApi: {
    signup: jest.fn().mockResolvedValue({ id: '1', email: 'test@example.com', is_admin: false, created_at: new Date().toISOString() }),
    login: jest.fn().mockResolvedValue('token-123'),
    currentUser: jest.fn().mockResolvedValue({ id: '1', email: 'test@example.com', is_admin: false, created_at: new Date().toISOString() })
  },
  dropApi: {}
}));

const { authApi } = jest.requireMock('../../lib/api');

describe('AuthPanel', () => {
  beforeEach(() => {
    pushMock.mockReset();
    const { setSession, clear } = useAuthStore.getState();
    useAuthStore.setState({ token: null, user: null, setSession, clear });
    jest.clearAllMocks();
  });

  it('renders sign-in form copy', () => {
    render(<AuthPanel mode="signin" />);
    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    expect(screen.getByText(/Need an account/i)).toBeInTheDocument();
  });

  it('performs signup then redirects', async () => {
    authApi.currentUser.mockResolvedValueOnce({
      id: '1',
      email: 'new@example.com',
      is_admin: false,
      created_at: new Date().toISOString()
    });

    render(<AuthPanel mode="signup" />);

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'new@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'NewPass123!' } });
    fireEvent.click(screen.getByRole('button', { name: /Sign up/i }));

    await waitFor(() => expect(authApi.signup).toHaveBeenCalledWith({ email: 'new@example.com', password: 'NewPass123!', is_admin: false }));
    await waitFor(() => expect(authApi.login).toHaveBeenCalledWith({ email: 'new@example.com', password: 'NewPass123!' }));
    await waitFor(() => expect(pushMock).toHaveBeenCalledWith('/drops'));
    expect(useAuthStore.getState().token).toEqual('token-123');
    expect(screen.getByText(/Welcome back, new@example.com/i)).toBeInTheDocument();
  });

  it('signs in without calling signup', async () => {
    render(<AuthPanel mode="signin" />);

    fireEvent.change(screen.getByLabelText(/Email/i), { target: { value: 'user@example.com' } });
    fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'Secret123!' } });
    fireEvent.click(screen.getByRole('button', { name: /Sign in/i }));

    await waitFor(() => expect(authApi.signup).not.toHaveBeenCalled());
    await waitFor(() => expect(authApi.login).toHaveBeenCalledWith({ email: 'user@example.com', password: 'Secret123!' }));
    expect(pushMock).toHaveBeenCalledWith('/drops');
  });
});
