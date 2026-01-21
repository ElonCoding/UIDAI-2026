export type TimePreset = "1m" | "3m" | "6m" | "1y" | "custom";

export interface Filters {
  state?: string | null;
  district?: string | null;
  ageGroup?: "18_plus" | "all";
  timePreset: TimePreset;
  startDate?: string | null;
  endDate?: string | null;
  granularity: "monthly" | "quarterly" | "yearly";
}

export interface SummaryResponse {
  totalActivity: number;
  adultSharePct: number;
  statesSignal: number;
  averageGrowth: number;
  statesCovered: number;
  window: { start: string; end: string };
  lastRefreshed: string;
}

export interface MetaResponse {
  states: string[];
  districts: Record<string, string[]>;
  minDate: string | null;
  maxDate: string | null;
  quickPresets: Record<string, string>;
}

export interface TimeseriesPoint {
  date: string;
  adultShare: number;
  totalActivity: number;
}

export interface MapFeatureDatum {
  id: string;
  state: string;
  name: string;
  migrationProxy: number;
  growthPct: number;
  totalActivity: number;
}

export interface ComparisonsResponse {
  states: MapFeatureDatum[];
  scatter: {
    state: string;
    growthPct: number;
    totalActivity: number;
    migrationProxy: number;
  }[];
}

