"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navItems = [
  { href: "/marketplace", label: "Products" },
  { href: "/dashboard", label: "For Companies" },
  { href: "/diagnostic", label: "Diagnose" },
];

const mobileItems = [
  { href: "/marketplace", icon: "🏠", label: "Home" },
  { href: "/marketplace", icon: "🔍", label: "Products" },
  { href: "/diagnostic", icon: "🧠", label: "Diagnose" },
  { href: "/dashboard", icon: "📊", label: "Dashboard" },
  { href: "/dashboard", icon: "👤", label: "Account" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="app-shell">
      <main className="app-main">
        <nav className="mock-nav" aria-label="Primary navigation">
          <Link className="mock-nav-logo" href="/marketplace">
            <span className="mock-logo-mark">⚡</span>
            FixPilot
          </Link>
          <div className="mock-nav-links">
            {navItems.map((item) => (
              <Link
                className={`mock-nav-link ${pathname.startsWith(item.href) ? "active" : ""}`}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            ))}
          </div>
          <Link className="mock-nav-cta" href="/dashboard">
            Start for free
          </Link>
        </nav>
        {children}
      </main>
      <nav className="mock-mobile-nav" aria-label="Mobile navigation">
        {mobileItems.map((item) => (
          <Link
            className={`mock-mobile-nav-item ${pathname.startsWith(item.href) ? "active" : ""}`}
            href={item.href}
            key={`${item.href}-${item.label}`}
          >
            <span className="mock-mobile-nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}
