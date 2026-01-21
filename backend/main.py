from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FOLDERS = {
    "enrol": "api_data_aadhar_enrolment",
    "bio": "api_data_aadhar_biometric",
    "demo": "api_data_aadhar_demographic",
}

STATE_NORMALIZATION = {
    "westbengal": "West Bengal",
    "west bangal": "West Bengal",
    "west bengal": "West Bengal",
    "orissa": "Odisha",
    "odisha": "Odisha",
    "andaman and nicobar islands": "Andaman & Nicobar Islands",
    "jammu and kashmir": "Jammu & Kashmir",
    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "the dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "pondicherry": "Puducherry",
    "puducherry": "Puducherry",
    "karnatka": "Karnataka",
    "telngana": "Telangana",
    "andhrapradesh": "Andhra Pradesh",
    "u.p.": "Uttar Pradesh",
    "m.p.": "Madhya Pradesh",
    "a.p.": "Andhra Pradesh",
}


def clean_state_name(name: str) -> str:
    s = str(name).lower().strip()
    s = s.replace("&", "and")
    s = " ".join(s.split())
    return STATE_NORMALIZATION.get(s, s.title())


def parse_date(value: Optional[str]) -> Optional[pd.Timestamp]:
    if not value:
        return None
    try:
        return pd.to_datetime(value, format="%Y-%m-%d")
    except Exception:
        return None


def resolve_window(
    preset: Optional[str], start: Optional[str], end: Optional[str], max_date: pd.Timestamp
) -> Tuple[pd.Timestamp, pd.Timestamp]:
    if preset == "1m":
        start_date = max_date - timedelta(days=30)
    elif preset == "3m":
        start_date = max_date - timedelta(days=90)
    elif preset == "6m":
        start_date = max_date - timedelta(days=180)
    elif preset == "1y":
        start_date = max_date - timedelta(days=365)
    else:
        start_dt = parse_date(start)
        end_dt = parse_date(end)
        start_date = start_dt or (max_date - timedelta(days=90))
        max_date = end_dt or max_date
    return start_date, max_date


def calc_growth(series: pd.Series) -> float:
    """Percent change between first and last non-null points."""
    clean = series.dropna()
    if clean.empty:
        return 0.0
    first, last = clean.iloc[0], clean.iloc[-1]
    if first == 0:
        return 0.0
    return round(((last - first) / first) * 100, 2)


