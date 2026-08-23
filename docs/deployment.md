# Deployment

Deployment to Streamlit Community Cloud is finalized in phase 09. This is a placeholder —
not blocking for phase 01.

Planned shape (see `.claude/steering/tech.md`): connect the GitHub repo to Streamlit
Community Cloud, point it at `app.py`, deploy from `main`. Secrets (`DATABASE_URL`,
`GEMINI_API_KEY`) are set once in the Cloud app's Settings → Secrets panel — a manual step
in the Cloud UI, not something Claude configures remotely.
