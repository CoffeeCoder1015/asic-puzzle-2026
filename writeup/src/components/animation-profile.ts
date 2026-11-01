import type { WebGLRenderer } from "three";

type WorkSample = { time: number; kind: "glyph" | "glyph-update" | "entry" | "scene" | "framing"; ms: number; count: number; triangles?: number };
type FrameSample = { time: number; y: number };
type LongTaskSample = { time: number; duration: number };
type RendererFrameSample = { time: number; cpuMs: number; calls: number; triangles: number };
export type RendererFrameStats = Readonly<{
  renders: number;
  fps: number;
  intervalP95Ms: number | null;
  cpuMs: number;
  calls: number;
  triangles: number;
}>;
let workSamples: WorkSample[] | undefined;
let rendererFrames: RendererFrameSample[] | undefined;
let rendererTrackingStarted = 0;

export function getRendererFrameStats(): RendererFrameStats | undefined {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return undefined;
  if (!rendererFrames) return undefined;
  const now = performance.now();
  const cutoff = now - 1000;
  rendererFrames = rendererFrames.filter((sample) => sample.time >= cutoff);
  const samples = rendererFrames;
  const intervals = samples.slice(1).map((sample, index) => sample.time - samples[index].time).sort((a, b) => a - b);
  const p95 = intervals.length ? intervals[Math.floor((intervals.length - 1) * 0.95)] : null;
  const latest = samples.at(-1);
  const windowMs = Math.min(1000, now - rendererTrackingStarted);
  return Object.freeze({
    renders: samples.length,
    fps: windowMs > 0 ? samples.length * 1000 / windowMs : 0,
    intervalP95Ms: p95,
    cpuMs: latest?.cpuMs ?? 0,
    calls: latest?.calls ?? 0,
    triangles: latest?.triangles ?? 0,
  });
}

export function beginAnimationWork() {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return undefined;
  return workSamples ? performance.now() : undefined;
}

export function endAnimationWork(kind: WorkSample["kind"], start: number | undefined, count: number, triangles?: number) {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return;
  if (start === undefined || !workSamples) return;
  workSamples.push({ time: start, kind, ms: performance.now() - start, count, triangles });
}

export function observeSceneWork(renderer: WebGLRenderer) {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return;
  const params = new URLSearchParams(location.search);
  const profiling = params.has("animationProfile");
  const fpsEnabled = params.has("fps");
  if (!profiling && !fpsEnabled) return;
  if (profiling) {
    const context = renderer.getContext();
    const debugInfo = context.getExtension("WEBGL_debug_renderer_info");
    console.info("[animation-gpu]", JSON.stringify({ multiDraw: renderer.extensions.has("WEBGL_multi_draw"),
      renderer: debugInfo ? context.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : "unavailable" }));
  }
  rendererFrames = fpsEnabled ? [] : undefined;
  rendererTrackingStarted = performance.now();
  const render = renderer.render;
  const wrapped = function (this: WebGLRenderer, ...args: Parameters<WebGLRenderer["render"]>) {
    const start = beginAnimationWork();
    const frameStart = rendererFrames ? performance.now() : 0;
    try {
      render.apply(this, args);
    } finally {
      endAnimationWork("scene", start, this.info.render.calls, this.info.render.triangles);
    }
    if (rendererFrames) {
      const time = performance.now();
      rendererFrames.push({ time, cpuMs: time - frameStart, calls: this.info.render.calls, triangles: this.info.render.triangles });
    }
  };
  renderer.render = wrapped;
  return () => {
    if (renderer.render === wrapped) renderer.render = render;
    rendererFrames = undefined;
  };
}

