import api from "./client";
import {
  ComparisonsResponse,
  Filters,
  MapFeatureDatum,
  MetaResponse,
  SummaryResponse,
  TimeseriesPoint,
} from "@/types";

const mapFiltersToParams = (filters: Filters) => {
  const params: Record<string, string> = {
    preset: filters.timePreset,
    granularity: filters.granularity,
  };

  if (filters.state) params.state = filters.state;
  if (filters.district) params.district = filters.district;
  if (filters.timePreset === "custom") {
    if (filters.startDate) params.start = filters.startDate;
    if (filters.endDate) params.end = filters.endDate;
  }
  return params;
};

const mapFiltersToParamsWithoutGranularity = (filters: Filters) => {
  const params: Record<string, string> = {
    preset: filters.timePreset,
  };

  if (filters.state) params.state = filters.state;
  if (filters.district) params.district = filters.district;
  if (filters.timePreset === "custom") {
    if (filters.startDate) params.start = filters.startDate;
    if (filters.endDate) params.end = filters.endDate;
  }
  return params;
};

export const fetchMeta = async (): Promise<MetaResponse> => {
  const { data } = await api.get<MetaResponse>("/meta");
  return data;
};

export const fetchSummary = async (filters: Filters): Promise<SummaryResponse> => {
  const { data } = await api.get<SummaryResponse>("/summary", {
    params: mapFiltersToParamsWithoutGranularity(filters),
  });
  return data;
};

export const fetchTimeseries = async (filters: Filters): Promise<TimeseriesPoint[]> => {
  const { data } = await api.get<TimeseriesPoint[]>("/timeseries", {
    params: mapFiltersToParams(filters),
  });
  return data;
};

export const fetchMap = async (filters: Filters, level: "state" | "district"): Promise<MapFeatureDatum[]> => {
  const { data } = await api.get<MapFeatureDatum[]>("/map", {
    params: { ...mapFiltersToParamsWithoutGranularity(filters), level },
  });
  return data;
};

export const fetchComparisons = async (filters: Filters): Promise<ComparisonsResponse> => {
  const { data } = await api.get<ComparisonsResponse>("/comparisons", {
    params: mapFiltersToParamsWithoutGranularity(filters),
  });
  return data;
};

export const fetchInsights = async (filters: Filters): Promise<string[]> => {
  const { data } = await api.get<string[]>("/insights", {
    params: mapFiltersToParamsWithoutGranularity(filters),
  });
  return data;
};

