"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { setCompanyChecked, setJobChecked } from "@/lib/api";
import { cn } from "@/lib/utils";

export function CheckToggle({
  checked,
  pending,
  onToggle,
  label = "Checked",
}: {
  checked: boolean;
  pending?: boolean;
  onToggle: (next: boolean) => void;
  label?: string;
}) {
  return (
    <label
      className={cn(
        "inline-flex cursor-pointer select-none items-center gap-1.5 text-xs font-medium",
        checked ? "text-emerald-700" : "text-slate-500",
        pending && "opacity-60"
      )}
      onClick={(event) => event.stopPropagation()}
    >
      <input
        type="checkbox"
        aria-label={label || "Checked"}
        className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
        checked={checked}
        disabled={pending}
        onChange={(event) => onToggle(event.target.checked)}
      />
      {label ? label : null}
    </label>
  );
}

function invalidateReviewQueries(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ["companies"] });
  queryClient.invalidateQueries({ queryKey: ["company"] });
  queryClient.invalidateQueries({ queryKey: ["jobs"] });
  queryClient.invalidateQueries({ queryKey: ["dash"] });
}

export function CompanyCheckToggle({
  companyId,
  checked,
  label = "Checked",
}: {
  companyId: string;
  checked: boolean;
  label?: string;
}) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (is_checked: boolean) => setCompanyChecked(companyId, is_checked),
    onSuccess: () => invalidateReviewQueries(queryClient),
  });
  return (
    <CheckToggle
      checked={checked}
      pending={mutation.isPending}
      onToggle={(next) => mutation.mutate(next)}
      label={label}
    />
  );
}

export function JobCheckToggle({
  jobId,
  checked,
  label = "Checked",
}: {
  jobId: string;
  checked: boolean;
  label?: string;
}) {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (is_checked: boolean) => setJobChecked(jobId, is_checked),
    onSuccess: () => invalidateReviewQueries(queryClient),
  });
  return (
    <CheckToggle
      checked={checked}
      pending={mutation.isPending}
      onToggle={(next) => mutation.mutate(next)}
      label={label}
    />
  );
}
