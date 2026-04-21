const trimTrailingSlash = (value: string) => value.replace(/\/+$/, "");

const getBrowserOrigin = () => {
  if (typeof window === "undefined") {
    return "";
  }

  return window.location.origin;
};

const normalizeEnvValue = (value: string | undefined) => {
  const trimmed = value?.trim();
  return trimmed ? trimTrailingSlash(trimmed) : "";
};

const originToWebSocketOrigin = (origin: string) =>
  origin.replace(/^http/i, (protocol) =>
    protocol.toLowerCase() === "https" ? "wss" : "ws",
  );

const browserOrigin = getBrowserOrigin();

const getOrigin = (value: string) => {
  try {
    return new URL(value, browserOrigin || undefined).origin;
  } catch {
    return value.startsWith("/") ? browserOrigin : value;
  }
};

export const API_BASE_URL =
  normalizeEnvValue(import.meta.env.VITE_API_URL) || browserOrigin;

const siteOrigin = API_BASE_URL ? getOrigin(API_BASE_URL) : browserOrigin;

export const LOGIN_URL =
  normalizeEnvValue(import.meta.env.VITE_LOGIN_URL) ||
  `${siteOrigin}/login`;

export const WS_BASE_URL =
  normalizeEnvValue(import.meta.env.VITE_WS_URL) ||
  originToWebSocketOrigin(siteOrigin);

export const GITHUB_APP_INSTALL_URL =
  normalizeEnvValue(import.meta.env.VITE_GITHUB_APP_INSTALL_URL) ||
  "https://github.com/apps/raw-gent/installations/new";
