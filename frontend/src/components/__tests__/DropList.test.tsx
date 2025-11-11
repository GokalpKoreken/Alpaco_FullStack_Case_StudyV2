import '@testing-library/jest-dom';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { DropList } from '../DropList';
import { useAuthStore } from '../../store/authStore';

jest.mock('../../lib/api', () => ({
  authApi: {},
  dropApi: {
    list: jest.fn().mockResolvedValue([]),
    join: jest.fn().mockResolvedValue({ status: 'joined', already_joined: false }),
    leave: jest.fn().mockResolvedValue({ status: 'left', already_joined: false }),
    claim: jest.fn().mockResolvedValue({ claim_code: 'CODE123', claimed_at: new Date().toISOString() })
  }
}));

const { dropApi } = jest.requireMock('../../lib/api');

describe('DropList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({ token: 'token-abc', user: { id: '1', email: 'user@example.com', is_admin: false, created_at: new Date().toISOString() }, setSession: useAuthStore.getState().setSession, clear: useAuthStore.getState().clear });
  });

  it('shows empty state when no drops', async () => {
    (dropApi.list as jest.Mock).mockResolvedValueOnce([]);

    render(<DropList />);

    await waitFor(() => expect(screen.getByText(/No active drops/i)).toBeInTheDocument());
  });

  it('joins a drop', async () => {
    const drop = {
      id: 'drop-1',
      title: 'Limited Poster',
      description: 'Test drop',
      stock: 5,
      waitlist_open_at: new Date().toISOString(),
      claim_open_at: new Date(Date.now() - 1000).toISOString(),
      claim_close_at: new Date(Date.now() + 3600_000).toISOString(),
      base_priority: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    (dropApi.list as jest.Mock).mockResolvedValueOnce([drop]);

    render(<DropList />);

    await waitFor(() => expect(screen.getByText(drop.title)).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /Join waitlist/i }));

    expect(dropApi.join).toHaveBeenCalledWith(drop.id, 'token-abc');
  });
});
