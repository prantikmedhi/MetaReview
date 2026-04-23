# MetaReview Setup Guide

This guide gets MetaReview from zero to demo-ready with a professional setup suitable for a hackathon submission, technical judging, and a live walkthrough.

## 1. What you are deploying

MetaReview runs as a GitHub Action on pull requests. The workflow:

1. receives a pull request event
2. fetches changed files through the GitHub API
3. extracts SQL and referenced tables/columns
4. enriches that diff with OpenMetadata schema, tags, and lineage
5. asks Gemini to turn that context into a review
6. posts or updates a pull request comment in GitHub

## 2. Prerequisites

You need:

- A GitHub repository with Actions enabled
- Access to an OpenMetadata instance with API access
- A Google Gemini API key
- Python 3.11 or newer for local testing

## 3. Required secrets

Add these repository secrets in GitHub under `Settings -> Secrets and variables -> Actions`:

| Secret | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Calls Gemini for review generation |
| `OPENMETADATA_URL` | Yes | Base URL for your OpenMetadata instance |
| `OPENMETADATA_JWT_TOKEN` | Yes | Auth token for OpenMetadata API |

Optional repository variables:

| Variable | Default | Purpose |
|---|---|---|
| `OPENMETADATA_VERIFY_SSL` | `true` | Disable only for insecure local demo instances |
| `OPENMETADATA_MAX_DOWNSTREAM_DEPTH` | `2` | Controls lineage traversal depth |
| `METAREVIEW_MODEL` | `gemini-1.5-flash` | Gemini model name |
| `METAREVIEW_MAX_FILES` | `25` | Caps analyzed PR files |

## 4. OpenMetadata preparation

MetaReview is only as good as metadata quality. Before demo day, make sure your OpenMetadata instance contains:

- at least one service and database/schema/table inventory
- lineage between tables and downstream assets
- sensitive data tags such as `PII`, `Sensitive`, `Email`, `SSN`, or similar
- one known deprecated field or description note for demo impact

Recommended demo data:

- `analytics.users.email` tagged as PII
- `analytics.orders.legacy_user_id` marked deprecated in description or tag
- downstream dashboards connected through lineage

## 5. Repository setup

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Commit and push all project files, especially:

- `.github/workflows/metareview.yml`
- `src/metareview/*`
- `README.md`
- `SETUP.md`

## 6. How GitHub Action is wired

Workflow file: [`.github/workflows/metareview.yml`](./.github/workflows/metareview.yml)

Important design choices:

- Uses `pull_request_target` so repository secrets are available
- Avoids checking out pull request head code from forks
- Pulls file diff through GitHub API instead
- Updates existing MetaReview comment to keep PR clean

Security note:

`pull_request_target` is powerful. This repository setup is safe for hackathon/MVP use because workflow code runs from base repository and analyzes PR content through API responses instead of executing code from the PR branch.

## 7. Local test before GitHub demo

Export environment variables:

```bash
export GITHUB_TOKEN=ghp_your_token
export GITHUB_REPOSITORY=owner/repo
export PR_NUMBER=1
export GEMINI_API_KEY=your_gemini_key
export OPENMETADATA_URL=https://openmetadata.example.com
export OPENMETADATA_JWT_TOKEN=your_openmetadata_token
```

Run:

```bash
PYTHONPATH=src python3 -m metareview.main
```

Expected result:

- script prints analysis summary to console
- comment is created or updated on target pull request

## 8. Best demo flow

Use a prepared pull request with one or two obvious issues:

1. Change SQL to include `users.email`
2. Rename or remove deprecated column
3. Reference a model with known dashboard lineage

During demo:

1. Open PR diff
2. Point at risky SQL line
3. Trigger workflow by pushing tiny commit if needed
4. Open Actions tab briefly
5. Return to PR and show MetaReview comment
6. Explain:
   - PII risk
   - downstream impact
   - impact score
   - recommended action

## 9. Professional judging narrative

Use this framing:

- Problem: engineers break analytics because metadata is trapped in catalog tools
- Insight: OpenMetadata already knows blast radius and sensitivity, but PR workflows do not
- Product: MetaReview injects that intelligence directly into code review
- Outcome: fewer broken dashboards, fewer compliance mistakes, faster engineering feedback

## 10. Troubleshooting

### No PR comment appears

Check:

- workflow ran on `pull_request_target`
- `GITHUB_TOKEN` has `pull-requests: write`
- `GEMINI_API_KEY` and OpenMetadata secrets are present

### OpenMetadata calls fail

Check:

- base URL is correct and reachable
- JWT token is valid
- SSL validation settings match your environment

### Gemini fails

MetaReview falls back to deterministic static review text. Demo still works, but AI narrative will be less polished.

## 11. Submission checklist

Before final submission:

- add architecture screenshot to README if hackathon allows
- record 30 to 60 second backup demo video
- prepare one PR with guaranteed PII hit
- prepare one PR with guaranteed lineage hit
- verify comment generation stays under 10 seconds in normal conditions

## 12. What to say in one sentence

MetaReview turns OpenMetadata from passive catalog into active pull request guardrail for safer data changes.

