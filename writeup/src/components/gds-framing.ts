import { PerspectiveCamera, Vector3 } from "three";
import type { GdsMetadata } from "./gds-geometry";

export type GdsEnvelope = {
  halfWidth: number;
  halfDepth: number;
  layers: { bottom: number; top: number; lift: number }[];
};

/** World bounds after the renderer's normalization and −π/2 X rotation. */
export function createGdsEnvelope(data: GdsMetadata): GdsEnvelope {
  const [minX, minY, maxX, maxY] = data.source.bbox;
  const scale = 6 / Math.max(maxX - minX, maxY - minY);
  const zScale = scale / data.source.dbuMicrons;
  return {
    halfWidth: ((maxX - minX) * scale) / 2,
    halfDepth: ((maxY - minY) * scale) / 2,
    layers: data.layers.map((layer, index) => ({
      bottom: layer.zMin * zScale,
      top: layer.zMax * zScale,
      lift: index * 0.16,
    })),
  };
}

/** Fit an outside, posed camera with a 12% NDC margin before manual zoom takes over. */
export function fitGdsView(
  camera: PerspectiveCamera,
  envelope: GdsEnvelope,
  spacing: number,
): number {
  const bottom = Math.min(
    ...envelope.layers.map((layer) => layer.bottom + layer.lift * spacing),
  );
  const top = Math.max(
    ...envelope.layers.map((layer) => layer.top + layer.lift * spacing),
  );
  camera.zoom = 1;
  camera.updateProjectionMatrix();
  camera.updateMatrixWorld();

  const corner = new Vector3();
  let extent = 0;
  for (const x of [-envelope.halfWidth, envelope.halfWidth]) {
    for (const y of [bottom, top]) {
      for (const z of [-envelope.halfDepth, envelope.halfDepth]) {
        corner.set(x, y, z).project(camera);
        extent = Math.max(extent, Math.abs(corner.x), Math.abs(corner.y));
      }
    }
  }

  camera.zoom = Math.min(1, 0.88 / extent);
  camera.updateProjectionMatrix();
  return camera.zoom;
}

/** One zoom fits the entire sampled story, without changing the live camera. */
export function fitGdsStory(
  envelope: GdsEnvelope,
  fov: number,
  aspect: number,
  poseAt: (progress: number) => {
    camera: number[];
    target: number[];
    spacing: number;
  },
): number {
  const camera = new PerspectiveCamera(fov, aspect, 0.1, 100);
  let zoom = 1;
  for (let step = 0; step <= 1000; step++) {
    const pose = poseAt(step / 1000);
    camera.position.set(pose.camera[0], pose.camera[1], pose.camera[2]);
    camera.lookAt(pose.target[0], pose.target[1], pose.target[2]);
    zoom = Math.min(zoom, fitGdsView(camera, envelope, pose.spacing));
  }
  return zoom;
}
