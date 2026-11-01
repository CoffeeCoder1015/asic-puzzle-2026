import { readFile } from "node:fs/promises";

for (const path of process.argv.slice(2)) {
  const logs = JSON.parse(await readFile(path, "utf8"));
  const events = logs.filter((row) => row.message?.startsWith("[gds-profile] "))
    .map((row) => JSON.parse(row.message.slice("[gds-profile] ".length)));
  const session = Math.max(...events.map((event) => event.session ?? 0));
  if (!session) throw new Error(`${path}: capture again with the current gdsProfile probe`);
  const current = events.filter((event) => event.session === session);
  const samples = new Map();
  let incomplete = 0;
  for (let index = 0; index < current.length; index++) {
    const start = current[index];
    if (start.phase !== "selected") continue;
    const rest = current.slice(index + 1);
    const boundary = rest.findIndex((event) => event.phase === "selected");
    const segment = boundary < 0 ? rest : rest.slice(0, boundary);
    const ready = segment.find((event) => event.phase === "scene-ready" && event.layout === start.layout);
    if (!ready) { incomplete++; continue; }
    const values = samples.get(start.layout) ?? [];
    values.push(ready.ms - start.ms);
    samples.set(start.layout, values);
  }
  const summary = Object.fromEntries([...samples].map(([layout, values]) => {
    values.sort((a, b) => a - b);
    const middle = Math.floor(values.length / 2);
    const median = values.length % 2 ? values[middle] : (values[middle - 1] + values[middle]) / 2;
    return [layout, { count: values.length, medianMs: median, rangeMs: [values[0], values.at(-1)] }];
  }));
  const firstSelection = current.find((event) => event.phase === "selected")?.ms ?? Infinity;
  console.log(JSON.stringify({ path, session, incomplete, failures: current.filter((event) => event.phase === "failed").length,
    fetchesDuringSwitches: current.filter((event) => event.phase === "fetch-start" && event.ms >= firstSelection).length,
    geometryBuildsDuringSwitches: current.filter((event) => event.phase === "geometry-start" && event.ms >= firstSelection).length,
    summary }, null, 2));
}
