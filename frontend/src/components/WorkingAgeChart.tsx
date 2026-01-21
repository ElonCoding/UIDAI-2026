import React, { useMemo } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar,
} from "recharts";
import { TimeseriesPoint } from "@/types";
import { downloadCsv } from "@/utils/format";

interface Props {
  data: TimeseriesPoint[];
}

const WorkingAgeChart: React.FC<Props> = ({ data }) => {
  const exportCsv = () => downloadCsv(data, "working-age-timeseries.csv");

  const chartData = useMemo(() => data ?? [], [data]);

  return (
    <div className="panel" id="working-age">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <p className="badge">Working-Age Migration Signal (Proxy)</p>
          <h3>Adult Share of Aadhaar Activity</h3>
          <p className="subtitle">18+ activity as % of total, across selected geography & window.</p>
        </div>
        <div className="export-actions">
          <button className="ghost-button" onClick={exportCsv}>
            Export CSV
          </button>
        </div>
      </div>

      <div className="chart-row">
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="grad1" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="5%" stopColor="#2ac3d6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#2ac3d6" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fill: "#9fb0d0", fontSize: 12 }} />
              <YAxis
                tickFormatter={(v) => `${v}%`}
                tick={{ fill: "#9fb0d0", fontSize: 12 }}
                domain={[0, 100]}
              />
              <Tooltip
                contentStyle={{ background: "#0f1426", border: "1px solid rgba(255,255,255,0.08)" }}
                formatter={(value: number) => [`${value}%`, "Adult Share"]}
              />
              <Area
                type="monotone"
                dataKey="adultShare"
                stroke="#2ac3d6"
                fill="url(#grad1)"
                strokeWidth={2}
                name="Adult Share %"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fill: "#9fb0d0", fontSize: 12 }} />
              <YAxis tickFormatter={(v) => v.toLocaleString()} tick={{ fill: "#9fb0d0", fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: "#0f1426", border: "1px solid rgba(255,255,255,0.08)" }}
                formatter={(value: number) => [value.toLocaleString(), "Total Activity"]}
              />
              <Legend />
              <Bar dataKey="totalActivity" fill="#f59f00" name="Total Aadhaar Activity" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default WorkingAgeChart;

