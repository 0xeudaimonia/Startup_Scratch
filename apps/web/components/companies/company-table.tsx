"use client";

import Link from "next/link";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import type { CompanyCard } from "@/lib/types";
import { formatDate, formatMoney, remoteLabel, stageLabel } from "@/lib/utils";

const helper = createColumnHelper<CompanyCard>();

const columns = [
  helper.accessor("name", {
    header: "Company",
    cell: (info) => (
      <Link className="font-medium text-emerald-800 hover:underline" href={`/companies/${info.row.original.slug}`}>
        {info.getValue()}
      </Link>
    ),
  }),
  helper.accessor("normalized_domain", { header: "Domain" }),
  helper.accessor("funding_stage", { header: "Stage", cell: (info) => stageLabel(info.getValue()) }),
  helper.accessor("latest_funding_usd", {
    header: "Funding",
    cell: (info) => formatMoney(info.getValue() || info.row.original.latest_funding_amount),
  }),
  helper.accessor("latest_funding_date", { header: "Funded", cell: (info) => formatDate(info.getValue()) }),
  helper.accessor("remote_policy", { header: "Remote", cell: (info) => remoteLabel(info.getValue()) }),
  helper.accessor("engineering_job_count", { header: "Eng jobs" }),
  helper.accessor("opportunity_score", { header: "Score" }),
];

export function CompanyTable({ companies }: { companies: CompanyCard[] }) {
  const table = useReactTable({ data: companies, columns, getCoreRowModel: getCoreRowModel() });
  return (
    <div className="overflow-x-auto rounded-xl border bg-white">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>
              {group.headers.map((header) => (
                <th key={header.id} className="px-4 py-3 font-medium">
                  {flexRender(header.column.columnDef.header, header.getContext())}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-t">
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-4 py-3">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
