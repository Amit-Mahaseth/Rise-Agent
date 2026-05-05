import { ReactNode } from "react";
import { NavLink } from "react-router-dom";

const rail = [
  { to: "/", label: "Overview", icon: IconHome },
  { to: "/assets", label: "Leads", icon: IconStack },
  { to: "/collectibles", label: "Campaigns", icon: IconGrid },
  { to: "/activity", label: "Activity", icon: IconClock },
] as const;

type ConsoleFrameProps = {
  children: ReactNode;
};

export function ConsoleFrame({ children }: ConsoleFrameProps) {
  return (
    <div className="console">
      <aside className="console__rail" aria-label="Workspace">
        <div className="console__rail-top">
          {rail.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) => `console__rail-link${isActive ? " console__rail-link--active" : ""}`}
              title={label}
            >
              <Icon />
            </NavLink>
          ))}
        </div>
        <button type="button" className="console__rail-link console__rail-link--bottom" title="Workspace settings">
          <IconGear />
        </button>
      </aside>
      <div className="console__surface">{children}</div>
    </div>
  );
}

function IconHome() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <path d="M4 11.5 12 4l8 7.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6 10v9.5h12V10" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconStack() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <path d="M12 4 4 9l8 5 8-5-8-5Z" strokeLinecap="round" strokeLinejoin="round" />
      <path d="m4 15 8 5 8-5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconGrid() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <rect x="4" y="4" width="7" height="7" rx="2" />
      <rect x="13" y="4" width="7" height="7" rx="2" />
      <rect x="4" y="13" width="7" height="7" rx="2" />
      <rect x="13" y="13" width="7" height="7" rx="2" />
    </svg>
  );
}

function IconClock() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 8v5l3 2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconGear() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7">
      <path
        d="M12 15.25a3.25 3.25 0 1 0 0-6.5 3.25 3.25 0 0 0 0 6.5Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M19 12h-1m-12 0H5m14.07-5.93-.71.71m-11.71 11.71-.71.71M19 17.07l-.71-.71M5.64 6.64l-.71-.71M12 5v1m0 12v1m7.07-7.07-.71-.71M6.64 17.36l-.71-.71"
        strokeLinecap="round"
      />
    </svg>
  );
}
