import React, { useEffect, useMemo, useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import { Feature, FeatureCollection, GeoJsonObject } from "geojson";
import { MapFeatureDatum } from "@/types";
import { downloadCsv } from "@/utils/format";

interface Props {
  data: MapFeatureDatum[];
  level: "state" | "district";
}

const gradientStops = [
  { value: 20, color: "#0ea5e9" },
  { value: 40, color: "#14b8a6" },
  { value: 60, color: "#f59f00" },
  { value: 80, color: "#ef4444" },
];

const GeoMap: React.FC<Props> = ({ data, level }) => {
  const [geojson, setGeojson] = useState<FeatureCollection | null>(null);

  useEffect(() => {
    fetch("/india_states.geo.json")
      .then((res) => res.json())
      .then((json: FeatureCollection) => setGeojson(json))
      .catch(() => setGeojson(null));
  }, []);

  const exportCsv = () => downloadCsv(data, `${level}-map.csv`);

  const featureStyle = (feature: Feature<GeoJsonObject, any>) => {
    const name = (feature.properties?.NAME_1 as string)?.replaceAll("_", " ");
    const match = data.find((d) => d.state === name);
    const value = match?.migrationProxy ?? 0;
    const color = gradientStops.find((stop) => value <= stop.value)?.color ?? "#ef4444";
    return {
      fillColor: color,
      weight: 1,
      opacity: 1,
      color: "rgba(255,255,255,0.25)",
      fillOpacity: 0.7,
    };
  };

  const onEachFeature = (feature: Feature, layer: any) => {
    const name = (feature.properties?.NAME_1 as string)?.replaceAll("_", " ");
    const match = data.find((d) => d.state === name);
    const content = match
      ? `${match.name}<br/>Migration Proxy: ${match.migrationProxy}%<br/>Growth: ${match.growthPct}%`
      : `${name}<br/>No data`;
    layer.bindTooltip(content, { sticky: true });
  };

  const center = useMemo(() => ({ lat: 23.5, lng: 82.5 }), []);

  return (
    <div className="panel" id="map">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <p className="badge">Geographic Visualization</p>
          <h3>Migration Intensity Choropleth</h3>
          <p className="subtitle">Hover for migration proxy & growth; click for drilldowns.</p>
        </div>
        <div className="export-actions">
          <button className="ghost-button" onClick={exportCsv}>
            Export CSV
          </button>
        </div>
      </div>

      <div style={{ height: 420, borderRadius: 12, overflow: "hidden", marginTop: 8 }}>
        <MapContainer center={center} zoom={4.3} style={{ height: "100%", width: "100%" }} zoomControl={false}>
          <TileLayer
            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {geojson && <GeoJSON data={geojson as any} style={featureStyle} onEachFeature={onEachFeature} />}
        </MapContainer>
      </div>

      <div className="map-legend">
        <span>Low</span>
        <div className="legend-gradient" />
        <span>High</span>
      </div>
    </div>
  );
};

export default GeoMap;

