"use client";

import Link from "next/link";
import { ExternalLink } from "lucide-react";
import type { CompanyCard } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { daysAgo, formatDate, formatMoney, remoteLabel, scoreTone, stageLabel } from "@/lib/utils";

function Logo({ company }: { company: CompanyCard }) {
  const domain = company.normalized_domain;
  const src = domain ? `https://www.google.com/s2/favicons?domain=${domain}&sz=128` : company.logo_url;
  const initials = company.name.slice(0, 2).toUpperCase();
  return (
    <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-lg border bg-slate-50 text-sm font-semibold text-slate-600">
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={src}
          alt=""
          className="h-8 w-8"
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
      ) : (
        initials
      )}
    </div>
  );
}

export function CompanyCardView({ company }: { company: CompanyCard }) {
  const website = company.website_url;
  const careers = company.careers_url || company.jobs_url;
  return (
    <Card className="flex h-full flex-col">
      <CardContent className="flex h-full flex-col gap-4 pt-5">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <Logo company={company} />
            <div>
              <Link href={`/companies/${company.slug}`} className="font-semibold hover:text-emerald-700">
                {company.name}
              </Link>
              <div className="text-xs text-muted-foreground">{company.normalized_domain || "No website"}</div>
            </div>
          </div>
          <div className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${scoreTone(company.opportunity_score)}`}>
            {company.opportunity_score}
          </div>
        </div>
        <p className="line-clamp-2 text-sm text-slate-600">{company.short_description || "No description yet."}</p>
        <div className="flex flex-wrap gap-1.5">
          <Badge>{stageLabel(company.funding_stage)}</Badge>
          <Badge>{remoteLabel(company.remote_policy)}</Badge>
          {company.hiring_engineers ? <Badge className="border-emerald-200 bg-emerald-50 text-emerald-800">Hiring engineers</Badge> : null}
        </div>
        <dl className="grid grid-cols-2 gap-2 text-xs text-slate-600">
          <div>
            <dt className="text-slate-400">Country</dt>
            <dd>{company.headquarters_country || "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Founded</dt>
            <dd>{formatDate(company.founded_date)}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Employees</dt>
            <dd>{company.employee_range || "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Latest funding</dt>
            <dd>
              {formatMoney(company.latest_funding_usd || company.latest_funding_amount, company.latest_funding_currency || "USD")}
              {company.latest_funding_date ? ` · ${formatDate(company.latest_funding_date)}` : ""}
            </dd>
          </div>
          <div className="col-span-2">
            <dt className="text-slate-400">Investors</dt>
            <dd>{company.investors.slice(0, 3).join(", ") || "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Eng jobs</dt>
            <dd>{company.engineering_job_count}</dd>
          </div>
          <div>
            <dt className="text-slate-400">Discovered</dt>
            <dd>{daysAgo(company.first_discovered_at)}</dd>
          </div>
        </dl>
        <div className="mt-auto flex flex-wrap gap-2">
          {website ? (
            <Button asChild size="sm">
              <a href={website} target="_blank" rel="noreferrer">
                Website <ExternalLink className="h-3.5 w-3.5" />
              </a>
            </Button>
          ) : null}
          {careers ? (
            <Button asChild size="sm" variant="outline">
              <a href={careers} target="_blank" rel="noreferrer">
                Careers
              </a>
            </Button>
          ) : null}
          <Button asChild size="sm" variant="outline">
            <Link href={`/companies/${company.slug}`}>Jobs</Link>
          </Button>
          <Button asChild size="sm" variant="secondary">
            <Link href={`/companies/${company.slug}`}>Details</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function CompanyGrid({ companies }: { companies: CompanyCard[] }) {
  if (!companies.length) {
    return <div className="rounded-xl border bg-white p-10 text-center text-sm text-muted-foreground">No companies match these filters.</div>;
  }
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {companies.map((company) => (
        <CompanyCardView key={company.id} company={company} />
      ))}
    </div>
  );
}
