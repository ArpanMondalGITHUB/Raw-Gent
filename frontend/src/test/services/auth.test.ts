import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../config/runtime', () => ({
  LOGIN_URL: '#github-login',
}));

import { loginWithGitHub } from '../../services/auth';

beforeEach(() => {
  window.history.pushState({}, '', '/home');
});

describe('auth service', () => {
  it('navigates the browser to the GitHub login URL', () => {
    loginWithGitHub();

    expect(window.location.hash).toBe('#github-login');
  });
});
