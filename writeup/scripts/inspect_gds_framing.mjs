import { readFile } from "node:fs/promises";
import {
  PerspectiveCamera,
  Vector3,
} from "../node_modules/three/build/three.module.js";
import { circuitPose } from "../src/components/circuit-choreography.ts";
import {
  createGdsEnvelope,
  fitGdsStory,
} from "../src/components/gds-framing.ts";

const data = JSON.parse(
  await readFile(
    new URL("../public/data/warmup-layout.json", import.meta.url),
    "utf8",
  ),
);
const envelope = createGdsEnvelope(data);
const sizes =
  process.argv.length > 2
    ? process.argv.slice(2).map((size) => size.split("x").map(Number))
    : [
        [1040, 510],
        [1040, 650],
        [335, 500],
        [335, 240],
        [1600, 500],
      ];

if (
  sizes.some(
    (size) =>
      size.length !== 2 ||
      size.some((value) => !Number.isFinite(value) || value <= 0),
  )
) {
  throw new Error("Use positive canvas sizes such as 1040x510 and 335x500.");
}

const maskBounds = [Infinity, Infinity, -Infinity, -Infinity];
const cells = new Map(data.cells.map((cell) => [cell.name, cell]));
for (const placement of data.placements) {
  const angle = (placement.rotation * Math.PI) / 180;
  const cosine = Math.cos(angle);
  const sine = Math.sin(angle);
  for (const layer of cells.get(placement.cell).layers) {
    for (const polygon of layer.polygons) {
      for (const [x, originalY] of polygon.hull) {
        const y = placement.mirror ? -originalY : originalY;
        const worldX = x * cosine - y * sine + placement.x;
        const worldY = x * sine + y * cosine + placement.y;
        maskBounds[0] = Math.min(maskBounds[0], worldX);
        maskBounds[1] = Math.min(maskBounds[1], worldY);
        maskBounds[2] = Math.max(maskBounds[2], worldX);
        maskBounds[3] = Math.max(maskBounds[3], worldY);
      }
    }
  }
}

const views = [];
for (const [width, height] of sizes) {
  const camera = new PerspectiveCamera(31, width / height, 0.1, 100);
  const storyZoom = fitGdsStory(envelope, camera.fov, camera.aspect, circuitPose);
  camera.zoom = storyZoom;
  camera.updateProjectionMatrix();
  let maximumNdcExtent = 0;
  let minimumNdcDepth = 1;
  let maximumNdcDepth = -1;
  for (let step = 0; step <= 1000; step++) {
    const pose = circuitPose(step / 1000);
    camera.position.set(...pose.camera);
    camera.lookAt(...pose.target);
    camera.updateMatrixWorld();
    const bottom = Math.min(
      ...envelope.layers.map(
        (layer) => layer.bottom + layer.lift * pose.spacing,
      ),
    );
    const top = Math.max(
      ...envelope.layers.map((layer) => layer.top + layer.lift * pose.spacing),
    );
    for (const x of [-envelope.halfWidth, envelope.halfWidth]) {
      for (const y of [bottom, top]) {
        for (const z of [-envelope.halfDepth, envelope.halfDepth]) {
          const point = new Vector3(x, y, z).project(camera);
          maximumNdcExtent = Math.max(
            maximumNdcExtent,
            Math.abs(point.x),
            Math.abs(point.y),
          );
          minimumNdcDepth = Math.min(minimumNdcDepth, point.z);
          maximumNdcDepth = Math.max(maximumNdcDepth, point.z);
        }
      }
    }
  }
  views.push({
    width,
    height,
    poses: 1001,
    storyZoom,
    maximumNdcExtent,
    minimumNdcDepth,
    maximumNdcDepth,
  });
}

console.log(
  JSON.stringify(
    {
      sourceBBox: data.source.bbox,
      physicalMaskBounds: maskBounds,
      openingTurnDegrees:
        ((circuitPose(0.5).angle - circuitPose(0).angle) * 180) / Math.PI,
      closingTurnDegrees:
        ((circuitPose(1).angle - circuitPose(0.5).angle) * 180) / Math.PI,
      totalTurnDegrees:
        ((circuitPose(1).angle - circuitPose(0).angle) * 180) / Math.PI,
      views,
    },
    null,
    2,
  ),
);
