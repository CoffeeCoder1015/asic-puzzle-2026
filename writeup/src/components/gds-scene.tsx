"use client";

import type { MotionValue } from "motion/react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import type { PointLight, PerspectiveCamera } from "three";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { circuitPose } from "./circuit-choreography";
import {
  createGdsEnvelope,
  fitGdsStory,
  type GdsEnvelope,
} from "./gds-framing";
import {
  beginAnimationWork,
  endAnimationWork,
  observeSceneWork,
} from "./animation-profile";
import { buildGdsLayout } from "./gds-layout";
import type { PreparedGdsLayout } from "./gds-geometry";

export type GdsViewCommand = {
  action: "in" | "out" | "reset";
  sequence: number;
};

function LayoutScene({
  data,
  selected,
  separation,
  storyProgress,
  interactive,
}: {
  data: PreparedGdsLayout;
  selected: boolean;
  separation: number;
  storyProgress?: MotionValue<number>;
  interactive: boolean;
}) {
  const { invalidate } = useThree();
  const layout = useMemo(() => buildGdsLayout(data), [data]);
  useLayoutEffect(() => {
    if (!selected || !interactive) return;
    layout.layers.forEach((layer, index) => {
      layer.position.z = index * separation * 0.16;
    });
    invalidate();
  }, [layout, selected, separation, interactive, invalidate]);
  useFrame(() => {
    if (!selected || interactive || !storyProgress) return;
    const pose = circuitPose(storyProgress.get());
    layout.layers.forEach((layer, index) => {
      layer.position.z = index * pose.spacing * 0.16;
    });
  });
  useEffect(() => () => layout.dispose(), [layout]);
  return <primitive object={layout.group} visible={selected} dispose={null} />;
}

