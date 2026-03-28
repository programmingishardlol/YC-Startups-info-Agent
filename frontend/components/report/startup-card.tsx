import { ArrowUpRight, MapPin, Radar, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { StartupCompany } from "@/lib/types";

function currency(value: number | null) {
  if (value === null) {
    return "null";
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function text(value: string | null, fallback = "null") {
  return value ?? fallback;
}

export function StartupCard({ company }: { company: StartupCompany }) {
  return (
    <Card className="relative overflow-hidden">
      <div className="absolute inset-x-0 top-0 h-24 bg-[radial-gradient(circle_at_top_left,_rgba(245,158,11,0.25),transparent_55%)]" />
      <CardHeader className="relative gap-4 pb-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-3">
            <Badge variant="accent" className="w-fit">
              {company.overview.yc_batch}
            </Badge>
            <CardTitle>{company.overview.company_name}</CardTitle>
          </div>
          <a
            href={company.overview.company_url}
            target="_blank"
            rel="noreferrer"
            className={cn(buttonVariants({ variant: "outline", size: "sm" }), "rounded-full")}
          >
            YC page
            <ArrowUpRight className="h-4 w-4" />
          </a>
        </div>
        <CardDescription className="max-w-3xl text-base text-stone-700">
          {text(company.overview.description, "Description unavailable.")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">
              <MapPin className="h-3.5 w-3.5" />
              Location
            </div>
            <div className="text-sm leading-7 text-stone-800">{text(company.overview.location)}</div>
          </div>
          <div className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
            <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">
              <Radar className="h-3.5 w-3.5" />
              Website
            </div>
            <div className="text-sm leading-7 text-stone-800">
              {company.overview.website ? (
                <a href={company.overview.website} target="_blank" rel="noreferrer" className="underline decoration-stone-300 underline-offset-4">
                  {company.overview.website}
                </a>
              ) : (
                "null"
              )}
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <section className="space-y-4">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">The Problem</p>
              <p className="text-sm leading-7 text-stone-800">{text(company.research.problem)}</p>
            </div>
            <Separator />
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">The Solution</p>
              <p className="text-sm leading-7 text-stone-800">{text(company.research.solution)}</p>
            </div>
            <Separator />
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Market Category</p>
                <p className="text-sm leading-7 text-stone-800">{text(company.research.market_category)}</p>
              </div>
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Target Customer</p>
                <p className="text-sm leading-7 text-stone-800">{text(company.research.target_customer)}</p>
              </div>
            </div>
          </section>

          <section className="rounded-[24px] border border-stone-200 bg-stone-50/80 p-5">
            <div className="mb-4 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">
              <Sparkles className="h-4 w-4" />
              Market Snapshot
            </div>
            <div className="space-y-4">
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Estimate</p>
                <p className="text-sm leading-7 text-stone-800">{text(company.research.market_size_estimate)}</p>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Market Definition</p>
                <p className="text-sm leading-7 text-stone-800">{text(company.research.market_definition)}</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-stone-200 bg-white/80 p-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone-500">TAM</p>
                  <p className="mt-2 text-sm font-medium text-stone-900">{currency(company.research.tam_estimate_usd)}</p>
                </div>
                <div className="rounded-2xl border border-stone-200 bg-white/80 p-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone-500">SAM</p>
                  <p className="mt-2 text-sm font-medium text-stone-900">{currency(company.research.sam_estimate_usd)}</p>
                </div>
                <div className="rounded-2xl border border-stone-200 bg-white/80 p-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-stone-500">SOM</p>
                  <p className="mt-2 text-sm font-medium text-stone-900">{currency(company.research.som_estimate_usd)}</p>
                </div>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Reasoning</p>
                <p className="text-sm leading-7 text-stone-800">{text(company.research.market_size_reasoning)}</p>
              </div>
            </div>
          </section>
        </div>

        <Separator />

        <section className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Founders</p>
            <div className="grid gap-3">
              {company.founders.map((founder) => (
                <div key={founder.name} className="rounded-2xl border border-stone-200 bg-stone-50/80 p-4">
                  <p className="text-base font-semibold text-stone-950">{founder.name}</p>
                  <p className="mt-1 text-sm text-stone-500">{text(founder.title, "Title unknown")}</p>
                  <p className="mt-3 text-sm leading-7 text-stone-800">
                    {text(founder.background_summary, "Background summary unavailable.")}
                  </p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">Launch Post</p>
            {company.launch_post ? (
              <div className="rounded-[24px] border border-amber-200 bg-[linear-gradient(135deg,rgba(251,191,36,0.18),rgba(255,255,255,0.86))] p-5">
                <p className="text-lg font-semibold text-stone-950">{company.launch_post.title}</p>
                <p className="mt-3 text-sm leading-7 text-stone-700">{text(company.launch_post.tagline)}</p>
                <a
                  href={company.launch_post.url}
                  target="_blank"
                  rel="noreferrer"
                  className={cn(
                    buttonVariants({ variant: "ghost", size: "sm" }),
                    "mt-4 px-0 text-stone-900 hover:bg-transparent",
                  )}
                >
                  Open launch post
                  <ArrowUpRight className="h-4 w-4" />
                </a>
              </div>
            ) : (
              <div className="rounded-[24px] border border-dashed border-stone-300 bg-stone-50/60 p-5 text-sm leading-7 text-stone-600">
                No public launch post was available for this company in the current YC payload.
              </div>
            )}
          </div>
        </section>
      </CardContent>
    </Card>
  );
}
