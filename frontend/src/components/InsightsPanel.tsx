import React from "react";

interface Props {
  insights?: string[];
}

const InsightsPanel: React.FC<Props> = ({ insights }) => {
  return (
    <div className="panel" id="insights">
      <p className="badge">Insights & Interpretation</p>
      <h3>Executive Brief</h3>
      <p className="subtitle">Dynamic notes update with every filter change.</p>
      <ul className="insights-list">
        {insights?.map((item) => (
          <li key={item}>{item}</li>
        )) || <li>No insights available</li>}
      </ul>
    </div>
  );
};

export default InsightsPanel;

