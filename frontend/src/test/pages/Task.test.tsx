import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  useWebsocket: vi.fn(),
  chatui: vi.fn(),
}));

vi.mock('../../components/AppSidebar', () => ({
  AppSidebar: () => <aside data-testid="app-sidebar">Sidebar</aside>,
}));

vi.mock('../../components/Navbar', () => ({
  Navbar: () => <nav data-testid="navbar">Navbar</nav>,
}));

vi.mock('../../components/Chatui', () => ({
  Chatui: (props: unknown) => {
    mocks.chatui(props);
    return <section data-testid="chatui">Chat UI</section>;
  },
}));

vi.mock('../../hooks/ws_hooks', () => ({
  useWebsocket: mocks.useWebsocket,
}));

import Task from '../../pages/Task';

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear();
  mocks.useWebsocket.mockReturnValue({
    isConnected: false,
    jobStatus: null,
    messages: [],
    onSendMessage: vi.fn(),
  });
});

describe('Task page', () => {
  it('shows a missing job message when no task is stored', () => {
    render(<Task />);

    expect(screen.getByText('No job ID found')).toBeInTheDocument();
    expect(mocks.useWebsocket).toHaveBeenCalledWith(undefined);
    expect(screen.queryByTestId('chatui')).not.toBeInTheDocument();
  });

  it('passes websocket state to Chatui when a stored job exists', () => {
    const onSendMessage = vi.fn();
    const jobStatus = {
      job_id: 'job-1',
      status: 'running',
      messages: [],
      file_changes: [],
      created_at: '2026-04-26T10:00:00.000Z',
    };
    const messages = [{ role: 'agent', content: 'Working', timestamp: '2026-04-26T10:00:00.000Z' }];
    mocks.useWebsocket.mockReturnValueOnce({
      isConnected: true,
      jobStatus,
      messages,
      onSendMessage,
    });
    sessionStorage.setItem('currentTask', JSON.stringify({ job_id: 'job-1' }));

    render(<Task />);

    expect(screen.getByTestId('app-sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('navbar')).toBeInTheDocument();
    expect(screen.getByTestId('chatui')).toBeInTheDocument();
    expect(mocks.useWebsocket).toHaveBeenCalledWith('job-1');
    expect(mocks.chatui).toHaveBeenCalledWith(
      expect.objectContaining({
        jobStatus,
        messages,
        onSendMessage,
        isConnected: true,
      }),
    );
  });
});
