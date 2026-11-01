import { createAnimationCapture, getRendererFrameStats } from "./animation-profile";

/** Explicit workload controls stay separate from frame observation and statistics. */
export function observeAnimationProfile(root: HTMLElement) {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return;
  const params = new URLSearchParams(location.search);
  const profiling = params.has("animationProfile");
  const fpsEnabled = params.has("fps");
  if (!profiling && !fpsEnabled) return;
  const capture = createAnimationCapture(root);
  const panel = document.createElement("div");
  panel.style.cssText = profiling
    ? "position:fixed;bottom:12px;left:12px;z-index:200;background:#101713;color:#b6d9c7;padding:8px;font:11px monospace;width:min(360px,calc(100vw - 24px));box-sizing:border-box"
    : "position:fixed;top:10px;right:10px;z-index:200;background:#101713eF;color:#b6d9c7;padding:7px 9px;font:11px/1.45 monospace;white-space:pre;pointer-events:none;border:1px solid #547661;border-radius:4px";
  const createHud = () => {
    const hud = profiling ? document.createElement("div") : panel;
    hud.style.cssText = "position:fixed;top:10px;right:10px;z-index:200;background:#101713eF;color:#b6d9c7;padding:7px 9px;font:11px/1.45 monospace;white-space:pre;pointer-events:none;border:1px solid #547661;border-radius:4px";
    hud.setAttribute("aria-label", "Renderer frame rate diagnostics");
    let hudFrame = 0;
    let lastRefresh = 0;
    const rafTimes: number[] = [];
    const refreshHud = (time: number) => {
      rafTimes.push(time);
      while (rafTimes.length && rafTimes[0] < time - 1000) rafTimes.shift();
      if (time - lastRefresh >= 250) {
        lastRefresh = time;
        const rafElapsed = rafTimes.length > 1 ? rafTimes.at(-1)! - rafTimes[0] : 0;
        const rafHz = rafElapsed > 0 ? (rafTimes.length - 1) * 1000 / rafElapsed : 0;
        const stats = getRendererFrameStats();
        hud.textContent = document.hidden
          ? "rAF  hidden   Three fps  hidden"
          : !stats || stats.renders === 0
            ? `rAF  ${rafHz.toFixed(0)} Hz   Three fps  idle\nrender p95  -- ms   CPU  -- ms\nlast calls  --   triangles  --`
            : `rAF  ${rafHz.toFixed(0)} Hz   Three fps  ${stats.fps.toFixed(0)}\nrender p95  ${stats.intervalP95Ms?.toFixed(1) ?? "--"} ms   CPU  ${stats.cpuMs.toFixed(1)} ms\nlast calls  ${stats.calls}   triangles  ${stats.triangles}`;
      }
      hudFrame = requestAnimationFrame(refreshHud);
    };
    document.body.append(hud);
    hudFrame = requestAnimationFrame(refreshHud);
    return { element: hud, dispose() { cancelAnimationFrame(hudFrame); hud.remove(); } };
  };
  const hud = fpsEnabled ? createHud() : undefined;
  if (!profiling) {
    return {
      record: capture.record,
      dispose() { hud?.dispose(); capture.dispose(); },
    };
  }
  const output = document.createElement("textarea");
  output.readOnly = true;
  output.setAttribute("aria-label", "Animation profile report");
  output.style.cssText = "display:block;width:100%;height:90px;box-sizing:border-box;font:10px monospace";
  let timeout = 0;
  let sweepFrame = 0;
  const buttons: HTMLButtonElement[] = [];
  type Scenario = { workload: string; startId: string | null; endId: string | null; startY?: number; endY?: number };
  const run = (scenario: Scenario) => {
    if (scenario.workload === "scripted-entry-sweep" && root.getAttribute("data-enhanced") !== "true") {
      output.value = "Replay entry before sweeping.";
      return;
    }
    if (scenario.workload === "scripted-article-scroll" && root.getAttribute("data-enhanced") !== "false") {
      output.value = "Restore the static article before scrolling it.";
      return;
    }
    if (scenario.workload === "scripted-postscript-sweep" && root.getAttribute("data-enhanced") !== "false") {
      output.value = "Restore the static article before sweeping the postscript.";
      return;
    }
    const startY = scenario.startY ?? root.getBoundingClientRect().top + scrollY;
    const endY = Math.min(document.documentElement.scrollHeight - innerHeight,
      scenario.endY ?? startY + root.offsetHeight - root.querySelector<HTMLElement>(".circuit-opening__stage")!.offsetHeight);
    if (scenario.workload !== "native-input-or-idle") window.scrollTo({ top: startY, behavior: "instant" });
    buttons.forEach((button) => { button.disabled = true; });
    output.value = "Capturing 6 seconds. Keep this tab visible.";
    capture.start();
    const startTime = performance.now();
    const advance = (time: number) => {
      const fraction = Math.min(1, (time - startTime) / 6000);
      window.scrollTo({ top: startY + fraction * (endY - startY), behavior: "instant" });
      sweepFrame = requestAnimationFrame(advance);
    };
    if (scenario.workload !== "native-input-or-idle") sweepFrame = requestAnimationFrame(advance);
    timeout = window.setTimeout(() => {
      cancelAnimationFrame(sweepFrame);
      output.value = JSON.stringify({ ...scenario, ...capture.finish() });
      buttons.forEach((button) => { button.disabled = false; });
    }, 6000);
  };
  const point = (id: string) => {
    const element = document.getElementById(id)!;
    return element.getBoundingClientRect().top + scrollY;
  };
  const footerBottom = () => {
    const footer = document.querySelector<HTMLElement>(".article-footer")!;
    return footer.getBoundingClientRect().bottom + scrollY;
  };
  const controls: [string, () => Scenario][] = [
    ["Capture 6s", () => ({ workload: "native-input-or-idle", startId: null, endId: null })],
    ["Sweep entry 6s", () => {
      const startY = root.getBoundingClientRect().top + scrollY;
      return { workload: "scripted-entry-sweep", startId: "entry-top", endId: "entry-progress-0.96", startY, endY: startY + 0.96 * (root.offsetHeight - root.querySelector<HTMLElement>(".circuit-opening__stage")!.offsetHeight) };
    }],
    ["Scroll article 6s", () => ({ workload: "scripted-article-scroll", startId: "extracting-the-circuit", endId: "article-footer-bottom", startY: point("extracting-the-circuit"), endY: footerBottom() })],
    ["Sweep postscript 6s", () => ({ workload: "scripted-postscript-sweep", startId: "ml-postscript", endId: "article-footer-bottom", startY: point("ml-postscript"), endY: footerBottom() })],
  ];
  for (const [label, scenario] of controls) {
    const button = document.createElement("button");
    button.textContent = label;
    button.style.cssText = "padding:4px;margin:2px;border:1px solid #547661";
    button.onclick = () => run(scenario());
    buttons.push(button);
    panel.append(button);
  }
  panel.append(output);
  document.body.append(panel);
  return {
    record: capture.record,
    dispose() { clearTimeout(timeout); cancelAnimationFrame(sweepFrame); hud?.dispose(); capture.dispose(); panel.remove(); },
  };
}
