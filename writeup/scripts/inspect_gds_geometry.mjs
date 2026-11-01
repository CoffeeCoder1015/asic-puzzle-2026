import { readFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import { Matrix3, Matrix4, Vector3 } from "../node_modules/three/build/three.module.js";
import layoutModule from "../src/components/gds-layout.ts";
import geometryModule from "../src/components/gds-geometry.ts";

const referencePath = process.argv[2];
if (!referencePath) throw new Error("Supply the retained reference builder module path.");
const referenceModule = await import(pathToFileURL(referencePath));
const reference = referenceModule.default ?? referenceModule;
const { buildGdsLayout } = layoutModule;
const { prepareGdsLayout } = geometryModule;

function* vertices(layer) {
  const matrix = new Matrix4();
  const normalMatrix = new Matrix3();
  const position = new Vector3();
  const normal = new Vector3();
  const sample = { position, normal };
  for (const mesh of layer.children) {
    const positions = mesh.geometry.getAttribute("position");
    const normals = mesh.geometry.getAttribute("normal");
    const instances = mesh.isInstancedMesh ? mesh.count : 1;
    for (let instance = 0; instance < instances; instance++) {
      if (mesh.isInstancedMesh) mesh.getMatrixAt(instance, matrix);
      else matrix.copy(mesh.matrix);
      normalMatrix.getNormalMatrix(matrix);
      for (let vertex = 0; vertex < positions.count; vertex++) {
        position.fromBufferAttribute(positions, vertex).applyMatrix4(matrix);
        normal.fromBufferAttribute(normals, vertex).applyNormalMatrix(normalMatrix);
        yield sample;
      }
    }
  }
}

const summaries = [];
for (const id of ["warmup", "puzzle"]) {
  const data = JSON.parse(await readFile(new URL(`../public/data/${id}-layout.json`, import.meta.url), "utf8"));
  const before = reference.buildGdsLayout(data, false);
  const after = buildGdsLayout(prepareGdsLayout(data));
  const layers = data.layers.map((layer, index) => {
    const a = vertices(before.layers[index]);
    const b = vertices(after.layers[index]);
    let count = 0, maxPositionDifference = 0, maxNormalDifference = 0;
    let left, right;
    while (true) {
      left = a.next(); right = b.next();
      if (left.done || right.done) break;
      for (const axis of ["x", "y", "z"]) {
        maxPositionDifference = Math.max(maxPositionDifference, Math.abs(left.value.position[axis] - right.value.position[axis]));
        maxNormalDifference = Math.max(maxNormalDifference, Math.abs(left.value.normal[axis] - right.value.normal[axis]));
      }
      count++;
    }
    return { id: layer.id, verticesCompared: count, sameLength: left.done === right.done,
      maxPositionDifference, maxNormalDifference,
      inputObjects: before.layers[index].children.length, outputObjects: after.layers[index].children.length };
  });
  summaries.push({ id, outerRotationUnchanged: before.group.rotation.equals(after.group.rotation), layers });
  before.dispose(); after.dispose();
}
console.log(JSON.stringify(summaries, null, 2));
