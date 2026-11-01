/** Opt-in User Timing marks and console records for the actual layout switch. */
export function traceGds(layout: string, phase: string) {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return;
  if (typeof window === "undefined") return;
  if (!new URLSearchParams(location.search).has("gdsProfile")) return;
  performance.mark(`gds:${layout}:${phase}`);
  console.info(
    "[gds-profile]",
    JSON.stringify({ session: performance.timeOrigin, layout, phase, ms: performance.now() }),
  );
}
