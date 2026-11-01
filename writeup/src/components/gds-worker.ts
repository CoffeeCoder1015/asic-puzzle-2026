import {
  prepareGdsLayout,
  type GdsLayout,
  type PreparedGdsLayout,
} from "./gds-geometry";

export type GdsWorkerRequest = {
  id: "puzzle" | "warmup";
  url: string;
};

export type GdsWorkerResponse =
  | {
      id: GdsWorkerRequest["id"];
      status: "progress";
      phase: "received" | "parsed" | "geometry-start" | "geometry-end";
    }
  | { id: GdsWorkerRequest["id"]; status: "loaded"; data: PreparedGdsLayout }
  | { id: GdsWorkerRequest["id"]; status: "failed" };

function reply(message: GdsWorkerResponse, transfer: Transferable[] = []) {
  self.postMessage(message, { transfer });
}

self.onmessage = async ({ data: request }: MessageEvent<GdsWorkerRequest>) => {
  const { id, url } = request;
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("GDS geometry unavailable");
    const text = await response.text();
    if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG === "1") {
      reply({ id, status: "progress", phase: "received" });
    }
    const raw = JSON.parse(text) as GdsLayout;
    if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG === "1") {
      reply({ id, status: "progress", phase: "parsed" });
      reply({ id, status: "progress", phase: "geometry-start" });
    }
    const data = prepareGdsLayout(raw);
    if (process.env.NEXT_PUBLIC_WRITEUP_DEBUG === "1") {
      reply({ id, status: "progress", phase: "geometry-end" });
    }
    const transfer = data.geometries.flatMap((geometry) =>
      geometry ? [geometry.positions.buffer, geometry.normals.buffer] : [],
    );
    reply({ id, status: "loaded", data }, transfer);
  } catch {
    reply({ id, status: "failed" });
  }
};
