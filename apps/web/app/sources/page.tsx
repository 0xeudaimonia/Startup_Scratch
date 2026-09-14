"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchScrapeRuns, fetchSources, runScraper } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate } from "@/lib/utils";
import { useState } from "react";

export default function SourcesPage() {
  const queryClient = useQueryClient();
  const [selected, setSelected] = useState("fixture");
  const sources = useQuery({ queryKey: ["sources"], queryFn: fetchSources });
  const runs = useQuery({ queryKey: ["scrape-runs"], queryFn: fetchScrapeRuns });
  const scrape = useMutation({
    mutationFn: runScraper,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["sources"] });
      await queryClient.invalidateQueries({ queryKey: ["scrape-runs"] });
      await queryClient.invalidateQueries({ queryKey: ["companies"] });
      await queryClient.invalidateQueries({ queryKey: ["stats"] });
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Sources</h1>
        <p className="text-sm text-muted-foreground">
          Adapter health, scrape history, and a manual run button. Disabled sources require an official API or permission.
        </p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Run a scraper</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-center gap-3">
          <select
            className="h-9 rounded-md border px-3 text-sm"
            value={selected}
            onChange={(event) => setSelected(event.target.value)}
          >
            {(sources.data || []).map((source) => (
              <option key={source.name} value={source.name} disabled={!source.enabled}>
                {source.name} {source.enabled ? "" : "(disabled)"}
              </option>
            ))}
          </select>
          <Button onClick={() => scrape.mutate(selected)} disabled={scrape.isPending}>
            {scrape.isPending ? "Running…" : "Run scraper"}
          </Button>
          {scrape.isSuccess ? (
            <span className="text-sm text-emerald-700">
              {scrape.data.status}: created {scrape.data.records_created}, updated {scrape.data.records_updated}
            </span>
          ) : null}
          {scrape.isError ? <span className="text-sm text-red-600">{String(scrape.error)}</span> : null}
        </CardContent>
      </Card>
      <div className="grid gap-4 lg:grid-cols-2">
        {(sources.data || []).map((source) => (
          <Card key={source.name}>
            <CardHeader className="flex flex-row items-start justify-between">
              <div>
                <CardTitle className="capitalize">{source.name.replaceAll("_", " ")}</CardTitle>
                <div className="text-xs uppercase text-muted-foreground">{source.category}</div>
              </div>
              <Badge className={source.enabled ? "border-emerald-200 bg-emerald-50" : ""}>
                {source.enabled ? "Enabled" : "Disabled"}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-slate-600">
              <p>{source.description}</p>
              {source.requires ? <p>Requires: {source.requires}</p> : null}
              {source.last_run ? (
                <p>
                  Last run {formatDate(source.last_run.started_at)} · {source.last_run.status} ·{" "}
                  {source.last_run.records_created} created
                </p>
              ) : (
                <p>No runs yet.</p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Scrape runs</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase text-slate-500">
              <tr>
                <th className="py-2">Source</th>
                <th>Status</th>
                <th>Found</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Errors</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {(runs.data || []).map((run) => (
                <tr key={run.id} className="border-t">
                  <td className="py-2">{run.source}</td>
                  <td>{run.status}</td>
                  <td>{run.records_found}</td>
                  <td>{run.records_created}</td>
                  <td>{run.records_updated}</td>
                  <td>{run.errors?.length || 0}</td>
                  <td>{run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  );
}
