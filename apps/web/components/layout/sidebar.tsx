"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Briefcase,
  Building2,
  Compass,
  Globe2,
  LayoutDashboard,
  Radar,
  Sparkles,
  Wallet,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/funding", label: "Funding", icon: Wallet },
  { href: "/remote", label: "Remote Companies", icon: Globe2 },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/new-today", label: "New Today", icon: Sparkles },
  { href: "/sources", label: "Sources", icon: Compass },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="flex w-64 shrink-0 flex-col bg-slate-950 text-slate-100">
      <div className="flex items-center gap-2 px-5 py-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500 text-white">
          <Radar className="h-5 w-5" />
        </div>
        <div>
          <div className="text-sm font-semibold tracking-tight">Startup Radar</div>
          <div className="text-xs text-slate-400">Remote engineering intel</div>
        </div>
      </div>
      <nav className="flex flex-1 flex-col gap-1 px-3">
        {NAV.map((item) => {
          const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                active ? "bg-emerald-500/15 text-white" : "text-slate-300 hover:bg-white/5 hover:text-white"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="px-5 py-4 text-xs text-slate-500">Daily discovery for software engineers</div>
    </aside>
  );
}