function SceneView({
  envelope,
  active,
  interactive,
  storyProgress,
  command,
  onReady,
  onFailure,
}: {
  envelope: GdsEnvelope;
  active: boolean;
  interactive: boolean;
  storyProgress?: MotionValue<number>;
  command: GdsViewCommand;
  onReady: () => void;
  onFailure: () => void;
}) {
  const controls = useRef<OrbitControlsImpl>(null);
  const inspectionLight = useRef<PointLight>(null);
  const firstFrame = useRef(true);
  const readyFrame = useRef(0);
  const wasInteractive = useRef(false);
  const handledCommand = useRef(command.sequence);
  const zoomedByReader = useRef(false);
  const { camera, gl, invalidate, size } = useThree();
  useEffect(() => () => cancelAnimationFrame(readyFrame.current), []);
  useEffect(() => observeSceneWork(gl), [gl]);
  const fov = (camera as PerspectiveCamera).fov;
  const storyZoom = useMemo(() => {
    const start = beginAnimationWork();
    const zoom = fitGdsStory(
      envelope,
      fov,
      size.width / size.height,
      circuitPose,
    );
    endAnimationWork("framing", start, 1001);
    return zoom;
  }, [envelope, fov, size.width, size.height]);
  useLayoutEffect(() => {
    const orbit = controls.current!;
    if (firstFrame.current) {
      camera.position.set(7, 6.5, 9);
      orbit.target.set(0, 0.35, 0);
      camera.lookAt(orbit.target);
    }
    if (interactive && !wasInteractive.current && storyProgress) {
      const pose = circuitPose(1);
      camera.position.set(pose.camera[0], pose.camera[1], pose.camera[2]);
      orbit.target.set(pose.target[0], pose.target[1], pose.target[2]);
      camera.lookAt(orbit.target);
    }
    wasInteractive.current = interactive;
    if (!interactive) {
      zoomedByReader.current = false;
      // Discard any remaining manual orbit damping before the story owns the view.
      orbit.enableDamping = false;
      orbit.update();
    }
    if (!zoomedByReader.current) {
      (camera as PerspectiveCamera).zoom = storyZoom;
      camera.updateProjectionMatrix();
    }
    invalidate();
  }, [camera, storyZoom, interactive, storyProgress, invalidate]);
  useEffect(() => {
    if (active) invalidate();
  }, [active, interactive, invalidate]);
  useEffect(
    () => storyProgress?.on("change", () => invalidate()),
    [storyProgress, invalidate],
  );
  useFrame(() => {
    if (firstFrame.current) {
      firstFrame.current = false;
      // Notify after this render has completed, rather than before its GPU upload.
      readyFrame.current = requestAnimationFrame(onReady);
    }
    if (!interactive && storyProgress) {
      const pose = circuitPose(storyProgress.get());
      camera.position.set(pose.camera[0], pose.camera[1], pose.camera[2]);
      controls.current!.target.set(
        pose.target[0],
        pose.target[1],
        pose.target[2],
      );
      camera.lookAt(pose.target[0], pose.target[1], pose.target[2]);
      if (inspectionLight.current) {
        inspectionLight.current.position.set(
          Math.sin(pose.angle + 1) * 8,
          6,
          Math.cos(pose.angle + 1) * 8,
        );
        inspectionLight.current.intensity = pose.light;
      }
    }
    if (interactive && inspectionLight.current)
      inspectionLight.current.intensity = 0;
  });
  useEffect(() => {
    if (!interactive || command.sequence === handledCommand.current) return;
    const orbit = controls.current!;
    const damping = orbit.enableDamping;
    orbit.enableDamping = false;
    orbit.update();
    if (command.action === "reset") {
      zoomedByReader.current = false;
      camera.position.set(7, 6.5, 9);
      orbit.target.set(0, 0.35, 0);
      (camera as PerspectiveCamera).zoom = storyZoom;
      camera.updateProjectionMatrix();
    } else {
      zoomedByReader.current = true;
      camera.position
        .sub(orbit.target)
        .multiplyScalar(command.action === "in" ? 0.8 : 1.25)
        .add(orbit.target);
    }
    handledCommand.current = command.sequence;
    orbit.update();
    orbit.enableDamping = damping;
    invalidate();
  }, [command, interactive, camera, storyZoom, invalidate]);
  useEffect(() => {
    const lost = (event: Event) => {
      event.preventDefault();
      onFailure();
    };
    gl.domElement.addEventListener("webglcontextlost", lost);
    return () => gl.domElement.removeEventListener("webglcontextlost", lost);
  }, [gl, onFailure]);
  return (
    <>
      <pointLight ref={inspectionLight} color="#e7d6a6" intensity={0} />
      <OrbitControls
        ref={controls}
        makeDefault
        enabled={active && interactive}
        enableZoom={false}
        enableRotate={interactive}
        enablePan={false}
        enableDamping={active && interactive}
        minDistance={3}
        maxDistance={28}
        minPolarAngle={0.12}
        maxPolarAngle={Math.PI * 0.48}
      />
    </>
  );
}

export default function GdsScene({
  models,
  selected,
  active,
  interactive,
  storyProgress,
  separation,
  command,
  onReady,
  onFailure,
}: {
  models: { id: string; data: PreparedGdsLayout }[];
  selected: string | null;
  active: boolean;
  interactive: boolean;
  storyProgress?: MotionValue<number>;
  separation: number;
  command: GdsViewCommand;
  onReady: () => void;
  onFailure: () => void;
}) {
  const data = models.find((model) => model.id === selected)?.data;
  const envelope = useMemo(
    () => (data ? createGdsEnvelope(data) : null),
    [data],
  );
  return (
    <Canvas
      className="gds-viewer__canvas"
      dpr={[1, 1.5]}
      frameloop="demand"
      resize={{ scroll: false }}
      camera={{ position: [7, 6.5, 9], fov: 31, near: 0.1, far: 100 }}
      gl={{ alpha: true, antialias: true, powerPreference: "low-power" }}
      fallback={null}
    >
      <ambientLight intensity={1.5} />
      <directionalLight position={[-4, 8, 5]} color="#e2f5e7" intensity={3} />
      <directionalLight position={[5, 3, -4]} color="#a4d9bd" intensity={2.5} />
      {models.map((model) => (
        <LayoutScene
          key={model.id}
          data={model.data}
          selected={model.id === selected}
          separation={separation}
          storyProgress={storyProgress}
          interactive={interactive}
        />
      ))}
      {envelope && (
        <SceneView
          key={selected}
          envelope={envelope}
          active={active}
          interactive={interactive}
          storyProgress={storyProgress}
          command={command}
          onReady={onReady}
          onFailure={onFailure}
        />
      )}
    </Canvas>
  );
}
