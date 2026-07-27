/**
 * Soft drifting aurora blobs — inspired by 21st.dev LiquidAurora (CSS-only).
 */
export function AuroraField({ className = "" }: { className?: string }) {
  return (
    <div
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
      aria-hidden
    >
      <div className="aurora-blob aurora-blob-a" />
      <div className="aurora-blob aurora-blob-b" />
      <div className="aurora-blob aurora-blob-c" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(5,8,22,0.55)_70%,rgba(5,8,22,0.92)_100%)]" />
    </div>
  );
}
