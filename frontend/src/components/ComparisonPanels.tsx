import React from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis } from "recharts";
import { ComparisonsResponse } from "@/types";
import { downloadCsv, formatNumber } from "@/utils/format";

interface Props {
  data?: ComparisonsResponse;
}

const ComparisonPanels: React.FC<Props> = ({ data }) => {
  const exportBar = () => data && downloadCsv(data.states, "state-comparison.csv");
  const exportScatter = () => data && downloadCsv(data.scatter, "growth-vs-activity.csv");

  return (
    <div className="layout-two">
      <div className="panel" id="state-comparison">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <p className="badge">Comparative Analysis</p>
            <h3>State-wise Migration Signal</h3>
          </div>
          <button className="ghost-button" onClick={exportBar}>
            Export CSV
          </button>
        </div>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.states ?? []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tickFormatter={(v) => `${v}%`} tick={{ fill: "#9fb0d0", fontSize: 12 }} />
              <YAxis dataKey="state" type="category" tick={{ fill: "#9fb0d0", fontSize: 12 }} width={110} />
              <Tooltip
                contentStyle={{ background: "#0f1426", border: "1px solid rgba(255,255,255,0.08)" }}
                formatter={(v: number) => [`${v}%`, "Migration Proxy"]}
              />
              <Bar dataKey="migrationProxy" fill="#2ac3d6" barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="panel" id="scatter">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <p className="badge">Correlation View</p>
            <h3>Growth % vs Aadhaar Activity</h3>
          </div>
          <button className="ghost-button" onClick={exportScatter}>
            Export CSV
          </button>
        </div>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                dataKey="totalActivity"
                name="Total Activity"
                tickFormatter={(v) => formatNumber(v)}
                tick={{ fill: "#9fb0d0", fontSize: 12 }}
              />
              <YAxis
                dataKey="growthPct"
                name="Growth %"
                tickFormatter={(v) => `${v}%`}
                tick={{ fill: "#9fb0d0", fontSize: 12 }}
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                contentStyle={{ background: "#0f1426", border: "1px solid rgba(255,255,255,0.08)" }}
                formatter={(value: number, name: string, props) =>
                  name === "totalActivity" ? [formatNumber(value), "Total Aadhaar Activity"] : [`${value}%`, "Growth %"]
                }
                labelFormatter={(_, payload) => payload?.[0]?.payload?.state}
              />
              <Scatter data={data?.scatter ?? []} fill="#f59f00" />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default ComparisonPanels;

