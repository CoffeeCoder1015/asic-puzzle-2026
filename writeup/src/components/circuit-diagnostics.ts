/** Opt-in debug trace. It observes the real canvas, never drives the animation. */
export function observeCircuit(root: HTMLElement) {
  if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG !== "1") return;
  if (!new URLSearchParams(location.search).has("sceneDebug")) return;

  const output = document.createElement("textarea");
  output.readOnly = true;
  output.setAttribute("aria-label", "Circuit scroll size trace");
  output.style.cssText = "position:fixed;bottom:12px;left:12px;width:300px;height:140px;z-index:100;background:#101713;color:#b6d9c7;font:11px monospace;padding:8px;border:1px solid #547661";
  document.body.append(output);
  const samples: object[] = [];
  let lastSize = "";
  let resizeCount = 0;
  const record = (progress: number) => {
    const stage = root.querySelector(".gds-viewer__stage")!;
    const canvas = stage.querySelector("canvas");
    const { clientWidth: width, clientHeight: height } = stage;
    const size = `${width}x${height}`;
    if (lastSize && size !== lastSize) resizeCount++;
    lastSize = size;
    samples.push({ y: scrollY, progress, width, height, bufferWidth: canvas?.width, bufferHeight: canvas?.height });
    if (samples.length > 600) samples.shift();
    output.value = JSON.stringify({ resizeCount, samples }, null, 2);
  };
  return { record, dispose: () => output.remove() };
}
