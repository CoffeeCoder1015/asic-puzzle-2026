import { readFile } from "node:fs/promises";
import path from "node:path";

const median = (values) => {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
};
const rows = [];
for (const file of process.argv.slice(2)) {
  const report = JSON.parse(await readFile(file, "utf8"));
  const initial = report.initial ?? { viewport: report.viewport, dpr: report.dpr, ambient: report.ambient };
  const final = report.final ?? initial;
  const workload = report.workload ?? "unknown";
  const entry = workload.includes("entry") || workload.includes("scroll-0-to-0.96");
  const article = workload.includes("article") || workload.includes("postscript");
  const work = (kind) => report.work.filter((sample) => sample.kind === kind);
  const cpu = (kind) => work(kind).reduce((total, sample) => total + sample.ms, 0);
  const scene = work("scene");
  const progress = report.progress.map((sample) => sample.value);
  const intervals = report.frames.slice(1).map((sample, index) => sample.time - report.frames[index].time);
  const moved = Math.abs(report.frames.at(-1)?.y - report.frames[0]?.y);
  const invalid = [
    report.hidden && "hidden", report.errors && `${report.errors} errors`,
    intervals.length < 2 && "no frame observations", report.ready !== "true" && "viewer unavailable",
    JSON.stringify(initial.viewport) !== JSON.stringify(final.viewport) && "viewport changed",
    initial.dpr !== final.dpr && "DPR changed",
    initial.ambient !== final.ambient && "ambient changed",
    entry && (!scene.length || progress.length < 2) && "entry work absent",
    article && !(moved > 100) && "article did not scroll",
    article && report.enhanced !== "false" && "article was not released",
  ].filter(Boolean);
  rows.push({ file: path.basename(file), status: invalid.join(", ") || "observed", workload,
    viewport: initial.viewport, dpr: initial.dpr, ambient: initial.ambient,
    frames: intervals.length, p50: report.frameIntervals.p50, p95: report.frameIntervals.p95,
    over16_7: intervals.filter((value) => value > 16.7).length,
    over33_3: intervals.filter((value) => value > 33.3).length,
    longTasks: report.longTaskSupported ? report.longTasks.length : null,
    glyphCpuMs: cpu("glyph"), glyphUpdateCpuMs: cpu("glyph-update"), entryCpuMs: cpu("entry"), renderCpuMs: cpu("scene"),
    renders: scene.length, rendererFps: scene.length * 1000 / report.durationMs,
    drawCalls: [...new Set(scene.map((sample) => sample.count))], triangles: [...new Set(scene.map((sample) => sample.triangles))],
    progress: progress.length ? [Math.min(...progress), Math.max(...progress)] : [],
    scroll: [report.frames[0]?.y, report.frames.at(-1)?.y],
  });
}
const groups = new Map();
for (const row of rows) {
  const version = row.file.match(/(?:^|-)(before|after)-\d+\.json$/)?.[1];
  if (!version) continue;
  const key = `${row.workload}/${version}`;
  const group = groups.get(key) ?? [];
  group.push(row);
  groups.set(key, group);
}
const comparisons = [];
for (const [group, selected] of groups) {
  for (const metric of ["p50", "p95", "over33_3", "glyphCpuMs", "glyphUpdateCpuMs", "renderCpuMs", "frames", "rendererFps"]) {
    const values = selected.map((row) => row[metric]);
    comparisons.push({ group, metric, runs: values.length, invalid: selected.filter((row) => row.status !== "observed").length,
      median: median(values), range: [Math.min(...values), Math.max(...values)] });
  }
}
console.log(JSON.stringify({ captures: rows, comparisons }, null, 2));
