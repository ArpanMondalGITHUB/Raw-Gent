# Contributing to Raw-Gent

Thanks for taking the time to contribute.

Raw-Gent is still an early open-source project, so the most helpful contributions are the ones that improve clarity, stability, and developer experience without making the repo harder to run. Bug fixes, documentation improvements, test coverage, setup polish, and focused feature work are all welcome.

## Before You Start

- Read the main [README.md](README.md) for the product overview and local setup.
- Read [DEPLOYMENT.md](DEPLOYMENT.md) if your change affects Docker, environment variables, or production behavior.
- Search existing issues and pull requests before starting overlapping work.
- If you want to make a larger architectural change, open an issue first so we can align before you invest a lot of time.

## Good First Contribution Areas

- Fix bugs in auth, job coordination, or WebSocket flows
- Improve Redis or worker reliability
- Add tests for backend routes, Redis integration, or WebSocket behavior
- Improve documentation, setup, or deployment instructions
- Polish frontend UX around job status, diffs, or repository selection

## Development Setup

The easiest way to work on the whole stack is Docker:

```bash
docker compose --env-file .env up --build
```

For direct local development, follow the setup in [README.md](README.md). In short:

- `backend/` uses Python + Poetry
- `frontend/` uses Node + Yarn
- `job_runner/` uses Python + `requirements.txt`
- Redis is required for the async job flow

## Repository Layout

- `backend/`: FastAPI API, auth routes, job orchestration, Redis services, WebSocket routes
- `frontend/`: React/Vite app for login, task submission, live updates, and diff viewing
- `job_runner/`: local/cloud worker execution and agent workflow logic
- `deploy/`: proxy and deployment configuration

## Branches and Pull Requests

- Create a focused branch for your change.
- Keep pull requests narrow and reviewable when possible.
- Explain the user-facing impact and the technical approach in the PR description.
- Link the related issue if there is one.
- Include screenshots or short screen recordings for UI changes.
- Mention any environment-variable, Docker, or migration implications clearly.

## Code Style Expectations

- Prefer small, readable changes over broad refactors unless the refactor is the point of the PR.
- Match the existing style of the file you are editing.
- Update docs when behavior, setup, or environment variables change.
- Do not commit secrets, private keys, or real credentials.
- Keep generated files, local env files, and machine-specific artifacts out of commits.

## Testing Expectations

Automated coverage in this project is still growing, so contributors should be honest and practical here.

For the part of the project you touch, run the strongest check that is realistically available:

- Frontend: build the app and make sure the affected flow still works
- Backend: run the API locally or in Docker and exercise the changed route or service
- Worker: run targeted jobs against a safe test repository when possible
- If you add or change behavior around Redis, job status, or WebSockets, add or update tests where practical

If you could not run a test or local verification step, call that out clearly in the pull request.


## Security

If you believe you found a security issue, please do not open a public issue first. Follow the process in [SECURITY.md](SECURITY.md).

## Community Standards

By participating in this project, you agree to follow the guidelines in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
