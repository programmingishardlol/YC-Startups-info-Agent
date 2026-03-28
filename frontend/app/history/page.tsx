import { ArrowLeft, ArrowUpRight, Clock3, Eye } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { getSeenStartupHistory } from "@/lib/startup-store";
import { cn } from "@/lib/utils";

export const dynamic = "force-dynamic";

function formatDate(value: string | null) {
  if (!value) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function text(value: string | null, fallback = "null") {
  return value ?? fallback;
}

export default async function HistoryPage() {
  const items = await getSeenStartupHistory();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
      <section className="relative overflow-hidden rounded-[36px] border border-stone-300/70 bg-white/70 p-8 shadow-[0_32px_120px_-55px_rgba(41,32,24,0.55)] backdrop-blur md:p-10">
        <div className="absolute -left-10 top-0 h-48 w-48 rounded-full bg-amber-200/35 blur-3xl" />
        <div className="relative max-w-4xl">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-4">
              <Badge variant="accent" className="w-fit">
                Startup Memory
              </Badge>
              <h1 className="max-w-3xl font-serif text-5xl font-semibold tracking-tight text-stone-950 sm:text-6xl">
                Startups you have already seen before
              </h1>
              <p className="max-w-2xl text-base leading-8 text-stone-700 sm:text-lg">
                This page helps you remember what previously shown startups do, without changing the 5 currently pinned on the homepage.
              </p>
            </div>
            <a href="/" className={cn(buttonVariants({ variant: "outline" }), "rounded-full")}>
              <ArrowLeft className="h-4 w-4" />
              Back to homepage
            </a>
          </div>
          <div className="mt-8 flex flex-wrap gap-3">
            <div className="rounded-2xl border border-stone-200 bg-stone-50/80 px-4 py-3">
              <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-stone-500">Seen Startups</p>
              <p className="mt-1 text-xl font-semibold text-stone-950">{items.length}</p>
            </div>
          </div>
        </div>
      </section>

      {items.length > 0 ? (
        <section className="grid gap-6">
          {items.map((item) => (
            <Card key={item.company.overview.company_url} className="overflow-hidden">
              <CardHeader className="gap-4 border-b border-stone-200/80 bg-white/50">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="space-y-3">
                    <Badge variant="outline" className="w-fit">
                      {item.company.overview.yc_batch}
                    </Badge>
                    <CardTitle>{item.company.overview.company_name}</CardTitle>
                    <CardDescription className="max-w-3xl text-base text-stone-700">
                      {text(item.company.overview.description, "Description unavailable.")}
                    </CardDescription>
                  </div>
                  <a
                    href={item.company.overview.company_url}
                    target="_blank"
                    rel="noreferrer"
                    className={cn(buttonVariants({ variant: "outline", size: "sm" }), "rounded-full")}
                  >
                    YC page
                    <ArrowUpRight className="h-4 w-4" />
                  </a>
                </div>
              </CardHeader>
              <CardContent className="space-y-6 pt-6">
                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
                    <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">
                      <Clock3 className="h-3.5 w-3.5" />
                      Last Seen
                    </div>
                    <div className="text-sm leading-7 text-stone-800">{formatDate(item.last_shown_at)}</div>
                  </div>
                  <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
                    <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">
                      <Eye className="h-3.5 w-3.5" />
                      Times Shown
                    </div>
                    <div className="text-sm leading-7 text-stone-800">{item.shown_count}</div>
                  </div>
                  <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
                    <div className="mb-1 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Location</div>
                    <div className="text-sm leading-7 text-stone-800">{text(item.company.overview.location)}</div>
                  </div>
                  <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
                    <div className="mb-1 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Website</div>
                    <div className="text-sm leading-7 text-stone-800">
                      {item.company.overview.website ? (
                        <a
                          href={item.company.overview.website}
                          target="_blank"
                          rel="noreferrer"
                          className="underline decoration-stone-300 underline-offset-4"
                        >
                          {item.company.overview.website}
                        </a>
                      ) : (
                        "null"
                      )}
                    </div>
                  </div>
                </div>

                <div className="grid gap-6 lg:grid-cols-2">
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">The Problem</p>
                    <p className="text-sm leading-7 text-stone-800">{text(item.company.research.problem)}</p>
                  </div>
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">The Solution</p>
                    <p className="text-sm leading-7 text-stone-800">{text(item.company.research.solution)}</p>
                  </div>
                </div>

                <Separator />

                <div className="grid gap-6 lg:grid-cols-2">
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Market Category</p>
                    <p className="text-sm leading-7 text-stone-800">{text(item.company.research.market_category)}</p>
                  </div>
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Target Customer</p>
                    <p className="text-sm leading-7 text-stone-800">{text(item.company.research.target_customer)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </section>
      ) : (
        <Card className="overflow-hidden">
          <CardHeader className="gap-3 border-b border-stone-200/80 bg-white/50">
            <Badge variant="outline" className="w-fit">
              No History Yet
            </Badge>
            <CardTitle className="text-3xl">You have not shown any startups yet</CardTitle>
            <CardDescription className="text-base">
              Use the homepage refresh button first. After startups are shown there, they will appear here as historical memory.
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </main>
  );
}
