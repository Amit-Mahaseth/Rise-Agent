export default function GridOverlay() {
  return (
    <div className="absolute inset-0 z-[2] pointer-events-none hidden lg:block">
      {/* 25% vertical line */}
      <div
        className="absolute top-0 bottom-0 w-px"
        style={{ left: '25%', backgroundColor: 'rgba(255,255,255,0.07)' }}
      />
      {/* 50% vertical line */}
      <div
        className="absolute top-0 bottom-0 w-px"
        style={{ left: '50%', backgroundColor: 'rgba(255,255,255,0.07)' }}
      />
      {/* 75% vertical line */}
      <div
        className="absolute top-0 bottom-0 w-px"
        style={{ left: '75%', backgroundColor: 'rgba(255,255,255,0.07)' }}
      />
    </div>
  );
}
