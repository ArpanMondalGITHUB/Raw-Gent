import { afterEach, describe, expect, it, vi } from 'vitest';

const importRuntime = async () => {
  vi.resetModules();
  return import('../config/runtime');
};

afterEach(() => {
  vi.unstubAllEnvs();
  vi.resetModules();
});

describe('runtime config', () => {
  it('uses browser origin when API env is empty', async () => {
    vi.stubEnv('VITE_API_URL', '');
    vi.stubEnv('VITE_WS_URL', '');
    vi.stubEnv('VITE_LOGIN_URL', '');

    const runtime = await importRuntime();

    expect(runtime.API_BASE_URL).toBe('https://rawgent.test');
    expect(runtime.WS_BASE_URL).toBe('wss://rawgent.test');
    expect(runtime.LOGIN_URL).toBe('https://rawgent.test/login');
  });

  it('trims configured URLs and trailing slashes', async () => {
    vi.stubEnv('VITE_API_URL', ' https://api.rawgent.test/// ');
    vi.stubEnv('VITE_WS_URL', ' wss://ws.rawgent.test/// ');
    vi.stubEnv('VITE_LOGIN_URL', ' https://login.rawgent.test/login/// ');

    const runtime = await importRuntime();

    expect(runtime.API_BASE_URL).toBe('https://api.rawgent.test');
    expect(runtime.WS_BASE_URL).toBe('wss://ws.rawgent.test');
    expect(runtime.LOGIN_URL).toBe('https://login.rawgent.test/login');
  });

  it('derives login and websocket URLs from API origin', async () => {
    vi.stubEnv('VITE_API_URL', 'http://localhost:8000/api');
    vi.stubEnv('VITE_WS_URL', '');
    vi.stubEnv('VITE_LOGIN_URL', '');

    const runtime = await importRuntime();

    expect(runtime.LOGIN_URL).toBe('http://localhost:8000/login');
    expect(runtime.WS_BASE_URL).toBe('ws://localhost:8000');
  });

  it('uses the default GitHub app installation URL', async () => {
    vi.stubEnv('VITE_GITHUB_APP_INSTALL_URL', '');

    const runtime = await importRuntime();

    expect(runtime.GITHUB_APP_INSTALL_URL).toBe(
      'https://github.com/apps/raw-gent/installations/new',
    );
  });

  it('uses a configured GitHub app installation URL', async () => {
    vi.stubEnv('VITE_GITHUB_APP_INSTALL_URL', ' https://github.com/apps/test/installations/new/ ');

    const runtime = await importRuntime();

    expect(runtime.GITHUB_APP_INSTALL_URL).toBe(
      'https://github.com/apps/test/installations/new',
    );
  });
});