export function createAnimationCapture(root: HTMLElement) {
  let frame = 0;
  let frames: FrameSample[] = [];
  let progress: { time: number; value: number; y: number }[] = [];
  let started = 0;
  let hidden = false;
  let errors = 0;
  let longTasks: LongTaskSample[] = [];
  let observer: PerformanceObserver | undefined;
  let longTaskSupported: boolean | null = null;
  let session = "";
  let initialScrollY = 0;
  const state = () => ({
    entryEnhanced: root.getAttribute("data-enhanced"),
    ready: root.querySelector(".gds-viewer")?.getAttribute("data-ready"),
    ambient: document.querySelector(".ambient-field")?.getAttribute("data-running") ?? null,
    viewport: [innerWidth, innerHeight], dpr: devicePixelRatio, hidden: document.hidden,
  });
  let initialState: ReturnType<typeof state>;
  const onError = () => { errors++; };
  const onVisibility = () => { if (document.hidden) hidden = true; };
  const sample = (time: number) => {
    frames.push({ time, y: scrollY });
    frame = requestAnimationFrame(sample);
  };
  const drainLongTasks = () => {
    if (!observer) return;
    for (const entry of observer.takeRecords()) {
      if (entry.startTime >= started) longTasks.push({ time: entry.startTime, duration: entry.duration });
    }
  };
  const stop = () => {
    cancelAnimationFrame(frame);
    window.removeEventListener("error", onError);
    window.removeEventListener("unhandledrejection", onError);
    document.removeEventListener("visibilitychange", onVisibility);
    drainLongTasks();
    observer?.disconnect();
    observer = undefined;
  };
  return {
    start() {
      stop();
      frames = [];
      progress = [];
      longTasks = [];
      workSamples = [];
      hidden = document.hidden;
      errors = 0;
      initialScrollY = scrollY;
      initialState = state();
      started = performance.now();
      session = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      longTaskSupported = typeof PerformanceObserver !== "undefined" && PerformanceObserver.supportedEntryTypes?.includes("longtask") === true;
      if (longTaskSupported) {
        observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (entry.startTime >= started) longTasks.push({ time: entry.startTime, duration: entry.duration });
          }
        });
        observer.observe({ type: "longtask", buffered: false });
      }
      window.addEventListener("error", onError);
      window.addEventListener("unhandledrejection", onError);
      document.addEventListener("visibilitychange", onVisibility);
      frame = requestAnimationFrame(sample);
    },
    record(value: number) {
      if (workSamples) progress.push({ time: performance.now(), value, y: scrollY });
    },
    finish() {
      stop();
      const work = workSamples ?? [];
      workSamples = undefined;
      const intervals = frames.slice(1).map((sample, index) => sample.time - frames[index].time).sort((a, b) => a - b);
      const percentile = (fraction: number) => intervals[Math.floor((intervals.length - 1) * fraction)];
      const costs = (kind: WorkSample["kind"]) => {
        const selected = work.filter((sample) => sample.kind === kind);
        return { invocations: selected.length, cpuMs: selected.reduce((sum, sample) => sum + sample.ms, 0), maxCpuMs: Math.max(0, ...selected.map((sample) => sample.ms)), count: selected.reduce((sum, sample) => sum + sample.count, 0), triangles: selected.reduce((sum, sample) => sum + (sample.triangles ?? 0), 0) };
      };
      const frameThresholds = { over16_7ms: intervals.filter((value) => value > 16.7).length, over33_3ms: intervals.filter((value) => value > 33.3).length, over50ms: intervals.filter((value) => value > 50).length };
      return {
        session,
        durationMs: performance.now() - started,
        initial: { scrollY: initialScrollY, ...initialState }, final: { scrollY, ...state() }, hidden, errors,
        ready: root.querySelector(".gds-viewer")?.getAttribute("data-ready"),
        enhanced: root.getAttribute("data-enhanced"),
        frameIntervals: { count: intervals.length, p50: percentile(0.5), p95: percentile(0.95), max: intervals.at(-1), ...frameThresholds },
        longTaskSupported, longTasks, glyph: costs("glyph"), glyphUpdate: costs("glyph-update"), entry: costs("entry"), scene: costs("scene"), framing: costs("framing"), frames, progress, work,
      };
    },
    dispose() { stop(); workSamples = undefined; },
  };
}

export type AnimationCapture = ReturnType<typeof createAnimationCapture>;
