# MetaReview Setup Guide

This guide is optimized for a fully free, end-to-end hackathon setup without Docker:

- OpenMetadata hosted sandbox at `https://sandbox.open-metadata.org`
- GitHub-hosted Actions runner
- Gemini providing review text
- GitHub pull request comment as final output

## 1. Architecture

Recommended flow:

1. OpenMetadata sandbox hosts metadata, tags, and lineage.
2. GitHub Actions runs MetaReview on `ubuntu-latest`.
3. MetaReview reads the pull request diff through the GitHub API.
4. MetaReview calls the OpenMetadata sandbox API.
5. Gemini turns the metadata findings into readable review text.
6. MetaReview posts or updates a GitHub PR comment.

This avoids Docker, local OpenMetadata, and self-hosted runners.

## 2. Prerequisites

You need:

- Python `3.11+` for local testing
- GitHub repository for this project
- Gemini API key
- OpenMetadata sandbox account
- OpenMetadata sandbox personal access token

## 3. Set up OpenMetadata sandbox

1. Open `https://sandbox.open-metadata.org`.
2. Sign in with Google.
3. Complete onboarding by adding yourself as a user/team member.
4. Search for sample tables in the sandbox.
5. Pick one useful demo table with at least one of:
   - PII or sensitive tag
   - deprecated or important column
   - downstream lineage

Use this during the live demo to show that MetaReview is powered by OpenMetadata metadata.

## 4. Generate OpenMetadata token

In the sandbox UI:

1. Open **Settings**.
2. Open **Team & User Management**.
3. Open **Users**.
4. Select your user.
5. Generate a personal access token.

Do not paste this token in chat, commits, screenshots, or shared docs. Store it only in your shell or GitHub secrets.

MetaReview accepts either sandbox URL:

```bash
OPENMETADATA_URL=https://sandbox.open-metadata.org
```

or:

```bash
OPENMETADATA_URL=https://sandbox.open-metadata.org/api
```

Both are normalized internally.

## 5. Configure GitHub secrets

In your repository, open:

```text
Settings -> Secrets and variables -> Actions -> Repository secrets
```

Add:

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | your Gemini API key |
| `OPENMETADATA_URL` | `https://sandbox.open-metadata.org` |
| `OPENMETADATA_JWT_TOKEN` | your OpenMetadata sandbox personal access token |

Optional repository variables:

```text
Settings -> Secrets and variables -> Actions -> Variables
```

| Variable | Recommended value |
|---|---|
| `OPENMETADATA_VERIFY_SSL` | `true` |
| `OPENMETADATA_MAX_DOWNSTREAM_DEPTH` | `2` |
| `METAREVIEW_MODEL` | `gemini-1.5-flash` |
| `METAREVIEW_MAX_FILES` | `25` |

## 6. Workflow to use

Use the default GitHub-hosted workflow:

```text
.github/workflows/metareview.yml
```

This workflow runs on `ubuntu-latest` and can reach `https://sandbox.open-metadata.org`.

Do not use the self-hosted workflow for the sandbox path. The self-hosted workflow is only useful when OpenMetadata runs on your laptop.

## 7. Local test run

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Export values:

```bash
export GITHUB_TOKEN=ghp_your_token
export GITHUB_REPOSITORY=owner/repo
export PR_NUMBER=1
export GEMINI_API_KEY=your_gemini_key
export OPENMETADATA_URL=https://sandbox.open-metadata.org
export OPENMETADATA_JWT_TOKEN=your_openmetadata_sandbox_token
export OPENMETADATA_VERIFY_SSL=true
export OPENMETADATA_MAX_DOWNSTREAM_DEPTH=2
export METAREVIEW_MODEL=gemini-1.5-flash
export METAREVIEW_MAX_FILES=25
```

Run:

```bash
PYTHONPATH=src python3 -m metareview.main
```

Expected outcome:

- MetaReview fetches PR files from GitHub.
- MetaReview queries the OpenMetadata sandbox.
- MetaReview asks Gemini for review copy.
- MetaReview creates or updates a GitHub PR comment.

## 8. Best demo sequence

Recommended live demo:

1. Open `https://sandbox.open-metadata.org`.
2. Show a table with tags, columns, or lineage.
3. Open a GitHub PR that changes SQL.
4. Trigger or wait for `.github/workflows/metareview.yml`.
5. Open the MetaReview PR comment.
6. Explain:
   - OpenMetadata supplied metadata context
   - Gemini converted it into reviewer-friendly language
   - GitHub PR comment keeps the guardrail in the developer workflow

## 9. Troubleshooting

### GitHub Action cannot authenticate with OpenMetadata

Check:

- `OPENMETADATA_JWT_TOKEN` is a current, unexpired token.
- The token was copied without extra spaces or quotes.
- `OPENMETADATA_URL` is `https://sandbox.open-metadata.org`.
- `OPENMETADATA_VERIFY_SSL` is `true`.

If you accidentally exposed a token, revoke it and generate a new one.

### GitHub Action finds no OpenMetadata tables

Check:

- The SQL in the PR references table names that exist in the sandbox.
- Try simpler table names from the sandbox search UI.
- Use a PR that references a known sandbox table for the demo.

### Gemini fails

MetaReview falls back to deterministic static review text. The PR comment still works, but the wording will be less polished.

### Workflow does not run

Check:

- Actions are enabled for the repository.
- The workflow file exists at `.github/workflows/metareview.yml`.
- The PR changes a SQL or SQL-like file.

## 10. Professional hackathon framing

Use this narrative:

- Problem: metadata exists, but developers do not see it during PR review.
- Insight: OpenMetadata already knows lineage and sensitivity.
- Product: MetaReview injects that knowledge directly into code review.
- Outcome: fewer broken dashboards, safer data changes, faster review loops.

## 11. Submission checklist

Before final submission:

- verify sandbox login works
- verify OpenMetadata token is stored as a GitHub secret
- verify Gemini key is stored as a GitHub secret
- verify one PR gets a MetaReview comment
- prepare one known sandbox table example
- prepare one SQL PR that references that table
- record a short backup demo video

## 12. Optional Docker fallback

If the sandbox is unavailable, you can still run OpenMetadata locally with Docker and use:

```bash
OPENMETADATA_URL=http://localhost:8585/api
OPENMETADATA_VERIFY_SSL=false
```

For that path, use a local CLI run or `.github/workflows/metareview-self-hosted.yml`, because GitHub-hosted runners cannot reach `localhost` on your laptop.

## 13. One-line pitch

MetaReview turns OpenMetadata intelligence into live pull request guardrails for safer data engineering changes.