class DataStore:
    """Loads, cleans, and aggregates UIDAI datasets for API responses."""

    def __init__(self) -> None:
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.health: Dict[str, str] = {}
        self.state_to_district: Dict[str, List[str]] = {}
        self.min_date: pd.Timestamp = pd.Timestamp("1900-01-01")
        self.max_date: pd.Timestamp = pd.Timestamp("1900-01-01")
        self.last_refreshed: datetime = datetime.utcnow()
        self._load()

    def _load_csv_folder(self, folder: str) -> pd.DataFrame:
        full_path = BASE_DIR / folder
        files = list(full_path.glob("*.csv")) + list(Path(".").glob(f"{folder}*.csv"))
        if not files:
            self.health[folder] = "no_data"
            return pd.DataFrame()

        try:
            df = pd.concat([pd.read_csv(path, low_memory=False) for path in files], ignore_index=True)
            df["state"] = df["state"].apply(clean_state_name)
            df = df[~df["state"].str.isnumeric()]
            df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
            df = df.dropna(subset=["date"])
            self.health[folder] = f"ok:{len(files)}"
            return df
        except Exception as exc:  # pragma: no cover - defensive
            self.health[folder] = f"error:{exc}"
            return pd.DataFrame()

    def _load(self) -> None:
        for key, folder in CSV_FOLDERS.items():
            self.datasets[key] = self._load_csv_folder(folder)

        enrol = self.datasets.get("enrol", pd.DataFrame())
        if not enrol.empty:
            self.min_date = enrol["date"].min()
            self.max_date = enrol["date"].max()
            self.state_to_district = {
                state: sorted(enrol[enrol["state"] == state]["district"].dropna().unique().tolist())
                for state in sorted(enrol["state"].unique())
            }
        self.last_refreshed = datetime.utcnow()

    def reload(self) -> None:
        self._load()

    def _filter_df(
        self, df: pd.DataFrame, state: Optional[str], district: Optional[str], start: pd.Timestamp, end: pd.Timestamp
    ) -> pd.DataFrame:
        if df.empty:
            return df
        mask = (df["date"] >= start) & (df["date"] <= end)
        if state:
            mask &= df["state"] == state
        if district:
            mask &= df["district"] == district
        return df.loc[mask].copy()

    def _enrol_totals(self, df: pd.DataFrame) -> Tuple[float, float]:
        if df.empty:
            return 0.0, 0.0
        totals = df[["age_0_5", "age_5_17", "age_18_greater"]].sum()
        total_activity = totals.sum()
        adult_share = (totals["age_18_greater"] / total_activity) if total_activity else 0
        return total_activity, adult_share

    def summary(
        self,
        state: Optional[str],
        district: Optional[str],
        preset: Optional[str],
        start: Optional[str],
        end: Optional[str],
    ) -> Dict[str, object]:
        if self.max_date is pd.NaT:  # pragma: no cover - empty data safety
            return {"totalActivity": 0, "statesSignal": 0, "averageGrowth": 0, "statesCovered": 0}

        window_start, window_end = resolve_window(preset, start, end, self.max_date)

        enrol = self._filter_df(self.datasets["enrol"], state, district, window_start, window_end)
        bio = self._filter_df(self.datasets["bio"], state, district, window_start, window_end)
        demo = self._filter_df(self.datasets["demo"], state, district, window_start, window_end)

        enrol_total, adult_share = self._enrol_totals(enrol)
        bio_total = bio[["bio_age_5_17", "bio_age_17_"]].sum().sum() if not bio.empty else 0
        demo_total = demo[["demo_age_5_17", "demo_age_17_"]].sum().sum() if not demo.empty else 0
        combined_total = float(enrol_total + bio_total + demo_total)

        # Growth: compare first vs last month adult activity
        growth_values = []
        if not enrol.empty:
            monthly = (
                enrol.set_index("date")
                .resample("M")[["age_18_greater", "age_0_5", "age_5_17"]]
                .sum()
                .reset_index()
            )
            monthly["adult_share"] = np.where(
                monthly[["age_0_5", "age_5_17", "age_18_greater"]].sum(axis=1) > 0,
                monthly["age_18_greater"] / monthly[["age_0_5", "age_5_17", "age_18_greater"]].sum(axis=1),
                0,
            )
            growth_values = monthly.groupby(lambda idx: True)["adult_share"].apply(calc_growth).tolist()

        states_data = []
        if not state and enrol is not None and not enrol.empty:
            for st in enrol["state"].unique():
                st_df = enrol[enrol["state"] == st]
                st_total, st_share = self._enrol_totals(st_df)
                states_data.append({"state": st, "share": st_share, "total": st_total})

        states_signal = 0
        if states_data:
            threshold = 0.52  # heuristic: adult share > 52% indicates migration-like signal
            states_signal = round(
                (len([s for s in states_data if s["share"] > threshold]) / max(len(states_data), 1)) * 100, 2
            )

        average_growth = float(np.mean(growth_values)) if growth_values else 0.0

        return {
            "totalActivity": int(combined_total),
            "adultSharePct": round(adult_share * 100, 2),
            "statesSignal": states_signal,
            "averageGrowth": round(average_growth, 2),
            "statesCovered": enrol["state"].nunique() if not enrol.empty else 0,
            "window": {"start": window_start.date().isoformat(), "end": window_end.date().isoformat()},
            "lastRefreshed": self.last_refreshed.isoformat(),
        }

    def working_age_timeseries(
        self,
        state: Optional[str],
        district: Optional[str],
        preset: Optional[str],
        start: Optional[str],
        end: Optional[str],
        granularity: str,
    ) -> List[Dict[str, object]]:
        if self.max_date is pd.NaT:
            return []

        window_start, window_end = resolve_window(preset, start, end, self.max_date)
        enrol = self._filter_df(self.datasets["enrol"], state, district, window_start, window_end)
        if enrol.empty:
            return []

        freq_map = {"monthly": "M", "quarterly": "Q", "yearly": "A"}
        freq = freq_map.get(granularity, "M")

        grouped = (
            enrol.set_index("date")[["age_0_5", "age_5_17", "age_18_greater"]]
            .resample(freq)
            .sum()
            .reset_index()
        )
        grouped["total"] = grouped[["age_0_5", "age_5_17", "age_18_greater"]].sum(axis=1)
        grouped["adult_share"] = np.where(grouped["total"] > 0, grouped["age_18_greater"] / grouped["total"], 0)
        return [
            {
                "date": row["date"].date().isoformat(),
                "adultShare": round(row["adult_share"] * 100, 2),
                "totalActivity": int(row["total"]),
            }
            for _, row in grouped.iterrows()
        ]

    def map_view(
        self,
        state: Optional[str],
        district: Optional[str],
        preset: Optional[str],
        start: Optional[str],
        end: Optional[str],
        level: str,
    ) -> List[Dict[str, object]]:
        if self.max_date is pd.NaT:
            return []
        window_start, window_end = resolve_window(preset, start, end, self.max_date)
        enrol = self._filter_df(self.datasets["enrol"], state, district, window_start, window_end)
        if enrol.empty:
            return []

        if level == "district" and not state:
            level = "state"

        group_cols = ["state"] if level == "state" else ["state", "district"]
        grouped = enrol.groupby(group_cols)

        rows = []
        for key, frame in grouped:
            totals = frame[["age_0_5", "age_5_17", "age_18_greater"]].sum()
            total_activity = totals.sum()
            adult_share = (totals["age_18_greater"] / total_activity) if total_activity else 0

            monthly = frame.set_index("date")["age_18_greater"].resample("M").sum()
            growth_pct = calc_growth(monthly)

            if isinstance(key, tuple):
                state_name, district_name = key
                name = f"{district_name}, {state_name}"
                identifier = district_name
            else:
                name = key
                identifier = key

            rows.append(
                {
                    "id": identifier,
                    "state": key[0] if isinstance(key, tuple) else key,
                    "name": name,
                    "migrationProxy": round(adult_share * 100, 2),
                    "growthPct": growth_pct,
                    "totalActivity": int(total_activity),
                }
            )

        rows = sorted(rows, key=lambda r: r["migrationProxy"], reverse=True)
        return rows

    def comparisons(
        self, state: Optional[str], district: Optional[str], preset: Optional[str], start: Optional[str], end: Optional[str]
    ) -> Dict[str, List[Dict[str, object]]]:
        data = self.map_view(state, district, preset, start, end, level="state")
        top_states = data[:12]
        scatter = [
            {
                "state": row["state"],
                "growthPct": row["growthPct"],
                "totalActivity": row["totalActivity"],
                "migrationProxy": row["migrationProxy"],
            }
            for row in data
        ]
        return {"states": top_states, "scatter": scatter}

    def insights(
        self, state: Optional[str], district: Optional[str], preset: Optional[str], start: Optional[str], end: Optional[str]
    ) -> List[str]:
        data = self.map_view(state, district, preset, start, end, level="state")
        if not data:
            return ["No data available for the selected filters."]

        top_growth = sorted(data, key=lambda r: r["growthPct"], reverse=True)[:3]
        top_intensity = data[:3]

        insights = []
        insights.append(
            f"Working-age Aadhaar activity shows strongest intensity in {', '.join([r['state'] for r in top_intensity])}."
        )
        insights.append(
            f"Fastest recent growth in adult activity: {', '.join([r['state'] for r in top_growth])}."
        )

        high_signal = [r for r in data if r["migrationProxy"] >= 55]
        if high_signal:
            insights.append(
                f"{len(high_signal)} states exceed the 55% adult-activity proxy threshold, suggesting elevated migration pull factors."
            )
        return insights


