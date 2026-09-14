export type CompanyCard = {
  id: string;
  slug: string;
  name: string;
  logo_url?: string | null;
  website_url?: string | null;
  normalized_domain?: string | null;
  careers_url?: string | null;
  jobs_url?: string | null;
  short_description?: string | null;
  headquarters_country?: string | null;
  headquarters_city?: string | null;
  founded_date?: string | null;
  employee_range?: string | null;
  funding_stage?: string | null;
  latest_funding_amount?: number | null;
  latest_funding_usd?: number | null;
  latest_funding_currency?: string | null;
  latest_funding_date?: string | null;
  investors: string[];
  remote_policy?: string | null;
  engineering_job_count: number;
  open_job_count: number;
  opportunity_score: number;
  growth_score: number;
  is_hiring: boolean;
  hiring_engineers: boolean;
  first_discovered_at?: string | null;
  first_source?: string | null;
  primary_industry?: string | null;
};

export type Job = {
  id: string;
  company_id: string;
  title: string;
  department?: string | null;
  role_category?: string | null;
  seniority?: string | null;
  employment_type?: string | null;
  location?: string | null;
  remote_type?: string | null;
  job_url?: string | null;
  source?: string | null;
  posted_date?: string | null;
  active: boolean;
  company_name?: string | null;
  company_slug?: string | null;
};

export type FundingRound = {
  id: string;
  round_type?: string | null;
  amount?: number | null;
  currency?: string | null;
  amount_usd?: number | null;
  announced_date?: string | null;
  investors: string[];
  lead_investors: string[];
  source?: string | null;
  source_url?: string | null;
};

export type Investor = {
  id: string;
  investor_name: string;
  investor_type?: string | null;
  notable: boolean;
  is_lead?: boolean | null;
};

export type CompanySource = {
  id: string;
  source_name: string;
  source_url?: string | null;
  external_id?: string | null;
  first_seen_at: string;
  last_seen_at: string;
  confidence?: number | null;
};

export type CompanyDetail = CompanyCard & {
  description?: string | null;
  linkedin_url?: string | null;
  github_url?: string | null;
  twitter_url?: string | null;
  crunchbase_url?: string | null;
  product_hunt_url?: string | null;
  wellfound_url?: string | null;
  yc_url?: string | null;
  source_urls: string[];
  headquarters_region?: string | null;
  headquarters_continent?: string | null;
  founded_year?: number | null;
  company_age_days?: number | null;
  total_funding_usd?: number | null;
  number_of_funding_rounds: number;
  investor_count: number;
  notable_investor_count: number;
  employee_count_min?: number | null;
  employee_count_max?: number | null;
  estimated_employee_count?: number | null;
  founders: string[];
  industries: string[];
  business_model: string[];
  frontend_technologies: string[];
  backend_technologies: string[];
  databases: string[];
  cloud_providers: string[];
  ai_technologies: string[];
  devops_technologies: string[];
  programming_languages: string[];
  frameworks: string[];
  tech_stack_confidence?: number | null;
  remote_policy_text?: string | null;
  remote_regions: string[];
  remote_confidence?: number | null;
  remote_evidence_url?: string | null;
  hiring_status?: string | null;
  careers_page_available: boolean;
  jobs_added_last_7_days: number;
  hiring_velocity: number;
  funding_recency_days?: number | null;
  opportunity_score_breakdown: Record<string, number>;
  discovery_sources: string[];
  last_updated_at?: string | null;
  funding_rounds: FundingRound[];
  jobs: Job[];
  investor_records: Investor[];
  sources: CompanySource[];
};

export type Paginated<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

export type Stats = {
  companies_discovered_today: number;
  companies_discovered_this_week: number;
  companies_funded_this_week: number;
  recently_founded: number;
  global_remote: number;
  hiring_engineers: number;
  engineering_jobs: number;
  average_opportunity_score: number;
  total_companies: number;
};

export type Source = {
  name: string;
  category: string;
  enabled: boolean;
  description: string;
  requires?: string | null;
  last_run?: ScrapeRun | null;
};

export type ScrapeRun = {
  id: string;
  source: string;
  started_at: string;
  completed_at?: string | null;
  status: string;
  records_found: number;
  records_created: number;
  records_updated: number;
  duplicate_records: number;
  errors: string[];
  duration_seconds?: number | null;
};

export type SavedView = {
  id: string;
  name: string;
  description?: string | null;
  filters: Record<string, string | number | boolean>;
};

export type CompanyQuery = Record<string, string | number | boolean | undefined>;
