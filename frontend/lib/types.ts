export type StartupReport = {
  yc_batch: string;
  count: number;
  companies: StartupCompany[];
  sources: string[];
};

export type SeenStartupHistoryItem = {
  company: StartupCompany;
  last_shown_at: string | null;
  shown_count: number;
};

export type StartupCompany = {
  overview: {
    company_name: string;
    yc_batch: string;
    launched_at: number | null;
    description: string | null;
    website: string | null;
    location: string | null;
    company_url: string;
  };
  research: {
    problem: string | null;
    solution: string | null;
    market_category: string | null;
    market_definition: string | null;
    target_customer: string | null;
    market_size_estimate: string | null;
    market_size_reasoning: string | null;
    tam_estimate_usd: number | null;
    sam_estimate_usd: number | null;
    som_estimate_usd: number | null;
  };
  founders: Array<{
    name: string;
    title: string | null;
    background_summary: string | null;
  }>;
  launch_post: {
    title: string;
    tagline: string | null;
    url: string;
    created_at: string | null;
  } | null;
};
