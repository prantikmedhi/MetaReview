# MetaReview Setup Guide

This guide is optimized for a fully free, end-to-end hackathon setup:

- OpenMetadata running locally in Docker on your Mac
- MetaReview running either from your terminal or from a self-hosted GitHub Actions runner on the same machine
- Gemini providing review text
- GitHub pull request comment as final output

## 1. Architecture that actually works locally

There are two valid ways to run MetaReview against a local Docker deployment of OpenMetadata:

### Option A. Local CLI run

Use this when you want fastest setup and maximum demo reliability.

Flow:

1. OpenMetadata runs on your Mac in Docker
2. MetaReview runs from your terminal
3. MetaReview reads PR diff through GitHub API
4. MetaReview calls local OpenMetadata at `http://localhost:8585/api`
5. MetaReview posts review comment back to GitHub

### Option B. Self-hosted GitHub Actions runner

Use this when you want full GitHub Action automation while keeping OpenMetadata local and free.

Flow:

1. OpenMetadata runs on your Mac in Docker
2. Self-hosted GitHub Actions runner runs on same Mac
3. Workflow calls local OpenMetadata through `localhost`
4. Workflow posts review comment back to GitHub

Important:

GitHub-hosted runners cannot reach `localhost` on your laptop. If OpenMetadata stays local, use local CLI or self-hosted runner.

## 2. MacBook Air M2 guidance

For your `MacBook Air M2, 16 GB RAM, 256 GB SSD`:

- This setup is viable for hackathon demo use
- Allocate `6-8 GB` RAM to Docker
- Allocate `4 CPUs` to Docker
- Keep at least `25-30 GB` free disk before setup
- Keep charger connected during demo

Official local Docker minimum from OpenMetadata docs:

- `6 GiB` memory
- `4 vCPUs`

## 3. Prerequisites

You need:

- Docker Desktop
- Python `3.11+`
- GitHub repository for this project
- GitHub personal access token for local testing
- Gemini API key

## 4. Start OpenMetadata locally with Docker

Use the official OpenMetadata local Docker deployment guide:

- Local Docker deployment: `https://docs.open-metadata.org/latest/quick-start/local-docker-deployment`

High-level steps:

1. Install Docker Desktop
2. Open Docker Desktop settings
3. Set resources:
   - Memory: `6 GB` minimum, `8 GB` preferred
   - CPU: `4`
4. Follow OpenMetadata quickstart to download their Docker Compose file
5. Start the stack with Docker Compose
6. Wait until OpenMetadata UI becomes reachable at:
   - `http://localhost:8585`

Quick health check:

```bash
curl http://localhost:8585/api/v1/system/version
```

If that responds, MetaReview can talk to OpenMetadata locally.

## 5. Generate OpenMetadata API token

After OpenMetadata is running:

1. Open `http://localhost:8585`
2. Sign in to OpenMetadata
3. Generate either:
   - bot token, recommended for automation
   - personal access token, acceptable for demo

Official auth docs:

- `https://docs.open-metadata.org/v1.13.x-SNAPSHOT/api-reference/authentication`

Use these local values:

```bash
OPENMETADATA_URL=http://localhost:8585/api
OPENMETADATA_VERIFY_SSL=false
OPENMETADATA_JWT_TOKEN=<generated_token>
```

## 6. Seed demo metadata in OpenMetadata

Before demo, make sure OpenMetadata contains metadata that produces strong review output.

Recommended demo entities:

- table `analytics.users`
- column `analytics.users.email` tagged as `PII`
- table `analytics.orders`
- column `analytics.orders.legacy_user_id` marked deprecated
- at least one downstream dashboard or model connected through lineage

Target demo story:

- PR touches `users.email`
- PR references deprecated column
- OpenMetadata shows downstream dependencies
- MetaReview returns `HIGH` or `MEDIUM` risk with concrete reasons

## 7. Configure MetaReview locally

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use `.env.example` as your reference values.

Export variables:

```bash
export GITHUB_TOKEN=ghp_your_token
export GITHUB_REPOSITORY=prantikmedhi/MetaReview
export PR_NUMBER=1
export GEMINI_API_KEY=your_gemini_key
export OPENMETADATA_URL=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN=your_openmetadata_token
export OPENMETADATA_VERIFY_SSL=false
export OPENMETADATA_MAX_DOWNSTREAM_DEPTH=2
export METAREVIEW_MODEL=gemini-1.5-flash
export METAREVIEW_MAX_FILES=25
```

