import {
  Box3,
  BufferAttribute,
  BufferGeometry,
  DoubleSide,
  Group,
  Mesh,
  MeshStandardMaterial,
  Sphere,
  Vector3,
} from "three";
import type { PreparedGdsLayout } from "./gds-geometry";
import { traceGds } from "./gds-profile";

const PALETTE = [
  "#192b22",
  "#547661",
  "#91ac83",
  "#b6a374",
  "#b2c5a1",
  "#89bfa1",
  "#b7caac",
  "#b3d8c0",
  "#d4be88",
  "#acd9bd",
  "#c0c9ac",
  "#a0ceb6",
  "#d4c69c",
  "#9ed7b8",
  "#bbc8b0",
  "#e0d1a1",
];

/** Assemble prepared buffers without scanning vertices; own geometry and materials. */
export function buildGdsLayout(data: PreparedGdsLayout) {
  traceGds(data.source.path, "assembly-start");
  const group = new Group();
  group.rotation.x = -Math.PI / 2;
  const layers = data.layers.map(() => new Group());
  layers.forEach((layer) => group.add(layer));
  const geometries: BufferGeometry[] = [];
  const materials = data.layers.map(
    (layer, index) =>
      new MeshStandardMaterial({
        color: PALETTE[index],
        metalness: index > 4 ? 0.48 : 0.18,
        roughness: 0.38,
        transparent: index > 0,
        opacity: index > 0 ? 0.78 : 1,
        side: DoubleSide,
        forceSinglePass: true,
      }),
  );

  data.geometries.forEach((prepared, layerIndex) => {
    if (!prepared) return;
    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(prepared.positions, 3));
    geometry.setAttribute("normal", new BufferAttribute(prepared.normals, 3));
    geometry.boundingBox = new Box3(
      new Vector3(...prepared.boundingBox.min),
      new Vector3(...prepared.boundingBox.max),
    );
    geometry.boundingSphere = new Sphere(
      new Vector3(...prepared.boundingSphere.center),
      prepared.boundingSphere.radius,
    );
    geometries.push(geometry);
    layers[layerIndex].add(new Mesh(geometry, materials[layerIndex]));
  });

  traceGds(data.source.path, "assembly-end");
  return {
    group,
    layers,
    dispose: () => {
      geometries.forEach((geometry) => geometry.dispose());
      materials.forEach((material) => material.dispose());
    },
  };
}
