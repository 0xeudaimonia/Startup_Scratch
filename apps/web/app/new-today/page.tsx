"use client";

import { Suspense } from "react";
import { CompanyBrowser } from "@/components/companies/company-browser";

export default function NewTodayPage() {
  return (
    <Suspense>
      <CompanyBrowser
        title="New Today"
        description="Companies first discovered in the last 24 hours."
        preset={{ discovered: "0", sort: "newest_discovered" }}
      />
    </Suspense>
  );
}
