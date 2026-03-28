import { AlertCircle, ArrowRight, ExternalLink, History, Layers3, RefreshCw } from "lucide-react";

import { refreshHomepageAction } from "@/app/actions";
import { SourcePanel } from "@/components/report/source-panel";
import { StartupCard } from "@/components/report/startup-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getHomepageReport } from "@/lib/startup-store";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  try {
    const report = await getHomepageReport();

    return (
      <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
        <section className="relative overflow-hidden rounded-[36px] border border-stone-300/70 bg-white/70 p-8 shadow-[0_32px_120px_-55px_rgba(41,32,24,0.55)] backdrop-blur md:p-10">
          <div className="absolute -right-16 top-0 h-56 w-56 rounded-full bg-amber-200/40 blur-3xl" />
          <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-orange-200/30 blur-3xl" />
          <div className="relative max-w-4xl">
            <Badge variant="accent" className="w-fit">
              YC Startup Research Agent
            </Badge>
            <h1 className="mt-5 max-w-3xl font-serif text-5xl font-semibold tracking-tight text-stone-950 sm:text-6xl">
              Latest YC startups, redesigned in Next.js.
            </h1>
            <p className="mt-5 max-w-2xl text-base leading-8 text-stone-700 sm:text-lg">
              This frontend reads the existing FastAPI enrichment pipeline and turns it into a cleaner founder-friendly report.
              The homepage stays stable until you click refresh, so reopening the site shows the same 5 startups.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <div className="rounded-2xl border border-stone-200 bg-stone-50/80 px-4 py-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-stone-500">Batch</p>
                <p className="mt-1 text-xl font-semibold text-stone-950">{report.yc_batch}</p>
              </div>
              <div className="rounded-2xl border border-stone-200 bg-stone-50/80 px-4 py-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-stone-500">Companies</p>
                <p className="mt-1 text-xl font-semibold text-stone-950">{report.count}</p>
              </div>
              <div className="rounded-2xl border border-stone-200 bg-stone-50/80 px-4 py-3">
                <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-stone-500">Sources</p>
                <p className="mt-1 text-xl font-semibold text-stone-950">{report.sources.length}</p>
              </div>
              <form action={refreshHomepageAction}>
                <Button type="submit" className="h-[54px] rounded-2xl px-5">
                  <RefreshCw className="h-4 w-4" />
                  Refresh 5 Startups
                </Button>
              </form>
              <a href="/history" className={cn(buttonVariants({ variant: "outline" }), "h-[54px] rounded-2xl px-5")}>
                <History className="h-4 w-4" />
                View Seen Startups
              </a>
            </div>
          </div>
        </section>

        {report.count > 0 ? (
          <section className="grid gap-6">
            {report.companies.map((company) => (
              <StartupCard key={company.overview.company_name} company={company} />
            ))}
          </section>
        ) : (
          <Card className="overflow-hidden">
            <CardHeader className="gap-3 border-b border-stone-200/80 bg-white/50">
              <Badge variant="outline" className="w-fit">
                No Startups Yet
              </Badge>
              <CardTitle className="text-3xl">No homepage startups are stored yet</CardTitle>
              <CardDescription className="text-base">
                Click the refresh button above to load the first set of startups into the homepage.
              </CardDescription>
            </CardHeader>
            <CardContent className="pt-6 text-sm leading-7 text-stone-700">
              After that, the same 5 startups will stay on the homepage until you manually refresh again. The weekly job still updates the catalog in the background.
            </CardContent>
          </Card>
        )}

        <SourcePanel sources={report.sources} />
      </main>
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown frontend error.";

    return (
      <main className="mx-auto flex min-h-screen w-full max-w-4xl items-center px-4 py-10 sm:px-6">
        <Card className="w-full overflow-hidden">
          <CardHeader className="gap-4 border-b border-stone-200/80 bg-white/50">
            <Badge variant="outline" className="w-fit">
              Backend Needed
            </Badge>
            <CardTitle className="flex items-center gap-3 text-3xl">
              <AlertCircle className="h-8 w-8 text-amber-700" />
              The frontend could not load the YC report
            </CardTitle>
            <CardDescription className="text-base">
              Start the FastAPI server and configure the database first, then reload this page. The Next.js UI now expects both
              <code className="mx-1 rounded bg-stone-100 px-1.5 py-0.5 text-sm">API_BASE_URL</code> and
              <code className="mx-1 rounded bg-stone-100 px-1.5 py-0.5 text-sm">DATABASE_URL</code>.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-5 pt-6">
            <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4 text-sm leading-7 text-stone-700">
              <p className="font-medium text-stone-950">Current error</p>
              <p className="mt-2">{message}</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <a
                href="http://127.0.0.1:8000/api/v1/startups/latest-enriched"
                target="_blank"
                rel="noreferrer"
                className={buttonVariants()}
              >
                Open backend JSON
                <ExternalLink className="h-4 w-4" />
              </a>
              <a
                href="http://127.0.0.1:8000"
                target="_blank"
                rel="noreferrer"
                className={buttonVariants({ variant: "outline" })}
              >
                Open existing FastAPI page
                <ArrowRight className="h-4 w-4" />
              </a>
              <div
                className={cn(
                  buttonVariants({ variant: "ghost" }),
                  "cursor-default text-stone-700 hover:bg-transparent",
                )}
              >
                <Layers3 className="h-4 w-4" />
                Set <code>API_BASE_URL</code> if your backend runs elsewhere
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    );
  }
}
