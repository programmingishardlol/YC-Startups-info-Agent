import "server-only";

import type { StartupReport } from "@/lib/types";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

async function fetchStartupReport(path: string): Promise<StartupReport> {
  const apiBaseUrl = process.env.API_BASE_URL ?? DEFAULT_API_BASE_URL;
  const response = await fetch(`${apiBaseUrl}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Backend request failed with status ${response.status}.`);
  }

  return (await response.json()) as StartupReport;
}

export async function getLatestStartupReport(): Promise<StartupReport> {
  return fetchStartupReport("/api/v1/startups/latest-enriched");
}

export async function getCurrentBatchStartupReport(limit = 200): Promise<StartupReport> {
  return fetchStartupReport(`/api/v1/startups/current-batch-enriched?limit=${limit}`);
}
