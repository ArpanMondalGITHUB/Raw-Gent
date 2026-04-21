# Deployment Guide

This repo supports one deployment shape in two environments:

- Local Docker on a single origin at `http://localhost`
- Production Docker on a single origin at `https://<APP_DOMAIN>`

In both cases, the reverse proxy is the only public entrypoint. The frontend and backend are served behind the same origin, so the browser talks to:

- UI: `/`
- API: `/agent/*`, `/auth/*`, `/webhook`, `/login`, `/callback`, and related backend routes
- WebSocket: `/ws/status/{job_id}`

## Prerequisites

### Required for local Docker

- Docker Desktop or Docker Engine with Docker Compose v2
- Ports `80` and `6379` available on your machine
- A GitHub OAuth App with its client ID and client secret
- A GitHub App with:
  - App ID
  - Client ID
  - Client secret
  - Private key PEM file
- At least one model/runtime option configured:
  - `GEMINI_API_KEY` for the local `job_runner` container

### Additional requirements for production

- A public domain pointed at the Docker host
- Ports `80` and `443` open to the internet
- An email address for Let's Encrypt certificate issuance via Caddy
- If using `JOB_RUNNER_MODE=cloud_run`:
  - A Google Cloud project
  - A deployed Cloud Run Job
  - `GCP_PROJECT_ID`, `GCP_REGION`, and `CLOUD_RUN_JOB`
  - Credentials available through `GOOGLE_CLOUD_KEY_JSON` or the host's default credentials

## Local Docker

### 1. Prepare environment variables

Copy the local example file:

```bash
cp .env.docker.example .env
```

Fill in these values in `.env`:

- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_CALLBACK_URL`
- `GITHUB_APP_ID`
- `GITHUB_APP_CLIENT_ID`
- `GITHUB_APP_CLIENT_SECRET`
- `GEMINI_API_KEY`

These values are already correct for the default local single-origin setup unless you intentionally change the port or hostname:

- `FRONTEND_URL=http://localhost`
- `BACKEND_URL=http://localhost`
- `CORS_ORIGINS=http://localhost`
- `GITHUB_CALLBACK_URL=http://localhost/auth/callback`
- `JOB_RUNNER_MODE=docker`
- `REDIS_URL=redis://redis:6379/0`

### 2. Mount the GitHub App private key

By default, Docker Compose mounts:

- Host path: `./private-key.pem`
- Container path: `/run/secrets/github_app_private_key`

If your PEM file lives elsewhere, update:

- `GITHUB_PRIVATE_KEY_HOST_FILE`

You usually do not need to change:

- `GITHUB_PRIVATE_KEY_PATH=/run/secrets/github_app_private_key`

### 3. Start the stack

```bash
docker compose --env-file .env up --build
```

### 4. Expected local URLs

After startup, these are the URLs you should use:

- App: `http://localhost`
- Login redirect start: `http://localhost/login`
- GitHub OAuth callback: `http://localhost/auth/callback`
- GitHub App callback/setup URL: `http://localhost/callback`
- WebSocket status stream: `ws://localhost/ws/status/{job_id}`
- Redis from host: `redis://localhost:6379/0`

Notes:

- The backend is not exposed directly on a separate host port. Requests go through Caddy on `http://localhost`.
- The frontend runtime falls back to the current browser origin, so leaving `VITE_API_URL`, `VITE_WS_URL`, and `VITE_LOGIN_URL` blank is fine for this single-origin setup.
- Local cookies default to `COOKIE_SECURE=false`, which is correct for plain HTTP on `localhost`.

## Production Docker

### 1. Prepare the production environment file

Copy the production example:

```bash
cp .env.production.example .env.production
```

Update these required values:

- `APP_DOMAIN`
- `ACME_EMAIL`
- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_APP_ID`
- `GITHUB_APP_CLIENT_ID`
- `GITHUB_APP_CLIENT_SECRET`
- One of:
  - `GEMINI_API_KEY` with `JOB_RUNNER_MODE=docker`
  - Cloud Run settings with `JOB_RUNNER_MODE=cloud_run`

For the default single-origin production setup, keep these aligned to the same public domain:

- `FRONTEND_URL=https://<APP_DOMAIN>`
- `BACKEND_URL=https://<APP_DOMAIN>`
- `CORS_ORIGINS=https://<APP_DOMAIN>`
- `GITHUB_CALLBACK_URL=https://<APP_DOMAIN>/auth/callback`

### 2. Mount the production GitHub App private key

The production example expects:

- Host path: `./backend/private-key.pem`
- Container path: `/run/secrets/github_app_private_key`

If your PEM file is stored elsewhere on the host, update:

- `GITHUB_PRIVATE_KEY_HOST_FILE`

### 3. Choose a job runner mode

#### Option A: Local container worker

Use this if the Docker host should run jobs itself:

- Set `JOB_RUNNER_MODE=docker`
- Set `GEMINI_API_KEY`

In this mode, the `job_runner` service consumes jobs from Redis inside the same Docker stack.

#### Option B: Cloud Run worker

Use this if job execution should happen in Google Cloud:

- Set `JOB_RUNNER_MODE=cloud_run`
- Set `GCP_PROJECT_ID`
- Set `GCP_REGION`
- Set `CLOUD_RUN_JOB`
- Set `GOOGLE_CLOUD_KEY_JSON` if the host does not already have working Google Cloud credentials

In this mode, the backend triggers the configured Cloud Run Job instead of enqueuing work for the local Docker worker.

### 4. DNS and GitHub configuration

Before starting the production stack:

- Point `APP_DOMAIN` to the Docker host
- Make sure ports `80` and `443` are reachable from the internet
- Set the GitHub OAuth callback URL to `https://<APP_DOMAIN>/auth/callback`
- Set the GitHub App callback/setup URL to `https://<APP_DOMAIN>/callback`
- If your GitHub App has a homepage URL, set it to `https://<APP_DOMAIN>/`

### 5. Start the production stack

```bash
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### 6. Expected production URLs

After DNS is live and Caddy has issued TLS certificates, these are the public URLs:

- App: `https://<APP_DOMAIN>`
- Login redirect start: `https://<APP_DOMAIN>/login`
- GitHub OAuth callback: `https://<APP_DOMAIN>/auth/callback`
- GitHub App callback/setup URL: `https://<APP_DOMAIN>/callback`
- WebSocket status stream: `wss://<APP_DOMAIN>/ws/status/{job_id}`

Notes:

- The production proxy terminates TLS and serves both frontend and backend on the same origin.
- `COOKIE_SECURE=true` and `COOKIE_SAMESITE=lax` are the correct defaults for this setup.
- `VITE_API_URL`, `VITE_WS_URL`, and `VITE_LOGIN_URL` can stay blank in single-origin production because the frontend resolves them from `window.location.origin`.

## Common Commands

Start local:

```bash
docker compose --env-file .env up --build
```

Start production:

```bash
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

Stop the stack:

```bash
docker compose down
```

Stop the production stack:

```bash
docker compose --env-file .env.production -f docker-compose.yml -f docker-compose.prod.yml down
```

Follow logs:

```bash
docker compose logs -f
```

## Troubleshooting

### Backend keeps restarting

If `backend` enters a restart loop, check:

- Missing or invalid GitHub credentials
- Missing GitHub App PEM mount
- Missing Redis connection
- Python import errors in the backend container

### GitHub login succeeds but cookies do not stick

Check:

- `FRONTEND_URL`, `BACKEND_URL`, and `CORS_ORIGINS` all point to the same public origin
- `COOKIE_SECURE=false` only for local HTTP
- `COOKIE_SECURE=true` in production HTTPS
- `COOKIE_SAMESITE=lax` for the current single-origin deployment

### WebSocket does not connect

Use the origin-appropriate path:

- Local: `ws://localhost/ws/status/{job_id}`
- Production: `wss://<APP_DOMAIN>/ws/status/{job_id}`

Because the proxy handles both app traffic and WebSocket upgrades, you should connect through the public origin rather than directly to the backend container.
