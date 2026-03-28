import { NextRequest, NextResponse } from "next/server";

import { refreshStartupCatalog } from "@/lib/startup-store";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const configuredSecret = process.env.CRON_SECRET;
  const suppliedSecret =
    request.headers.get("x-cron-secret") ??
    request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ??
    request.nextUrl.searchParams.get("secret");

  if (!configuredSecret || suppliedSecret !== configuredSecret) {
    return NextResponse.json({ error: "Unauthorized cron request." }, { status: 401 });
  }

  const result = await refreshStartupCatalog();
  return NextResponse.json(result);
}
