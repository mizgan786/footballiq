import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import ChatWidget from "./ChatWidget";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/search", label: "Players" },
  { to: "/predict", label: "Predictor" },
  { to: "/compare", label: "Compare" },
  { to: "/analytics", label: "Analytics" },
  { to: "/assistant", label: "Assistant" },
];

function NavItem({ to, label, end, onClick }) {
  return (
    <NavLink
      to={to}
      end={end}
      onClick={onClick}
      className={({ isActive }) =>
        `whitespace-nowrap px-3 py-2 rounded text-sm transition-colors ${
          isActive
            ? "bg-[var(--color-panel-raised)] text-[var(--color-amber)]"
            : "text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-panel-raised)]"
        }`
      }
    >
      {label}
    </NavLink>
  );
}

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="h-16 shrink-0 border-b border-[var(--color-border)] bg-[var(--color-panel)] sticky top-0 z-20">
        <div className="h-full px-4 md:px-6 flex items-center justify-between">
          <NavLink to="/" className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[var(--color-amber)]" />
            <span className="font-display text-lg tracking-wide">FootballIQ</span>
          </NavLink>

          {/* desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <NavItem key={item.to} {...item} />
            ))}
          </nav>

          {/* mobile toggle */}
          <button
            onClick={() => setMobileOpen((v) => !v)}
            className="md:hidden p-2 rounded hover:bg-[var(--color-panel-raised)]"
            aria-label="Toggle menu"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
              {mobileOpen ? (
                <path d="M5 5l10 10M15 5L5 15" strokeLinecap="round" />
              ) : (
                <path d="M2 5h16M2 10h16M2 15h16" strokeLinecap="round" />
              )}
            </svg>
          </button>
        </div>

        {/* mobile menu */}
        {mobileOpen && (
          <nav className="md:hidden flex flex-col gap-1 px-4 pb-3 border-t border-[var(--color-border)] pt-2">
            {NAV_ITEMS.map((item) => (
              <NavItem key={item.to} {...item} onClick={() => setMobileOpen(false)} />
            ))}
          </nav>
        )}
      </header>

      <main className="flex-1 min-w-0">
        <Outlet />
      </main>

      <ChatWidget />
    </div>
  );
}
