# MetaReview Demo Voiceover

## 0:00-0:20 Setup and hook

Hi, this is MetaReview. It reviews SQL changes in pull requests before merge, looks up metadata context from OpenMetadata, and leaves a practical review comment right on the PR.

In this demo, I am opening a realistic pull request that selects customer contact fields, including a few sensitive columns, so we can see the action call out meaningful risk instead of a generic success message.

## 0:20-1:00 Show the repository and the PR diff

Here is the sample change. The pull request updates `examples/customer_contact_review.sql`, which is the kind of SQL-bearing file MetaReview is designed to inspect.

The query now selects `email`, `phone_number`, `ssn`, and `credit_card` from the customer contact table. That gives the reviewer something realistic to evaluate because these are exactly the kinds of fields that should trigger extra scrutiny before merge.

I also added this short voiceover script in `docs/demo-video-voiceover.md` so the demo branch contains everything needed for the walkthrough.

## 1:00-1:45 Explain what the GitHub Action does

When I open this PR, the `MetaReview PR Guardrail` workflow starts automatically on `pull_request_target`.

The action checks out the trusted workflow code from the default branch, installs the Python dependencies, and runs MetaReview against the pull request diff. It does not execute the SQL. Instead, it parses the changed files, identifies referenced tables and columns, checks OpenMetadata for table and column context, scores the risk, and prepares a reviewer-facing comment.

That means the signal comes from metadata and the diff itself, not from running warehouse queries during CI.

## 1:45-2:30 Show the review output

Once the action finishes, the PR should get a comment with a risk score and a short explanation of what was detected.

For this example, I would expect the review to highlight PII-sensitive fields such as `email`, `phone_number`, `ssn`, and `credit_card`. Depending on the metadata available in OpenMetadata, it may also mention downstream impact or any relevant tags attached to the source table.

This is the key value of MetaReview: it gives engineers immediate context while the change is still in review, instead of discovering sensitive-field exposure later in the release process.

## 2:30-3:00 Wrap-up

To recap, this demo shows a normal pull request with a realistic SQL change, an automatic metadata-aware review, and actionable guidance directly in GitHub.

If you want to test the full flow yourself, open a PR like this against `main`, wait for the workflow to complete, and then inspect the MetaReview comment and the workflow logs.
