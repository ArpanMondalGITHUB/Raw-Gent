import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../config/runtime', () => ({
  GITHUB_APP_INSTALL_URL: '#install-github-app',
}));

import { installGithubApp } from '../../services/github';

beforeEach(() => {
  window.history.pushState({}, '', '/home');
});

describe('github service', () => {
  it('navigates to the GitHub App installation URL', () => {
    installGithubApp();

    expect(window.location.hash).toBe('#install-github-app');
  });
});