## 8. Run MetaReview from terminal

This is easiest fully free path.

Run:

```bash
PYTHONPATH=src python3 -m metareview.main
```

Expected outcome:

- MetaReview fetches PR files from GitHub
- MetaReview queries local OpenMetadata
- MetaReview asks Gemini for review copy
- MetaReview creates or updates GitHub PR comment

## 9. Run as self-hosted GitHub Action

This is best if judges want to see real automation.

Repository now includes:

- [`.github/workflows/metareview-self-hosted.yml`](./.github/workflows/metareview-self-hosted.yml)

This workflow:

- runs on `self-hosted`
- checks local OpenMetadata health
- executes MetaReview against your local Docker OpenMetadata

### GitHub setup

Add repository secrets under `Settings -> Secrets and variables -> Actions`:

| Secret | Value for local Docker setup |
|---|---|
| `GEMINI_API_KEY` | your Gemini key |
| `OPENMETADATA_URL` | `http://localhost:8585/api` |
| `OPENMETADATA_JWT_TOKEN` | token generated in local OpenMetadata |

Optional repository variables:

| Variable | Recommended value |
|---|---|
| `OPENMETADATA_VERIFY_SSL` | `false` |
| `OPENMETADATA_MAX_DOWNSTREAM_DEPTH` | `2` |
| `METAREVIEW_MODEL` | `gemini-1.5-flash` |
| `METAREVIEW_MAX_FILES` | `25` |

### Runner setup

1. In GitHub repository, open `Settings -> Actions -> Runners`
2. Add self-hosted runner
3. Install runner on same Mac where Docker OpenMetadata is running
4. Start runner
5. Enable workflow file:
   - [`.github/workflows/metareview-self-hosted.yml`](./.github/workflows/metareview-self-hosted.yml)

## 10. Which workflow file to use

- [`.github/workflows/metareview.yml`](./.github/workflows/metareview.yml)
  Use when OpenMetadata is hosted somewhere reachable from GitHub-hosted runners.
- [`.github/workflows/metareview-self-hosted.yml`](./.github/workflows/metareview-self-hosted.yml)
  Use when OpenMetadata runs locally on your laptop in Docker.

For your free local setup, prefer self-hosted workflow.

## 11. Best demo sequence

Recommended live demo:

1. Show local OpenMetadata UI at `http://localhost:8585`
2. Show `users.email` tagged as PII
3. Show lineage from affected table to dashboard/model
4. Open GitHub PR with SQL change
5. Trigger local CLI run or self-hosted workflow
6. Open PR comment from MetaReview
7. Explain:
   - sensitive data risk
   - deprecated field risk
   - downstream blast radius
   - impact score

## 12. Troubleshooting

### OpenMetadata UI does not load

Check:

- Docker Desktop is running
- Docker has at least `6 GB` memory
- OpenMetadata containers are healthy

### `curl http://localhost:8585/api/v1/system/version` fails

Check:

- OpenMetadata is not fully started yet
- port `8585` is in use by another service
- Docker resources are too low

### GitHub Action cannot reach OpenMetadata

Root cause is usually runner type mismatch.

- If workflow runs on `ubuntu-latest`, it cannot reach your laptop `localhost`
- Use self-hosted runner or local CLI mode

### OpenMetadata auth fails

Check:

- `OPENMETADATA_URL` is exactly `http://localhost:8585/api`
- token is valid
- token has enough permissions

### Gemini fails

MetaReview falls back to deterministic static review text. Demo still works, but response will be less polished.

## 13. Professional hackathon framing

Use this narrative:

- Problem: metadata exists, but developers do not see it during PR review
- Insight: OpenMetadata already knows lineage and sensitivity
- Product: MetaReview injects that knowledge directly into code review
- Outcome: fewer broken dashboards, safer data changes, faster review loops

## 14. Submission checklist

Before final submission:

- verify local OpenMetadata starts cleanly on your Mac
- verify `curl` health check works
- verify one PR gets comment successfully
- prepare one guaranteed PII example
- prepare one guaranteed lineage example
- keep terminal window ready as backup to run local CLI mode
- record short backup demo video

## 15. One-line pitch

MetaReview turns local OpenMetadata intelligence into live pull request guardrails for safer data engineering changes.
