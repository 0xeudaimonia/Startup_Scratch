"use client";

import { Suspense } from "react";
import { CompanyBrowser } from "@/components/companies/company-browser";

export default function CompaniesPage() {
  return (
    <Suspense fallback={<div>Loading…</div>}>
      <CompanyBrowser title="Companies" description="Search, filter, and inspect newly discovered startups." />
    </Suspense>
  );
}
