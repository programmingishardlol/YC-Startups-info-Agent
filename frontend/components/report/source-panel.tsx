import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function SourcePanel({ sources }: { sources: string[] }) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="border-b border-stone-200/80 bg-white/50">
        <Badge variant="outline" className="w-fit">
          Source Trail
        </Badge>
        <CardTitle className="text-2xl">Grounding links used in this run</CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="grid gap-3 md:grid-cols-2">
          {sources.map((source) => (
            <a
              key={source}
              href={source}
              target="_blank"
              rel="noreferrer"
              className="group flex items-start justify-between gap-3 rounded-2xl border border-stone-200 bg-stone-50/80 px-4 py-3 text-sm text-stone-700 transition hover:border-stone-300 hover:bg-white"
            >
              <span className="break-all leading-6">{source}</span>
              <ArrowUpRight className="mt-1 h-4 w-4 shrink-0 text-stone-400 transition group-hover:text-stone-800" />
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
