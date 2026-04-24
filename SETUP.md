# MetaReview Setup Guide

This guide describes how to operate MetaReview as a hosted GitHub pull request guardrail.

## 1. Architecture

1. GitHub Actions runs MetaReview on `ubuntu-latest`.
2. MetaReview reads the pull request file list and patches through the GitHub API.
3. MetaReview extracts SQL references from changed files.
4. MetaReview calls OpenMetadata for table, column, tag, and lineage context.
5. MetaReview builds a risk summary.
6. Gemini drafts reviewer-friendly text when available.
7. MetaReview creates or updates one GitHub PR comment.

MetaReview reviews metadata and diffs only. It does not execute SQL and does not retrieve data rows.

## 2. Prerequisites

- Python `3.11+` for local testing
- GitHub repository with Actions enabled
- Gemini API key
- OpenMetadata account and personal access token
- OpenMetadata URL reachable from the selected runner

## 3. OpenMetadata Token

In OpenMetadata:

1. Open **Settings**.
2. Open **Team & User Management**.
3. Open **Users**.
4. Select your user.
5. Generate a personal access token.

Store this token only in GitHub secrets or your local shell. Revoke and rotate it if it is exposed.

MetaReview accepts either URL shape:

```bash
OPENMETADATA_URL=https://sandbox.open-metadata.org
OPENMETADATA_URL=https://sandbox.open-metadata.org/api
```

Both are normalized internally.

## 4. GitHub Configuration

Open:

```text
Settings -> Secrets and variables -> Actions -> Repository secrets
```

Add:

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | Gemini API key |
| `OPENMETADATA_URL` | OpenMetadata base URL |
| `OPENMETADATA_JWT_TOKEN` | OpenMetadata personal access token |

Optional repository variables:

| Variable | Recommended value |
|---|---|
| `OPENMETADATA_VERIFY_SSL` | `true` |
| `OPENMETADATA_MAX_DOWNSTREAM_DEPTH` | `2` |
| `METAREVIEW_MODEL` | `gemini-2.5-flash` |
| `METAREVIEW_MAX_FILES` | `25` |

## 5. Workflow Selection

Use the hosted workflow when OpenMetadata is reachable from GitHub-hosted runners:

```text
.github/workflows/metareview.yml
```

Use the self-hosted workflow only for private OpenMetadata deployments that are reachable from your own runner:

```text
.github/workflows/metareview-self-hosted.yml
```

The self-hosted workflow is manual-only to avoid queued checks when no runner is available.

## 6. Local Test Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
export GITHUB_TOKEN=ghp_your_token
export GITHUB_REPOSITORY=owner/repo
export PR_NUMBER=1
export GEMINI_API_KEY=your_gemini_key
export OPENMETADATA_URL=https://sandbox.open-metadata.org
export OPENMETADATA_JWT_TOKEN=your_openmetadata_token
export OPENMETADATA_VERIFY_SSL=true
export OPENMETADATA_MAX_DOWNSTREAM_DEPTH=2
export METAREVIEW_MODEL=gemini-2.5-flash
export METAREVIEW_MAX_FILES=25
```

```bash
PYTHONPATH=src python3 -m metareview.main
```

Expected outcome:

- PR files are fetched from GitHub.
- SQL-bearing files are parsed.
- OpenMetadata context is requested for referenced tables.
- Risk is scored.
- A PR comment is created or updated.

## 7. Troubleshooting

### GitHub Action Cannot Authenticate With OpenMetadata

- Confirm `OPENMETADATA_JWT_TOKEN` is current.
- Confirm the secret has no extra spaces or quotes.
- Confirm `OPENMETADATA_URL` is reachable from the runner.
- Confirm `OPENMETADATA_VERIFY_SSL` matches your OpenMetadata deployment.

### No Tables Are Found

- Confirm the PR adds SQL-bearing lines, not only deleted lines.
- Use fully qualified table names where possible.
- For dbt models, use standard `ref("model")` or `source("schema", "table")` macros.

### Gemini Fails

MetaReview tries the configured model, then `gemini-2.5-flash`, then `gemini-flash-latest`. If all fail, it still posts deterministic fallback review text.

### Workflow Does Not Run

- Confirm Actions are enabled.
- Confirm `.github/workflows/metareview.yml` exists on the default branch.
- Confirm the pull request event is `opened`, `synchronize`, or `reopened`.

## 8. Release Checklist

- Secrets configured
- OpenMetadata token tested
- Gemini key tested
- Hosted workflow passes on a sample PR
- Generated PR comment contains impact score and recommended action
- No sensitive tokens appear in logs, comments, commits, or screenshots
