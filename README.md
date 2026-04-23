# MetaReview

MetaReview is a metadata-aware pull request guardrail for data teams. It analyzes SQL and dbt-oriented pull requests, pulls schema and lineage context from OpenMetadata, asks Gemini for a human-readable review, and posts a structured comment back into GitHub.

For a fully free hackathon setup, MetaReview can run against a local Docker deployment of OpenMetadata on your machine. The recommended end-to-end path is a self-hosted GitHub Actions runner on the same laptop, so the workflow can reach `http://localhost:8585/api`.

## Why this stands out

- Brings OpenMetadata intelligence into pull request workflows.
- Flags PII exposure, deprecated columns, and downstream blast radius before merge.
- Produces a risk score and executive summary that judges can understand in seconds.
- Ships as a GitHub Action, so there is no separate UI to build or explain.

## MVP capabilities

- Fetch changed files from a pull request through the GitHub API
- Extract SQL additions and referenced tables/columns
- Query OpenMetadata for table metadata and lineage
- Score impact as `LOW`, `MEDIUM`, or `HIGH`
- Generate a polished review with Gemini
- Upsert a GitHub pull request comment
- Fall back to deterministic review text if Gemini is unavailable

## Repository layout

```text
.github/workflows/metareview.yml   GitHub Action workflow
src/metareview/                    Core Python package
SETUP.md                           End-to-end setup guide
PRD.md                             Original product requirements
```

## Quick start

1. Start OpenMetadata locally with Docker on your machine.
2. Generate an OpenMetadata bot or personal token.
3. Add GitHub secrets:
   - `GEMINI_API_KEY`
   - `OPENMETADATA_URL`
   - `OPENMETADATA_JWT_TOKEN`
4. Use one of these execution modes:
   - `Local CLI`: run MetaReview directly from your terminal against a PR
   - `Self-hosted GitHub runner`: full PR-comment flow with local Docker OpenMetadata
5. Open pull request that changes `.sql`, dbt model, or SQL-containing files.

Full setup is in [SETUP.md](./SETUP.md).

## Local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPOSITORY=owner/repo
export PR_NUMBER=12
export GEMINI_API_KEY=xxx
export OPENMETADATA_URL=http://localhost:8585/api
export OPENMETADATA_JWT_TOKEN=xxx

PYTHONPATH=src python3 -m metareview.main
```

## Workflow options

- [`.github/workflows/metareview.yml`](./.github/workflows/metareview.yml): default GitHub-hosted runner workflow. Use this only when OpenMetadata is reachable from GitHub-hosted infrastructure.
- [`.github/workflows/metareview-self-hosted.yml`](./.github/workflows/metareview-self-hosted.yml): recommended free path for local Docker OpenMetadata. Run a self-hosted GitHub Actions runner on same Mac.

## Demo story

1. Open PR that renames or drops column used downstream.
2. MetaReview detects changed table references.
3. OpenMetadata reveals lineage and sensitive tags.
4. Gemini explains risk in plain language.
5. GitHub comment shows impact score and recommended next step.

## Hackathon positioning

- Real pain: broken dashboards, accidental PII misuse, blind schema changes
- Strong technical depth: GitHub + OpenMetadata + Gemini in one loop
- Fast to demo: single PR action, visible result, no front-end dependency
- Clear expansion path: Slack alerts, policy enforcement, auto-fix suggestions

## Local OpenMetadata defaults

For local Docker deployment, use:

- `OPENMETADATA_URL=http://localhost:8585/api`
- `OPENMETADATA_VERIFY_SSL=false`

