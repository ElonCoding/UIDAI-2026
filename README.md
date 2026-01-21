# UIDAI Migration & Urbanization Tracker

Executive-grade analytics dashboard for migration and urbanization signals using UIDAI Aadhaar activity as a proxy.  
New architecture: FastAPI backend (Python) + React + Vite frontend (TypeScript). The legacy Streamlit prototype remains in `app.py` but is superseded by the new stack.

## Structure

- `backend/` – FastAPI service exposing JSON endpoints for summaries, time series, map data, comparisons, and insights.
- `frontend/` – Vite + React UI with Leaflet map, Recharts visualizations, filters, and export actions.
- `api_data_aadhar_*` – Source CSVs (enrolment, biometric, demographic).
- `india_states.geo.json` – GeoJSON for state boundaries (copied to `frontend/public` for the map).

## Backend (FastAPI)

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate  # or source .venv/bin/activate on *nix
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Key endpoints:
- `GET /meta` – states, district list, min/max dates, quick presets
- `GET /summary` – KPI metrics (supports state/district + time presets/custom range)
- `GET /timeseries` – working-age migration proxy over time (monthly/quarterly/yearly)
- `GET /map` – choropleth values for states or districts
- `GET /comparisons` – bar + scatter datasets
- `GET /insights` – policy-ready narrative bullets

## Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev   # defaults to http://localhost:5173
```

Set `VITE_API_URL` in a `.env` file inside `frontend/` if the API is not on `http://localhost:8000`.

## Running both

1. Start the FastAPI server (port 8000).
2. Start Vite dev server (port 5173).
3. Open the frontend URL; all filters and visuals will call the backend API in real time.

## Notes

- Legacy Streamlit app remains in `app.py` and `requirements.txt` (root) for reference.
- Data is read from CSVs at startup; reload the API if you replace the CSV files.

