"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { fetchCompany } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate, formatMoney, remoteLabel, scoreTone, stageLabel } from "@/lib/utils";

function ScoreBreakdown({ breakdown }: { breakdown: Record<string, number> }) {
  const rows = Object.entries(breakdown).filter(([key]) => !["raw_score", "normalized_score"].includes(key));
  return (
    <div className="space-y-2">
      {rows.map(([key, value]) => (
        <div key={key} className="flex items-center justify-between text-sm">
          <span className="capitalize text-slate-600">{key.replaceAll("_", " ")}</span>
          <span className="font-medium text-emerald-700">+{value}</span>
        </div>
      ))}
      <div className="flex items-center justify-between border-t pt-2 text-sm font-semibold">
        <span>Normalized score</span>
        <span>{breakdown.normalized_score ?? 0}/100</span>
      </div>
    </div>
  );
}

export default function CompanyDetailPage() {
  const params = useParams<{ slug: string }>();
  const company = useQuery({ queryKey: ["company", params.slug], queryFn: () => fetchCompany(params.slug) });
  if (company.isLoading) return <div className="text-sm text-muted-foreground">Loading company…</div>;
  if (company.isError || !company.data) return <div>Company not found.</div>;
  const c = company.data;
  const techs = [
    ...c.programming_languages,
    ...c.frontend_technologies,
    ...c.backend_technologies,
    ...c.frameworks,
    ...c.databases,
    ...c.cloud_providers,
    ...c.ai_technologies,
    ...c.devops_technologies,
  ].filter((item, index, all) => all.indexOf(item) === index);

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="text-xs uppercase tracking-wide text-muted-foreground">{c.normalized_domain}</div>
          <h1 className="text-3xl font-semibold tracking-tight">{c.name}</h1>
          <p className="mt-2 max-w-2xl text-slate-600">{c.description || c.short_description}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Badge>{stageLabel(c.funding_stage)}</Badge>
            <Badge>{remoteLabel(c.remote_policy)}</Badge>
            {c.primary_industry ? <Badge>{c.primary_industry}</Badge> : null}
            {c.hiring_engineers ? <Badge className="border-emerald-200 bg-emerald-50">Hiring engineers</Badge> : null}
          </div>
        </div>
        <div className={`rounded-2xl border px-4 py-3 text-center ${scoreTone(c.opportunity_score)}`}>
          <div className="text-3xl font-semibold">{c.opportunity_score}</div>
          <div className="text-xs">Opportunity score</div>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {c.website_url ? (
          <Button asChild>
            <a href={c.website_url} target="_blank" rel="noreferrer">
              Website
            </a>
          </Button>
        ) : null}
        {c.careers_url ? (
          <Button asChild variant="outline">
            <a href={c.careers_url} target="_blank" rel="noreferrer">
              Careers
            </a>
          </Button>
        ) : null}
        {c.jobs_url ? (
          <Button asChild variant="outline">
            <a href={c.jobs_url} target="_blank" rel="noreferrer">
              Jobs
            </a>
          </Button>
        ) : null}
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Founding</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div>Founded {formatDate(c.founded_date)}</div>
            <div>Age {c.company_age_days ?? "—"} days</div>
            <div>
              {c.headquarters_city ? `${c.headquarters_city}, ` : ""}
              {c.headquarters_country || "Unknown HQ"}
            </div>
            <div>Employees {c.employee_range || "—"}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Funding</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div>Stage {stageLabel(c.funding_stage)}</div>
            <div>Latest {formatMoney(c.latest_funding_usd || c.latest_funding_amount)} on {formatDate(c.latest_funding_date)}</div>
            <div>Total {formatMoney(c.total_funding_usd)}</div>
            <div>{c.number_of_funding_rounds} round(s)</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Hiring</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1 text-sm">
            <div>{c.open_job_count} open jobs</div>
            <div>{c.engineering_job_count} engineering jobs</div>
            <div>Velocity {c.hiring_velocity}</div>
            <div>Careers page {c.careers_page_available ? "yes" : "no"}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Remote policy</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="font-medium">{remoteLabel(c.remote_policy)}</div>
          <p className="text-slate-600">{c.remote_policy_text || "No remote policy text captured."}</p>
          {c.remote_evidence_url ? (
            <a className="text-emerald-700 hover:underline" href={c.remote_evidence_url} target="_blank" rel="noreferrer">
              Evidence
            </a>
          ) : null}
          <div className="text-xs text-muted-foreground">Confidence {c.remote_confidence ?? "n/a"}</div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Funding history</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {(c.funding_rounds || []).length === 0 ? <div className="text-sm text-muted-foreground">No rounds stored.</div> : null}
            {(c.funding_rounds || []).map((round) => (
              <div key={round.id} className="rounded-lg border p-3 text-sm">
                <div className="font-medium">
                  {stageLabel(round.round_type)} · {formatMoney(round.amount_usd || round.amount, round.currency || "USD")}
                </div>
                <div className="text-muted-foreground">{formatDate(round.announced_date)}</div>
                <div>{(round.investors || []).join(", ")}</div>
              </div>
            ))}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Investors</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {(c.investor_records || []).map((investor) => (
              <div key={investor.id} className="flex items-center justify-between text-sm">
                <span>
                  {investor.investor_name}
                  {investor.is_lead ? " · lead" : ""}
                </span>
                {investor.notable ? <Badge>Notable</Badge> : null}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Open jobs</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {(c.jobs || []).filter((job) => job.active).map((job) => (
            <div key={job.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border p-3 text-sm">
              <div>
                <div className="font-medium">{job.title}</div>
                <div className="text-muted-foreground">
                  {job.role_category || "engineering"} · {job.location || "n/a"} · {job.remote_type || "unknown"}
                </div>
              </div>
              {job.job_url ? (
                <a className="text-emerald-700 hover:underline" href={job.job_url} target="_blank" rel="noreferrer">
                  Open role
                </a>
              ) : null}
            </div>
          ))}
          {(c.jobs || []).filter((job) => job.active).length === 0 ? (
            <div className="text-sm text-muted-foreground">No active jobs stored.</div>
          ) : null}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Technology stack</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {techs.length ? techs.map((tech) => <Badge key={tech}>{tech}</Badge>) : <span className="text-sm text-muted-foreground">No evidenced technologies yet.</span>}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Why this score</CardTitle>
          </CardHeader>
          <CardContent>
            <ScoreBreakdown breakdown={c.opportunity_score_breakdown || {}} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Discovery sources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>First source: {c.first_source || "—"}</div>
            <div>Sources: {(c.discovery_sources || []).join(", ") || "—"}</div>
            <div>Last updated: {formatDate(c.last_updated_at)}</div>
            {(c.sources || []).map((source) => (
              <div key={source.id} className="rounded-md border p-2">
                <div className="font-medium">{source.source_name}</div>
                {source.source_url ? (
                  <a className="break-all text-emerald-700 hover:underline" href={source.source_url} target="_blank" rel="noreferrer">
                    {source.source_url}
                  </a>
                ) : null}
              </div>
            ))}
            <div className="flex flex-wrap gap-2">
              {[c.linkedin_url, c.github_url, c.twitter_url, c.yc_url, c.product_hunt_url]
                .filter(Boolean)
                .map((url) => (
                  <a key={url as string} className="text-emerald-700 hover:underline" href={url as string} target="_blank" rel="noreferrer">
                    {url}
                  </a>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
