import { afterEach, describe, expect, it, vi } from 'vitest';

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe('api service', () => {
  it('creates an axios client with runtime base URL and JSON credentials config', async () => {
    vi.stubEnv('VITE_API_URL', 'https://api.rawgent.test');
    vi.resetModules();

    const apiClient = (await import('../../services/api')).default;

    expect(apiClient.defaults.baseURL).toBe('https://api.rawgent.test');
    expect(apiClient.defaults.withCredentials).toBe(true);
    expect(apiClient.defaults.headers.common).toBeDefined();
    expect(apiClient.defaults.headers.post?.['Content-Type']).toBeUndefined();
  });
});