store = DataStore()

app = FastAPI(
    title="UIDAI Migration & Urbanization Tracker API",
    description="Data API powering the migration and urbanization dashboard.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, object]:
    return {
        "status": "ok",
        "lastRefreshed": store.last_refreshed.isoformat(),
        "health": store.health,
    }


@app.get("/meta")
def meta() -> Dict[str, object]:
    return {
        "states": list(store.state_to_district.keys()),
        "districts": store.state_to_district,
        "minDate": store.min_date.date().isoformat() if store.min_date is not pd.NaT else None,
        "maxDate": store.max_date.date().isoformat() if store.max_date is not pd.NaT else None,
        "quickPresets": {
            "lastMonth": "1m",
            "last3Months": "3m",
            "last6Months": "6m",
            "lastYear": "1y",
        },
    }


@app.get("/summary")
def summary(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    preset: Optional[str] = Query(default="3m"),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
) -> Dict[str, object]:
    return store.summary(state, district, preset, start, end)


@app.get("/timeseries")
def timeseries(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    preset: Optional[str] = Query(default="6m"),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    granularity: str = Query(default="monthly", regex="^(monthly|quarterly|yearly)$"),
) -> List[Dict[str, object]]:
    return store.working_age_timeseries(state, district, preset, start, end, granularity)


@app.get("/map")
def map_view(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    preset: Optional[str] = Query(default="6m"),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
    level: str = Query(default="state", regex="^(state|district)$"),
) -> List[Dict[str, object]]:
    return store.map_view(state, district, preset, start, end, level)


@app.get("/comparisons")
def comparisons(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    preset: Optional[str] = Query(default="6m"),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
) -> Dict[str, List[Dict[str, object]]]:
    return store.comparisons(state, district, preset, start, end)


@app.get("/insights")
def insights(
    state: Optional[str] = Query(default=None),
    district: Optional[str] = Query(default=None),
    preset: Optional[str] = Query(default="3m"),
    start: Optional[str] = Query(default=None),
    end: Optional[str] = Query(default=None),
) -> List[str]:
    return store.insights(state, district, preset, start, end)

