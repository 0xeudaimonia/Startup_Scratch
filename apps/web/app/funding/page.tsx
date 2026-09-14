"use client";

import { Suspense } from "react";
import { CompanyBrowser } from "@/components/companies/company-browser";

export default function FundingPage() {
  return (
    <Suspense>
      <CompanyBrowser
        title="Funding"
        description="Startups with recently announced funding rounds."
        preset={{ funded_after: new Date(Date.now() - 90 * 86400000).toISOString().slice(0, 10), sort: "latest_funding" }}
      />
    </Suspense>
  );
}
