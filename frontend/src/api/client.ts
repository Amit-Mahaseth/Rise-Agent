import type { DashboardResponse } from "../types/dashboard";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export async function fetchDashboardSummary(): Promise<DashboardResponse> {
  const response = await fetch(`${API_BASE_URL}/dashboard/summary`);
  if (!response.ok) {
    throw new Error(`Failed to fetch dashboard summary: ${response.status}`);
  }
  return response.json() as Promise<DashboardResponse>;
}

