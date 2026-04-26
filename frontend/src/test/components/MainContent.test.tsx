import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  navigate: vi.fn(),
  fetchInstallRepos: vi.fn(),
  fetchbranch: vi.fn(),
  installGithubApp: vi.fn(),
  runAgent: vi.fn(),
}));

vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal<typeof import('react-router-dom')>();
  return {
    ...actual,
    useNavigate: () => mocks.navigate,
  };
});

vi.mock('../../services/github_api', () => ({
  fetchInstallRepos: mocks.fetchInstallRepos,
  fetchbranch: mocks.fetchbranch,
}));

vi.mock('../../services/github', () => ({
  installGithubApp: mocks.installGithubApp,
}));

vi.mock('../../services/run_agent', () => ({
  default: {
    runAgent: mocks.runAgent,
  },
}));

import { MainContent } from '../../components/MainContent';

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear();
  window.history.pushState({}, '', '/home');
  vi.spyOn(console, 'log').mockImplementation(() => {});
  vi.spyOn(console, 'error').mockImplementation(() => {});
  vi.spyOn(window, 'alert').mockImplementation(() => {});
  mocks.fetchInstallRepos.mockResolvedValue({
    repositories: [
      {
        id: 1,
        name: 'raw-gent',
        full_name: 'arpan/raw-gent',
        installation_id: '88',
      },
    ],
  });
  mocks.fetchbranch.mockResolvedValue({ Branches: [{ name: 'main' }, { name: 'dev' }] });
  mocks.runAgent.mockResolvedValue({ job_id: 'job-1', status: 'queued' });
});

describe('MainContent', () => {
  it('loads repositories and branches on mount', async () => {
    render(<MainContent />);

    expect(await screen.findByText('arpan/raw-gent')).toBeInTheDocument();
    expect(screen.getByDisplayValue('main')).toBeInTheDocument();
    expect(mocks.fetchInstallRepos).toHaveBeenCalledTimes(1);
    expect(mocks.fetchbranch).toHaveBeenCalledWith('raw-gent');
  });

  it('runs the agent and stores current task data', async () => {
    render(<MainContent />);

    await screen.findByText('arpan/raw-gent');
    fireEvent.change(screen.getByPlaceholderText('Help me fix this error ...'), {
      target: { value: 'Fix the failing tests' },
    });
    fireEvent.click(screen.getByRole('button', { name: /give me a plan/i }));

    await waitFor(() => {
      expect(mocks.runAgent).toHaveBeenCalledWith({
        prompt: 'Fix the failing tests',
        repo_name: 'arpan/raw-gent',
        installation_id: 88,
        branches: 'main',
      });
    });

    expect(JSON.parse(sessionStorage.getItem('currentTask') ?? '{}')).toMatchObject({
      job_id: 'job-1',
      prompt: 'Fix the failing tests',
      repo: 'arpan/raw-gent',
      branch: 'main',
      status: 'queued',
    });
    expect(mocks.navigate).toHaveBeenCalledWith('/task', expect.any(Object));
  });

  it('alerts when running without a prompt', async () => {
    render(<MainContent />);

    await screen.findByText('arpan/raw-gent');
    fireEvent.click(screen.getByRole('button', { name: /give me a plan/i }));

    expect(window.alert).toHaveBeenCalledWith('Please enter a prompt');
    expect(mocks.runAgent).not.toHaveBeenCalled();
  });

  it('opens GitHub installation when no repositories are available', async () => {
    mocks.fetchInstallRepos.mockResolvedValueOnce({ repositories: [] });
    render(<MainContent />);

    expect(await screen.findByText('No repositories found')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /no repositories found/i }));

    expect(mocks.installGithubApp).toHaveBeenCalledTimes(1);
  });
});
