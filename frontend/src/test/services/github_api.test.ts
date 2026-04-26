import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  get: vi.fn(),
}));

vi.mock('../../services/api', () => ({
  default: mocks,
}));

import { fetchInstallRepos, fetchbranch } from '../../services/github_api';

beforeEach(() => {
  mocks.get.mockReset();
});

describe('github_api service', () => {
  it('fetches installed repositories', async () => {
    mocks.get.mockResolvedValueOnce({ data: { repositories: [{ id: 1, name: 'raw-gent' }] } });

    await expect(fetchInstallRepos()).resolves.toEqual({
      repositories: [{ id: 1, name: 'raw-gent' }],
    });
    expect(mocks.get).toHaveBeenCalledWith('/installation-repos');
  });

  it('fetches branches for a repository', async () => {
    mocks.get.mockResolvedValueOnce({ data: { Branches: [{ name: 'main' }] } });

    await expect(fetchbranch('raw-gent')).resolves.toEqual({
      Branches: [{ name: 'main' }],
    });
    expect(mocks.get).toHaveBeenCalledWith('/branches/raw-gent');
  });
});
