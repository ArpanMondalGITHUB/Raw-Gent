import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
  post: vi.fn(),
}));

vi.mock('../../services/api', () => ({
  default: mocks,
}));

import agentApi from '../../services/run_agent';

beforeEach(() => {
  mocks.get.mockReset();
  mocks.post.mockReset();
});

describe('run_agent service', () => {
  it('posts run-agent requests', async () => {
    const request = {
      prompt: 'Fix tests',
      repo_name: 'owner/repo',
      installation_id: 42,
      branches: 'main',
    };
    mocks.post.mockResolvedValueOnce({ data: { job_id: 'job-1', status: 'queued' } });

    await expect(agentApi.runAgent(request)).resolves.toEqual({ job_id: 'job-1', status: 'queued' });
    expect(mocks.post).toHaveBeenCalledWith('/agent/run', request);
  });

  it('gets job status by id', async () => {
    const status = {
      job_id: 'job-1',
      status: 'running',
      messages: [],
      file_changes: [],
      created_at: '2026-04-26T10:00:00.000Z',
    };
    mocks.get.mockResolvedValueOnce({ data: status });

    await expect(agentApi.getJobStatus('job-1')).resolves.toEqual(status);
    expect(mocks.get).toHaveBeenCalledWith('/agent/status/job-1');
  });
});
