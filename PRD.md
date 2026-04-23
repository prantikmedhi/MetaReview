
🏆 PRODUCT REQUIREMENTS DOCUMENT (PRD)

🚀 Product Name

MetaReview — Metadata-Aware PR Guardrail

⸻

🧠 1. Problem Statement

Modern data teams use tools like OpenMetadata to manage:

* data lineage
* PII classification
* data contracts
* governance

But developers writing SQL / pipelines in GitHub:

* ❌ don’t see this metadata
* ❌ unknowingly break downstream dashboards
* ❌ misuse sensitive (PII) data

👉 This creates:

* broken analytics
* compliance risks
* expensive debugging

OpenMetadata already tracks full data flow and dependencies across systems, enabling impact analysis and governance  ￼

BUT this intelligence is not available inside PR workflows.

⸻

🎯 2. Solution

MetaReview is a GitHub Action that:

👉 Automatically reviews Pull Requests
👉 Uses OpenMetadata APIs
👉 Uses Gemini AI to generate insights

…and posts a smart review comment directly in GitHub

⸻

💡 3. Core Value Proposition

“Bring metadata intelligence into CI/CD so developers stop breaking data systems blindly.”

⸻

👥 4. Target Users

Primary

* Data Engineers
* Analytics Engineers (dbt users)

Secondary

* Data Platform Teams
* Data Governance Teams

⸻

🧩 5. Key Features

🔍 5.1 Metadata-Aware PR Review

* Analyze SQL/dbt code changes
* Extract tables + columns

⸻

⚠️ 5.2 PII Risk Detection

* Detect sensitive columns (email, SSN)
* Use OpenMetadata classification tags

👉 OpenMetadata supports metadata tagging for governance and compliance  ￼

⸻

💀 5.3 Deprecated Column Detection

* Identify outdated fields
* Suggest replacements

⸻

📉 5.4 Lineage-Based Impact Analysis

* Identify downstream dependencies:
    * dashboards
    * pipelines
    * models

👉 OpenMetadata lineage tracks relationships across tables, pipelines, dashboards for impact analysis  ￼

⸻

📊 5.5 Impact Score (Differentiator)

* Quantifies risk level:
    * LOW / MEDIUM / HIGH
* Based on:
    * PII usage
    * downstream assets
    * schema changes

⸻

🤖 5.6 AI-Generated Review (Gemini)

* Converts metadata → human-readable feedback
* Provides:
    * risks
    * suggestions
    * explanations

⸻

💬 5.7 GitHub PR Comment Bot

* Automatically posts review
* No UI required

⸻

🏗️ 6. System Architecture

GitHub PR Event
        ↓
GitHub Action Trigger
        ↓
Python Script (Core Engine)
        ↓
[Step 1] Extract SQL from PR
        ↓
[Step 2] Parse tables/columns
        ↓
[Step 3] Call OpenMetadata APIs
        ↓
[Step 4] Build metadata context
        ↓
[Step 5] Send to Gemini API
        ↓
[Step 6] Generate review
        ↓
[Step 7] Post PR comment

⸻

🛠️ 7. Tech Stack

🧠 Core

* Python (main logic)
* GitHub Actions (CI/CD trigger)

⸻

🔗 APIs

OpenMetadata API

* /api/v1/tables → schema + tags
* /api/v1/lineage → downstream impact
* /api/v1/dataContracts (optional)

⸻

Gemini API

* Model: gemini-1.5-flash
* Purpose:
    * generate PR review
    * interpret metadata

⸻

🧰 Libraries

* requests → API calls
* google-generativeai → Gemini
* re / sqlparse → SQL parsing

⸻

⚙️ Dev Tools

* GitHub
* GitHub Actions
* Google AI Studio (Gemini API key)

⸻

🔄 8. Workflow

Step-by-step

1. Developer opens PR
2. GitHub Action triggers
3. Script fetches PR diff
4. Extract SQL queries
5. Identify tables + columns
6. Query OpenMetadata
7. Build metadata context
8. Send context to Gemini
9. Generate review
10. Post PR comment

⸻

📊 9. Example Output

🔍 MetaReview Bot
⚠️ PII Risk — users.email is sensitive  
💀 Deprecated — orders.legacy_user_id  
📉 Impact — affects 4 dashboards  
📊 Impact Score: HIGH (8.7/10)

⸻

🧪 10. MVP Scope (Hackathon)

MUST HAVE

* GitHub Action working
* SQL extraction
* OpenMetadata API call
* Gemini-generated comment

SHOULD HAVE

* Impact score
* clean formatting

OPTIONAL

* data contracts
* advanced parsing

⸻

🚨 11. Risks & Mitigation

Risk	Solution
SQL parsing fails	fallback to regex
API latency	cache metadata
Gemini errors	fallback static template
Demo failure	pre-record PR demo

⸻

📈 12. Success Metrics

* PR comment generated < 10 sec
* Detects at least 2 risks
* Clean demo without errors

⸻

🎬 13. Demo Plan

1. Open PR with SQL change
2. Show query
3. Wait
4. Bot comment appears
5. Highlight:
    * PII detection
    * lineage impact

⸻

🚀 14. Future Scope

* Slack integration
* CI/CD pipeline scoring
* auto-fix suggestions
* real-time data contract enforcement

⸻

🧠 15. Why This Wins

* Deep OpenMetadata integration
* Solves real engineering problem
* Fits directly into developer workflow
* Strong demo impact

⸻

🧾 FINAL SUMMARY

MetaReview transforms OpenMetadata from a passive catalog into an active guardrail inside developer workflows, enabling safer, smarter data changes.

