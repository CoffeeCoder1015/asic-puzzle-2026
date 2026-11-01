import {
  BufferAttribute,
  BufferGeometry,
  ExtrudeGeometry,
  Matrix4,
  Path,
  Shape,
  Vector2,
} from "three";

type GdsPolygon = { hull: [number, number][]; holes: [number, number][][] };
type GdsPlacement = {
  cell: string;
  x: number;
  y: number;
  rotation: number;
  mirror: boolean;
};
export type GdsMetadata = {
  source: {
    path: string;
    dbuMicrons: number;
    bbox: [number, number, number, number];
  };
  layers: { id: string; name: string; zMin: number; zMax: number }[];
};

export type GdsLayout = GdsMetadata & {
  schemaVersion: 1;
  cells: { name: string; layers: { id: string; polygons: GdsPolygon[] }[] }[];
  placements: GdsPlacement[];
};

type Point3 = [number, number, number];

export type PreparedGdsGeometry = {
  positions: Float32Array<ArrayBuffer>;
  normals: Float32Array<ArrayBuffer>;
  boundingBox: { min: Point3; max: Point3 };
  boundingSphere: { center: Point3; radius: number };
};

/** Geometry slots retain the metadata's layer order, including empty layers. */
export type PreparedGdsLayout = GdsMetadata & {
  geometries: (PreparedGdsGeometry | null)[];
};

type GeometryPlacements = {
  geometry: BufferGeometry;
  placements: GdsPlacement[];
};

/** Reflection reverses handedness; reverse winding to retain the front faces. */
function mirroredGeometry(original: BufferGeometry) {
  const reflected = original.clone().scale(1, -1, 1);
  for (const attribute of Object.values(reflected.attributes)) {
    const values = attribute.array;
    const stride = attribute.itemSize;
    for (let triangle = 0; triangle < attribute.count; triangle += 3) {
      for (let item = 0; item < stride; item++) {
        const a = (triangle + 1) * stride + item;
        const b = (triangle + 2) * stride + item;
        [values[a], values[b]] = [values[b], values[a]];
      }
    }
    attribute.needsUpdate = true;
  }
  return reflected;
}

/** Extrude and bake static placements into transferable, renderer-independent data. */
export function prepareGdsLayout(data: GdsLayout): PreparedGdsLayout {
  const [minX, minY, maxX, maxY] = data.source.bbox;
  const scale = 6 / Math.max(maxX - minX, maxY - minY);
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;
  const zScale = scale / data.source.dbuMicrons;
  const layerRecords: GeometryPlacements[][] = data.layers.map(() => []);
  const temporaryGeometries = new Set<BufferGeometry>();
  const geometries: (PreparedGdsGeometry | null)[] = data.layers.map(() => null);

  for (const cell of data.cells) {
    const placements = data.placements.filter(
      (placement) => placement.cell === cell.name,
    );
    if (!placements.length) continue;
    for (const cellLayer of cell.layers) {
      const layerIndex = data.layers.findIndex(
        (layer) => layer.id === cellLayer.id,
      );
      const layer = data.layers[layerIndex];
      const shapes = cellLayer.polygons.map((polygon) => {
        const shape = new Shape(
          polygon.hull.map(([x, y]) => new Vector2(x * scale, y * scale)),
        );
        shape.holes = polygon.holes.map(
          (hole) =>
            new Path(hole.map(([x, y]) => new Vector2(x * scale, y * scale))),
        );
        return shape;
      });
      // One extrusion per unique cell/layer; repeated standard cells share it.
      const geometry = new ExtrudeGeometry(shapes, {
        depth: (layer.zMax - layer.zMin) * zScale,
        bevelEnabled: false,
        steps: 1,
      });
      // These materials have no textures, so only positions and normals are used.
      geometry.deleteAttribute("uv");
      temporaryGeometries.add(geometry);
      for (const mirror of [false, true]) {
        const instances = placements.filter(
          (placement) => placement.mirror === mirror,
        );
        if (!instances.length) continue;
        const instanceGeometry = mirror ? mirroredGeometry(geometry) : geometry;
        temporaryGeometries.add(instanceGeometry);
        layerRecords[layerIndex].push({
          geometry: instanceGeometry,
          placements: instances,
        });
      }
    }
  }

  layerRecords.forEach((records, layerIndex) => {
    if (!records.length) return;
    const layerZ = data.layers[layerIndex].zMin * zScale;
    const vertexCount = records.reduce(
      (count, record) =>
        count +
        record.geometry.getAttribute("position").count * record.placements.length,
      0,
    );
    const positions = new Float32Array(vertexCount * 3);
    const normals = new Float32Array(vertexCount * 3);
    const matrix = new Matrix4();
    // Match the Float32 placement transforms used by the renderer.
    const transform = new Float32Array(16);
    let offset = 0;

    for (const record of records) {
      const sourcePositions = record.geometry.getAttribute("position");
      const sourceNormals = record.geometry.getAttribute("normal");
      for (const placement of record.placements) {
        matrix.makeRotationZ((placement.rotation * Math.PI) / 180);
        matrix.setPosition(
          (placement.x - centerX) * scale,
          (placement.y - centerY) * scale,
          layerZ,
        );
        matrix.toArray(transform);
        for (let vertex = 0; vertex < sourcePositions.count; vertex++) {
          const x = sourcePositions.getX(vertex);
          const y = sourcePositions.getY(vertex);
          const z = sourcePositions.getZ(vertex);
          positions[offset] =
            transform[0] * x + transform[4] * y + transform[8] * z + transform[12];
          positions[offset + 1] =
            transform[1] * x + transform[5] * y + transform[9] * z + transform[13];
          positions[offset + 2] =
            transform[2] * x + transform[6] * y + transform[10] * z + transform[14];

          // Placements are rigid rotations; translation does not affect normals.
          const nx = sourceNormals.getX(vertex);
          const ny = sourceNormals.getY(vertex);
          const nz = sourceNormals.getZ(vertex);
          normals[offset] = transform[0] * nx + transform[4] * ny + transform[8] * nz;
          normals[offset + 1] =
            transform[1] * nx + transform[5] * ny + transform[9] * nz;
          normals[offset + 2] =
            transform[2] * nx + transform[6] * ny + transform[10] * nz;
          offset += 3;
        }
      }
    }

    const geometry = new BufferGeometry();
    geometry.setAttribute("position", new BufferAttribute(positions, 3));
    geometry.setAttribute("normal", new BufferAttribute(normals, 3));
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    geometries[layerIndex] = {
      positions,
      normals,
      boundingBox: {
        min: geometry.boundingBox!.min.toArray(),
        max: geometry.boundingBox!.max.toArray(),
      },
      boundingSphere: {
        center: geometry.boundingSphere!.center.toArray(),
        radius: geometry.boundingSphere!.radius,
      },
    };
    geometry.dispose();
  });

  temporaryGeometries.forEach((geometry) => geometry.dispose());
  temporaryGeometries.clear();
  return { source: data.source, layers: data.layers, geometries };
}
