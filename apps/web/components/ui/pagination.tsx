"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function parsePage(value: string | null | undefined): number {
  const page = Number(value);
  if (!Number.isFinite(page) || page < 1) return 1;
  return Math.floor(page);
}

function visiblePages(current: number, totalPages: number): Array<number | "ellipsis"> {
  if (totalPages <= 7) {
    return Array.from({ length: totalPages }, (_, index) => index + 1);
  }
  const start = Math.max(2, current - 1);
  const end = Math.min(totalPages - 1, current + 1);
  const items: Array<number | "ellipsis"> = [1];
  if (start > 2) items.push("ellipsis");
  for (let page = start; page <= end; page += 1) items.push(page);
  if (end < totalPages - 1) items.push("ellipsis");
  items.push(totalPages);
  return items;
}

export function Pagination({
  page,
  pageSize,
  total,
  label = "Pagination",
}: {
  page: number;
  pageSize: number;
  total: number;
  label?: string;
}) {
  const pathname = usePathname();
  const params = useSearchParams();
  const totalPages = Math.max(1, Math.ceil(total / Math.max(pageSize, 1)));
  if (totalPages <= 1) return null;

  function hrefForPage(nextPage: number) {
    const next = new URLSearchParams(params.toString());
    if (nextPage <= 1) next.delete("page");
    else next.set("page", String(nextPage));
    const query = next.toString();
    return query ? `${pathname}?${query}` : pathname;
  }

  return (
    <nav className="flex flex-wrap items-center justify-between gap-3 pt-2" aria-label={label}>
      <div className="text-sm text-muted-foreground">
        Page {Math.min(page, totalPages)} of {totalPages}
      </div>
      <div className="flex flex-wrap items-center gap-1">
        <Button asChild variant="outline" size="sm" className={page <= 1 ? "pointer-events-none opacity-50" : ""}>
          <Link href={hrefForPage(Math.max(1, page - 1))} aria-disabled={page <= 1} tabIndex={page <= 1 ? -1 : undefined}>
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Link>
        </Button>
        {visiblePages(page, totalPages).map((item, index) =>
          item === "ellipsis" ? (
            <span key={`ellipsis-${index}`} className="px-1.5 text-sm text-muted-foreground">
              …
            </span>
          ) : (
            <Button
              key={item}
              asChild
              variant={item === page ? "default" : "outline"}
              size="sm"
              className={cn("min-w-8 px-2", item === page && "pointer-events-none")}
            >
              <Link href={hrefForPage(item)} aria-current={item === page ? "page" : undefined}>
                {item}
              </Link>
            </Button>
          )
        )}
        <Button
          asChild
          variant="outline"
          size="sm"
          className={page >= totalPages ? "pointer-events-none opacity-50" : ""}
        >
          <Link
            href={hrefForPage(Math.min(totalPages, page + 1))}
            aria-disabled={page >= totalPages}
            tabIndex={page >= totalPages ? -1 : undefined}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Link>
        </Button>
      </div>
    </nav>
  );
}
