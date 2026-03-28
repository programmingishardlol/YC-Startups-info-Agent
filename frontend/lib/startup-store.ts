import "server-only";

import { randomUUID } from "node:crypto";

import type { Startup, Prisma } from "@prisma/client";

import { getCurrentBatchStartupReport } from "@/lib/api";
import { prisma } from "@/lib/prisma";
import type { SeenStartupHistoryItem, StartupCompany, StartupReport } from "@/lib/types";

const HOMEPAGE_STARTUP_COUNT = 5;
const CURRENT_BATCH_REFRESH_LIMIT = 200;

type StoredStartup = Startup & {
  payload: Prisma.JsonValue;
  sourceUrls: Prisma.JsonValue;
};

export async function getHomepageReport(): Promise<StartupReport> {
  const startups = await getHomepageVisibleStartups(HOMEPAGE_STARTUP_COUNT);

  const companies = startups.map((startup) => startup.payload as StartupCompany);
  const sources = uniqueStrings(
    startups.flatMap((startup) => jsonStringArray(startup.sourceUrls)),
  );

  return {
    yc_batch: companies[0]?.overview.yc_batch ?? (await getLatestKnownBatch()) ?? "Unknown",
    count: companies.length,
    companies,
    sources,
  };
}

export async function refreshHomepageSelection(): Promise<{ changed: boolean; count: number }> {
  let startups = await getUnseenStartups(HOMEPAGE_STARTUP_COUNT);

  if (startups.length < HOMEPAGE_STARTUP_COUNT) {
    await refreshStartupCatalog();
    startups = await getUnseenStartups(HOMEPAGE_STARTUP_COUNT);
  }

  if (!startups.length) {
    return { changed: false, count: 0 };
  }

  await setHomepageVisibleStartups(startups.map((startup) => startup.id));
  return { changed: true, count: startups.length };
}

export async function refreshStartupCatalog(): Promise<{ ycBatch: string; refreshedCount: number }> {
  const report = await getCurrentBatchStartupReport(CURRENT_BATCH_REFRESH_LIMIT);
  const now = new Date();

  await prisma.$transaction(async (tx) => {
    await tx.startup.updateMany({
      where: { ycBatch: report.yc_batch },
      data: { isActive: false, lastRefreshedAt: now },
    });

    for (const company of report.companies) {
      const slug = startupSlug(company.overview.company_url);
      await tx.startup.upsert({
        where: { slug },
        update: {
          companyName: company.overview.company_name,
          ycBatch: company.overview.yc_batch,
          companyUrl: company.overview.company_url,
          launchedAt: company.overview.launched_at,
          website: company.overview.website,
          location: company.overview.location,
          isActive: true,
          payload: company,
          sourceUrls: buildStartupSources(report, company),
          lastRefreshedAt: now,
        },
        create: {
          slug,
          companyName: company.overview.company_name,
          ycBatch: company.overview.yc_batch,
          companyUrl: company.overview.company_url,
          launchedAt: company.overview.launched_at,
          website: company.overview.website,
          location: company.overview.location,
          isActive: true,
          payload: company,
          sourceUrls: buildStartupSources(report, company),
          discoveredAt: now,
          lastRefreshedAt: now,
        },
      });
    }
  });

  return {
    ycBatch: report.yc_batch,
    refreshedCount: report.companies.length,
  };
}

export async function getSeenStartupHistory(limit = 200): Promise<SeenStartupHistoryItem[]> {
  const groupedViews = await prisma.startupView.groupBy({
    by: ["startupId"],
    _count: { _all: true },
    _max: { shownAt: true },
    orderBy: {
      _max: {
        shownAt: "desc",
      },
    },
    take: limit,
  });

  if (!groupedViews.length) {
    return [];
  }

  const startups = await prisma.startup.findMany({
    where: {
      id: {
        in: groupedViews.map((view) => view.startupId),
      },
    },
  });

  const startupById = new Map(startups.map((startup) => [startup.id, startup]));

  return groupedViews.flatMap((view) => {
    const startup = startupById.get(view.startupId);
    if (!startup) {
      return [];
    }

    return [
      {
        company: startup.payload as StartupCompany,
        last_shown_at: view._max.shownAt?.toISOString() ?? null,
        shown_count: view._count._all,
      },
    ];
  });
}

async function setHomepageVisibleStartups(startupIds: string[]): Promise<void> {
  const requestId = randomUUID();

  await prisma.$transaction(async (tx) => {
    await tx.startup.updateMany({
      data: { isHomepageVisible: false },
    });

    await tx.startup.updateMany({
      where: { id: { in: startupIds } },
      data: { isHomepageVisible: true },
    });

    await tx.startupView.createMany({
      data: startupIds.map((startupId) => ({
        startupId,
        requestId,
        surface: "homepage",
      })),
    });
  });
}

async function getHomepageVisibleStartups(limit: number): Promise<StoredStartup[]> {
  return prisma.startup.findMany({
    where: {
      isActive: true,
      isHomepageVisible: true,
    },
    orderBy: [{ launchedAt: "desc" }, { lastRefreshedAt: "desc" }],
    take: limit,
  });
}

async function getUnseenStartups(limit: number): Promise<StoredStartup[]> {
  return prisma.startup.findMany({
    where: {
      isActive: true,
      views: {
        none: {},
      },
    },
    orderBy: [{ launchedAt: "desc" }, { lastRefreshedAt: "desc" }],
    take: limit,
  });
}

async function getLatestKnownBatch(): Promise<string | null> {
  const latestStartup = await prisma.startup.findFirst({
    where: { isActive: true },
    orderBy: [{ launchedAt: "desc" }, { lastRefreshedAt: "desc" }],
    select: { ycBatch: true },
  });

  return latestStartup?.ycBatch ?? null;
}

function buildStartupSources(report: StartupReport, company: StartupCompany): string[] {
  return uniqueStrings([
    ...report.sources,
    company.overview.company_url,
    company.overview.website ?? "",
    company.launch_post?.url ?? "",
  ]);
}

function startupSlug(companyUrl: string): string {
  return companyUrl.split("/").filter(Boolean).at(-1) ?? companyUrl;
}

function jsonStringArray(value: Prisma.JsonValue): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((item): item is string => typeof item === "string");
}

function uniqueStrings(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))];
}
