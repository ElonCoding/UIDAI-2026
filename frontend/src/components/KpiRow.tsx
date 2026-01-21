import React from "react";
import { SummaryResponse } from "@/types";
import { formatNumber, formatPercent } from "@/utils/format";

interface Props {
  data?: SummaryResponse;
}

const KpiRow: React.FC<Props> = ({ data }) => {
  const kpis = [
    {
      label: "Total Aadhaar Activity",
      value: data ? formatNumber(data.totalActivity) : "—",
      trend: data ? `Working-age share: ${formatPercent(data.adultSharePct)}` : "",
    },
    {
      label: "% States Showing Migration Signal",
      value: data ? `${data.statesSignal.toFixed(1)}%` : "—",
      trend: "Threshold >52% adult share",
    },
    {
      label: "Average Growth %",
      value: data ? `${data.averageGrowth.toFixed(1)}%` : "—",
      trend: data ? `Window ${data.window.start} → ${data.window.end}` : "",
    },
    {
      label: "States / UTs Covered",
      value: data ? data.statesCovered : "—",
      trend: data ? `Updated ${new Date(data.lastRefreshed).toLocaleDateString()}` : "",
    },
  ];

  return (
    <div className="kpi-grid">
      {kpis.map((kpi) => (
        <div className="kpi-card" key={kpi.label}>
          <div className="kpi-label">{kpi.label}</div>
          <div className="kpi-value">{kpi.value}</div>
          <div className="kpi-trend">{kpi.trend}</div>
        </div>
      ))}
    </div>
  );
};

export default KpiRow;

