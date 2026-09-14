"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { fetchCompanies, fetchStats, isoDaysAgo, dateDaysAgo } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CompanyGrid } from "@/components/companies/company-card";

function Stat({ label, value, href }: { label: string; value: number | string; href: string }) {
  return (
    <Link href={href}>
      <Card className="transition hover:border-emerald-200 hover:shadow-md">
        <CardHeader>
          <CardTitle className="text-xs uppercase tracking-wide text-muted-foreground">{label}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-semibold">{value}</div>
        </CardContent>
      </Card>
    </Link>
  );
}

function Section({
  title,
  href,
  children,
}: {
  title: string;
  href: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">{title}</h2>
        <Link href={href} className="text-sm text-emerald-700 hover:underline">
          View all
        </Link>
      </div>
      {children}
    </section>
  );
}

export default function DashboardPage() {
  const stats = useQuery({ queryKey: ["stats"], queryFn: fetchStats });
  const today = useQuery({
    queryKey: ["dash", "today"],
    queryFn: () => fetchCompanies({ discovered_after: isoDaysAgo(0), page_size: 6, sort: "newest_discovered" }),
  });
  const funded = useQuery({
    queryKey: ["dash", "funded"],
    queryFn: () => fetchCompanies({ funded_after: dateDaysAgo(30), page_size: 6, sort: "latest_funding" }),
  });
  const founded = useQuery({
    queryKey: ["dash", "founded"],
    queryFn: () => fetchCompanies({ founded_after: dateDaysAgo(365), page_size: 6, sort: "founded_date" }),
  });
  const remote = useQuery({
    queryKey: ["dash", "remote"],
    queryFn: () => fetchCompanies({ remote_policy: "GLOBAL_REMOTE", page_size: 6, sort: "opportunity_score" }),
  });
  const hiring = useQuery({
    queryKey: ["dash", "hiring"],
    queryFn: () => fetchCompanies({ hiring_engineers: true, page_size: 6, sort: "engineering_job_count" }),
  });
  const top = useQuery({
    queryKey: ["dash", "top"],
    queryFn: () => fetchCompanies({ sort: "opportunity_score", page_size: 6 }),
  });

  const s = stats.data;
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          Newly funded and remote-friendly startups, refreshed automatically.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Discovered today" value={s?.companies_discovered_today ?? "—"} href="/new-today" />
        <Stat label="Discovered this week" value={s?.companies_discovered_this_week ?? "—"} href="/companies?discovered=7" />
        <Stat label="Funded this week" value={s?.companies_funded_this_week ?? "—"} href="/funding" />
        <Stat label="Recently founded" value={s?.recently_founded ?? "—"} href="/companies?founded=1y" />
        <Stat label="Global remote" value={s?.global_remote ?? "—"} href="/remote" />
        <Stat label="Hiring engineers" value={s?.hiring_engineers ?? "—"} href="/companies?hiring_engineers=true" />
        <Stat label="Engineering jobs" value={s?.engineering_jobs ?? "—"} href="/jobs" />
        <Stat label="Avg opportunity" value={s?.average_opportunity_score ?? "—"} href="/companies?sort=opportunity_score" />
      </div>
      <Section title="New today" href="/new-today">
        <CompanyGrid companies={today.data?.items || []} />
      </Section>
      <Section title="Newly funded" href="/funding">
        <CompanyGrid companies={funded.data?.items || []} />
      </Section>
      <Section title="Recently founded" href="/companies?founded=1y">
        <CompanyGrid companies={founded.data?.items || []} />
      </Section>
      <Section title="Global remote" href="/remote">
        <CompanyGrid companies={remote.data?.items || []} />
      </Section>
      <Section title="Hiring engineers" href="/companies?hiring_engineers=true">
        <CompanyGrid companies={hiring.data?.items || []} />
      </Section>
      <Section title="Top opportunities" href="/companies?sort=opportunity_score">
        <CompanyGrid companies={top.data?.items || []} />
      </Section>
    </div>
  );
}
