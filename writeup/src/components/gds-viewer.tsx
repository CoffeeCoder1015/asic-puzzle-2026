"use client";

import dynamic from "next/dynamic";
import { publicAsset } from "../lib/public-asset";
import {
  Component,
  useCallback,
  useEffect,
  useId,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { Minus, Play, Plus, RotateCcw } from "lucide-react";
import { Button } from "./ui/button";
import type { PreparedGdsLayout } from "./gds-geometry";
import type { GdsWorkerRequest, GdsWorkerResponse } from "./gds-worker";
import type { GdsViewCommand } from "./gds-scene";
import { traceGds } from "./gds-profile";
import "./gds-viewer.css";

const GdsScene = dynamic(() => import("./gds-scene"), { ssr: false });
const LAYOUTS = {
  puzzle: { label: "Puzzle", fallback: publicAsset("/figures/puzzle-layout.svg") },
  warmup: { label: "Warm-up", fallback: publicAsset("/figures/warmup-gds-viewer.png") },
};
type LayoutId = keyof typeof LAYOUTS;
type Resource =
  | { status: "loading" }
  | { status: "loaded"; data: PreparedGdsLayout }
  | { status: "failed" };

class GdsBoundary extends Component<
  { children: React.ReactNode; resetKey: LayoutId; onFailure: () => void },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch() {
    this.props.onFailure();
  }
  componentDidUpdate(previous: Readonly<{ resetKey: LayoutId }>) {
    if (this.state.failed && previous.resetKey !== this.props.resetKey)
      this.setState({ failed: false });
  }
  render() {
    return this.state.failed ? null : this.props.children;
  }
}

