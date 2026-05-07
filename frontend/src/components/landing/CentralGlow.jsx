export default function CentralGlow() {
  return (
    <div className="absolute inset-0 z-[2] pointer-events-none overflow-hidden">
      <svg
        className="absolute left-1/2 top-[10%] -translate-x-1/2 animate-glow-pulse"
        width="900"
        height="320"
        viewBox="0 0 900 320"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <filter id="glow-blur">
            <feGaussianBlur stdDeviation="25" />
          </filter>
          <radialGradient id="glow-gradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#0e7a6b" stopOpacity="0.5" />
            <stop offset="50%" stopColor="#0c6b5e" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#070b0a" stopOpacity="0" />
          </radialGradient>
        </defs>
        <ellipse
          cx="450"
          cy="160"
          rx="400"
          ry="120"
          fill="url(#glow-gradient)"
          filter="url(#glow-blur)"
        />
      </svg>
    </div>
  );
}
