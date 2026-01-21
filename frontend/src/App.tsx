import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import KpiRow from "./components/KpiRow";
import WorkingAgeChart from "./components/WorkingAgeChart";
import GeoMap from "./components/GeoMap";
import ComparisonPanels from "./components/ComparisonPanels";
import InsightsPanel from "./components/InsightsPanel";
import { fetchComparisons, fetchInsights, fetchMap, fetchMeta, fetchSummary, fetchTimeseries } from "./api/dashboard";
import { Filters } from "./types";

const App = () => {
  const [filters, setFilters] = useState<Filters>({
    state: null,
    district: null,
    ageGroup: "18_plus",
    timePreset: "3m",
    startDate: null,
    endDate: null,
    granularity: "monthly",
  });
  const [activeSection, setActiveSection] = useState("overview");

  const metaQuery = useQuery({ queryKey: ["meta"], queryFn: fetchMeta });

  const summaryQuery = useQuery({
    queryKey: ["summary", filters],
    queryFn: () => fetchSummary(filters),
  });

  const timeseriesQuery = useQuery({
    queryKey: ["timeseries", filters],
    queryFn: () => fetchTimeseries(filters),
  });

  const mapLevel = filters.state ? "district" : "state";
  const mapQuery = useQuery({
    queryKey: ["map", filters, mapLevel],
    queryFn: () => fetchMap(filters, mapLevel),
  });

  const comparisonsQuery = useQuery({
    queryKey: ["comparisons", filters],
    queryFn: () => fetchComparisons(filters),
  });

  const insightsQuery = useQuery({
    queryKey: ["insights", filters],
    queryFn: () => fetchInsights(filters),
  });

  const loading =
    summaryQuery.isLoading ||
    timeseriesQuery.isLoading ||
    mapQuery.isLoading ||
    comparisonsQuery.isLoading ||
    insightsQuery.isLoading;

  const subtitle = useMemo(() => {
    if (filters.district) return `${filters.district}, ${filters.state}`;
    if (filters.state) return `${filters.state} | Focus`;
    return "National view";
  }, [filters.state, filters.district]);

  return (
    <div className="app-shell">
      <Sidebar
        meta={metaQuery.data}
        filters={filters}
        activeSection={activeSection}
        onNavigate={setActiveSection}
        onChange={(next) => setFilters((prev) => ({ ...prev, ...next }))}
      />
      <main className="main">
        <Header lastRefreshed={summaryQuery.data?.lastRefreshed} />

        <div className="panel" id="overview">
          <p className="badge">Overall Objective</p>
          <h3>Executive-grade migration intelligence</h3>
          <p className="subtitle">
            Dashboard tracks Aadhaar activity as a proxy for migration & urbanization. Filters and drilldowns update all
            visuals in real time. Current scope: {subtitle}
          </p>
          <KpiRow data={summaryQuery.data} />
        </div>

        <WorkingAgeChart data={timeseriesQuery.data ?? []} />

        <div className="layout-two">
          <GeoMap data={mapQuery.data ?? []} level={mapLevel} />
          <InsightsPanel insights={insightsQuery.data} />
        </div>

        <ComparisonPanels data={comparisonsQuery.data} />

        {loading && <p className="status">Loading latest analytics...</p>}
      </main>
    </div>
  );
};

export default App;

