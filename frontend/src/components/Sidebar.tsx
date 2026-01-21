import React from "react";
import { Filters, MetaResponse, TimePreset } from "@/types";

interface SidebarProps {
  meta?: MetaResponse;
  filters: Filters;
  onChange: (next: Partial<Filters>) => void;
  activeSection: string;
  onNavigate: (id: string) => void;
}

const presetOptions: { label: string; value: TimePreset }[] = [
  { label: "Last Month", value: "1m" },
  { label: "Last 3 Months", value: "3m" },
  { label: "Last 6 Months", value: "6m" },
  { label: "Last Year", value: "1y" },
  { label: "Custom", value: "custom" },
];

const Sidebar: React.FC<SidebarProps> = ({ meta, filters, onChange, activeSection, onNavigate }) => {
  const districts = filters.state ? meta?.districts?.[filters.state] ?? [] : [];

  return (
    <aside className="sidebar">
      <div className="nav-links">
        {["overview", "state", "district", "age"].map((id) => (
          <button
            key={id}
            className={`nav-link ${activeSection === id ? "active" : ""}`}
            onClick={() => onNavigate(id)}
          >
            {id === "overview" && "India Overview"}
            {id === "state" && "State Deep Dive"}
            {id === "district" && "District Drilldown"}
            {id === "age" && "Age Migration Analysis"}
          </button>
        ))}
      </div>

      <hr className="divider" />
      <div className="controls">
        <div className="group">
          <label>State</label>
          <select
            value={filters.state ?? ""}
            onChange={(e) => onChange({ state: e.target.value || null, district: null })}
          >
            <option value="">All India</option>
            {meta?.states?.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>

        <div className="group">
          <label>District</label>
          <select
            value={filters.district ?? ""}
            disabled={!filters.state}
            onChange={(e) => onChange({ district: e.target.value || null })}
          >
            <option value="">All Districts</option>
            {districts.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        <div className="group">
          <label>Age Lens</label>
          <select value={filters.ageGroup} onChange={(e) => onChange({ ageGroup: e.target.value as Filters["ageGroup"] })}>
            <option value="all">All Ages</option>
            <option value="18_plus">18+ (Working Age)</option>
          </select>
        </div>

        <div className="group">
          <label>Time Window</label>
          <select
            value={filters.timePreset}
            onChange={(e) => onChange({ timePreset: e.target.value as TimePreset })}
          >
            {presetOptions.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        {filters.timePreset === "custom" && (
          <>
            <div className="group">
              <label>Start date</label>
              <input
                type="date"
                value={filters.startDate ?? ""}
                min={meta?.minDate ?? undefined}
                max={filters.endDate ?? meta?.maxDate ?? undefined}
                onChange={(e) => onChange({ startDate: e.target.value })}
              />
            </div>
            <div className="group">
              <label>End date</label>
              <input
                type="date"
                value={filters.endDate ?? ""}
                min={filters.startDate ?? meta?.minDate ?? undefined}
                max={meta?.maxDate ?? undefined}
                onChange={(e) => onChange({ endDate: e.target.value })}
              />
            </div>
          </>
        )}

        <div className="group">
          <label>Period Granularity</label>
          <select
            value={filters.granularity}
            onChange={(e) => onChange({ granularity: e.target.value as Filters["granularity"] })}
          >
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