/** The viewer owns both prepared layouts and one WebGL context until it unmounts. */
export function GdsViewer({
  storyProgress,
  activate = false,
  interactive = true,
  preload,
  onReplay,
  onSceneReady,
  onSceneFailure,
}: {
  storyProgress?: import("motion/react").MotionValue<number>;
  activate?: boolean;
  interactive?: boolean;
  preload: boolean;
  onReplay?: () => void;
  onSceneReady: () => void;
  onSceneFailure: () => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const description = useId();
  const slider = useId();
  const requests = useRef(new Map<LayoutId, "pending" | "loaded">());
  const worker = useRef<Worker | null>(null);
  const [layout, setLayout] = useState<LayoutId>("puzzle");
  const [inView, setInView] = useState(false);
  const [activated, setActivated] = useState(false);
  const [resources, setResources] = useState<
    Partial<Record<LayoutId, Resource>>
  >({});
  const [readyLayout, setReadyLayout] = useState<LayoutId | null>(null);
  const [canvasFailed, setCanvasFailed] = useState(false);
  const [separation, setSeparation] = useState(0);
  const [command, setCommand] = useState<GdsViewCommand>({
    action: "reset",
    sequence: 0,
  });
  const ready = readyLayout === layout;
  const failed = resources[layout]?.status === "failed" || canvasFailed;
  const models = useMemo(
    () =>
      Object.entries(resources).flatMap(([id, resource]) =>
        resource.status === "loaded" ? [{ id, data: resource.data }] : [],
      ),
    [resources],
  );

  useLayoutEffect(() => {
    if (interactive) setSeparation(0);
  }, [interactive]);
  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      setInView(entry.isIntersecting);
      if (entry.isIntersecting) setActivated(true);
    });
    observer.observe(host.current!);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    if (activate) setActivated(true);
  }, [activate]);

  const loadLayout = useCallback((id: LayoutId) => {
    if (requests.current.has(id)) return;
    requests.current.set(id, "pending");
    setResources((previous) => ({ ...previous, [id]: { status: "loading" } }));
    traceGds(id, "fetch-start");

    // A worker failure leaves loaded models cached and releases pending IDs for
    // a later reader selection. This callback stays stable, so failure cannot
    // retrigger the activation effect and create a retry loop.
    const failPending = () => {
      worker.current?.terminate();
      worker.current = null;
      const failed: LayoutId[] = [];
      requests.current.forEach((status, pendingId) => {
        if (status !== "pending") return;
        requests.current.delete(pendingId);
        failed.push(pendingId);
        traceGds(pendingId, "failed");
      });
      setResources((previous) => {
        const next = { ...previous };
        failed.forEach((pendingId) => {
          next[pendingId] = { status: "failed" };
        });
        return next;
      });
    };

    try {
      if (!worker.current) {
        const nextWorker = new Worker(new URL("./gds-worker.ts", import.meta.url));
        nextWorker.onmessage = ({
          data: message,
        }: MessageEvent<GdsWorkerResponse>) => {
          if (worker.current !== nextWorker) return;
          if (requests.current.get(message.id) !== "pending") return;
          if (message.status === "progress") {
            traceGds(message.id, message.phase);
            return;
          }
          if (message.status === "loaded") {
            requests.current.set(message.id, "loaded");
            setResources((previous) => ({
              ...previous,
              [message.id]: { status: "loaded", data: message.data },
            }));
          } else {
            requests.current.delete(message.id);
            traceGds(message.id, "failed");
            setResources((previous) => ({
              ...previous,
              [message.id]: { status: "failed" },
            }));
          }
        };
        const workerFailed = () => {
          if (worker.current === nextWorker) failPending();
        };
        nextWorker.onerror = workerFailed;
        nextWorker.onmessageerror = workerFailed;
        worker.current = nextWorker;
      }
      const request: GdsWorkerRequest = {
        id,
        url: new URL(publicAsset(`/data/${id}-layout.json`), window.location.href).href,
      };
      worker.current.postMessage(request);
    } catch {
      failPending();
    }
  }, []);
  useEffect(() => {
    if (activated) loadLayout(layout);
  }, [activated, layout, loadLayout]);
  useEffect(() => {
    const pending = requests.current;
    return () => {
      worker.current?.terminate();
      worker.current = null;
      pending.clear();
    };
  }, []);
  useEffect(() => {
    if (!activated || !ready || !preload) return;
    const loadOther = () => loadLayout(layout === "puzzle" ? "warmup" : "puzzle");
    if (window.requestIdleCallback) {
      const idle = window.requestIdleCallback(loadOther);
      return () => window.cancelIdleCallback(idle);
    }
    const timer = window.setTimeout(loadOther, 200);
    return () => window.clearTimeout(timer);
  }, [activated, ready, preload, layout, loadLayout]);
  useEffect(() => {
    if (failed) onSceneFailure();
  }, [failed, onSceneFailure]);

  const issue = (action: GdsViewCommand["action"]) =>
    setCommand((previous) => ({ action, sequence: previous.sequence + 1 }));
  const select = (id: LayoutId) => {
    if (id === layout && !failed) return;
    traceGds(id, "selected");
    setReadyLayout(null);
    setCanvasFailed(false);
    setSeparation(0);
    issue("reset");
    setLayout(id);
    if (activated) loadLayout(id);
  };

  return (
    <div
      className="gds-viewer"
      ref={host}
      data-layout={layout}
      data-ready={ready && !failed}
      data-fallback={failed || !activated}
      aria-busy={!ready && !failed}
    >
      <div
        className="gds-viewer__stage"
        role="img"
        aria-describedby={description}
        aria-label={`${LAYOUTS[layout].label} ASIC physical layout in three dimensions`}
      >
        <img
          className="gds-viewer__fallback"
          src={LAYOUTS[layout].fallback}
          alt=""
          width="2559"
          height="1470"
        />
        {models.length > 0 && !canvasFailed && (
          <GdsBoundary
            resetKey={layout}
            onFailure={() => setCanvasFailed(true)}
          >
            <GdsScene
              models={models}
              selected={failed ? null : layout}
              storyProgress={storyProgress}
              interactive={interactive}
              active={inView}
              separation={separation}
              command={command}
              onReady={() => {
                traceGds(layout, "scene-ready");
                setReadyLayout(layout);
                onSceneReady();
              }}
              onFailure={() => setCanvasFailed(true)}
            />
          </GdsBoundary>
        )}
        {activated && !ready && !failed && (
          <span className="gds-viewer__loading" role="status">
            Loading layout…
          </span>
        )}
      </div>
      <div className="gds-viewer__header">
        <p
          id={description}
          className="gds-viewer__description"
          aria-live="polite"
        >
          {failed
            ? "3D view unavailable. Showing the layout image."
            : "Layer spacing and colors are illustrative."}
          {ready && !failed && " Drag to orbit."}
        </p>
        <div
          className="gds-viewer__selection"
          role="group"
          aria-label="Circuit layout"
        >
          {(Object.keys(LAYOUTS) as LayoutId[]).map((id) => (
            <Button
              key={id}
              variant="ghost"
              size="sm"
              aria-pressed={layout === id}
              disabled={!interactive}
              onClick={() => select(id)}
            >
              {LAYOUTS[id].label}
            </Button>
          ))}
        </div>
      </div>
      <div className="gds-viewer__controls" aria-label="Layout view controls">
        <div className="gds-viewer__buttons">
          <Button
            variant="ghost"
            size="icon"
            aria-label="Zoom in on layout"
            disabled={!ready || failed || !interactive}
            onClick={() => issue("in")}
          >
            <Plus aria-hidden="true" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Zoom out from layout"
            disabled={!ready || failed || !interactive}
            onClick={() => issue("out")}
          >
            <Minus aria-hidden="true" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Reset layout view"
            disabled={!ready || failed || !interactive}
            onClick={() => {
              setSeparation(0);
              issue("reset");
            }}
          >
            <RotateCcw aria-hidden="true" />
          </Button>
        </div>
        {onReplay && (
          <Button
            className="gds-viewer__replay"
            variant="ghost"
            size="sm"
            disabled={!ready || failed || !interactive}
            onClick={onReplay}
          >
            <Play aria-hidden="true" /> Replay entry
          </Button>
        )}
        <label className="gds-viewer__spacing" htmlFor={slider}>
          Separate layers
          <input
            id={slider}
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={separation}
            disabled={!ready || failed || !interactive}
            onChange={(event) => setSeparation(Number(event.target.value))}
          />
        </label>
      </div>
    </div>
  );
}
