"use client";

import { Suspense } from "react";
import { CompanyBrowser } from "@/components/companies/company-browser";

export default function RemotePage() {
  return (
    <Suspense>
      <CompanyBrowser
        title="Remote Companies"
        description="Global remote and remote-first teams."
        preset={{ remote_policy: "GLOBAL_REMOTE,REMOTE_FIRST", sort: "opportunity_score" }}
      />
    </Suspense>
  );
}
