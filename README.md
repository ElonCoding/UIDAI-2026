# UIDAI Analytics Hub (Streamlit)

This repo is a **Streamlit** app (see `app.py`).

## Local run

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Why Vercel showed `NOT_FOUND`

Vercel deployments need a routable output (static files) or a supported runtime entrypoint (e.g. a serverless function).
This repo has neither by default, so requests to `/` had nothing to match and Vercel returned `NOT_FOUND`.

This repo includes a minimal static landing page in `public/index.html` and routes all paths to it via `vercel.json` so
Vercel no longer returns `NOT_FOUND`.

## Deploying the actual Streamlit app (recommended)

Use a platform that runs long-lived Python web processes (Streamlit server), such as:

- Streamlit Community Cloud
- Render
- Railway
- Fly.io


