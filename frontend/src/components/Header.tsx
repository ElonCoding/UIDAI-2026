import React from "react";

interface HeaderProps {
  lastRefreshed?: string;
}

const Header: React.FC<HeaderProps> = ({ lastRefreshed }) => {
  return (
    <div className="header">
      <div>
        <p className="badge">UIDAI Migration & Urbanization Tracker</p>
        <h1 className="title">Migration Proxy & Urbanization Hotspots</h1>
        <p className="subtitle">Executive-grade situational dashboard for policymakers</p>
      </div>
      {lastRefreshed && (
        <div className="status">
          Data refreshed: <strong>{new Date(lastRefreshed).toLocaleString()}</strong>
        </div>
      )}
    </div>
  );
};

export default Header;

