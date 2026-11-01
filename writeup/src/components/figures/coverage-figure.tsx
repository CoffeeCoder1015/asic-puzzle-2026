"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import { Pause, Play, RotateCcw, ArrowRight } from "lucide-react";
import { Button } from "../ui/button";
import "./coverage-figure.css";

type CircuitNode = Readonly<{
  id: string;
  x: number;
  y: number;
  stage: number;
  kind: "bus" | "and" | "xor" | "register";
}>;
const NODES: readonly CircuitNode[] = [
  { id: "input", x: 320, y: 60, stage: 0, kind: "bus" },
  { id: "n10", x: 170, y: 131, stage: 1, kind: "xor" },
  { id: "n11", x: 270, y: 131, stage: 1, kind: "register" },
  { id: "n12", x: 390, y: 131, stage: 1, kind: "and" },
  { id: "n13", x: 480, y: 131, stage: 1, kind: "xor" },
  { id: "n20", x: 95, y: 197, stage: 2, kind: "register" },
  { id: "n21", x: 185, y: 197, stage: 2, kind: "and" },
  { id: "n22", x: 260, y: 197, stage: 2, kind: "xor" },
  { id: "n23", x: 345, y: 197, stage: 2, kind: "register" },
  { id: "n24", x: 420, y: 197, stage: 2, kind: "and" },
  { id: "n25", x: 505, y: 197, stage: 2, kind: "xor" },
  { id: "n26", x: 565, y: 197, stage: 2, kind: "register" },
  { id: "n30", x: 60, y: 263, stage: 3, kind: "and" },
  { id: "n31", x: 135, y: 263, stage: 3, kind: "xor" },
  { id: "n32", x: 215, y: 263, stage: 3, kind: "register" },
  { id: "n33", x: 285, y: 263, stage: 3, kind: "and" },
  { id: "n34", x: 365, y: 263, stage: 3, kind: "xor" },
  { id: "n35", x: 440, y: 263, stage: 3, kind: "register" },
  { id: "n36", x: 515, y: 263, stage: 3, kind: "and" },
  { id: "n37", x: 585, y: 263, stage: 3, kind: "xor" },
  { id: "n40", x: 105, y: 329, stage: 4, kind: "xor" },
  { id: "n41", x: 185, y: 329, stage: 4, kind: "register" },
  { id: "n42", x: 270, y: 329, stage: 4, kind: "and" },
  { id: "n43", x: 350, y: 329, stage: 4, kind: "xor" },
  { id: "n44", x: 425, y: 329, stage: 4, kind: "register" },
  { id: "n45", x: 510, y: 329, stage: 4, kind: "and" },
  { id: "n46", x: 565, y: 329, stage: 4, kind: "xor" },
  { id: "n50", x: 155, y: 395, stage: 5, kind: "register" },
  { id: "n51", x: 240, y: 395, stage: 5, kind: "and" },
  { id: "n52", x: 320, y: 395, stage: 5, kind: "xor" },
  { id: "n53", x: 410, y: 395, stage: 5, kind: "register" },
  { id: "n54", x: 485, y: 395, stage: 5, kind: "and" },
  { id: "n55", x: 550, y: 395, stage: 5, kind: "xor" },
  { id: "n60", x: 240, y: 461, stage: 6, kind: "and" },
  { id: "n61", x: 335, y: 461, stage: 6, kind: "xor" },
  { id: "n62", x: 425, y: 461, stage: 6, kind: "register" },
  { id: "output", x: 320, y: 540, stage: 7, kind: "bus" },
];
const NODE_BY_ID = Object.fromEntries(NODES.map((node) => [node.id, node]));
const EDGES = [
  { id: "input-n10", source: "input", target: "n10" },
  { id: "n10-n20", source: "n10", target: "n20" },
  { id: "n20-n30", source: "n20", target: "n30" },
  { id: "n30-n40", source: "n30", target: "n40" },
  { id: "n40-n50", source: "n40", target: "n50" },
  { id: "n50-n60", source: "n50", target: "n60" },
  { id: "n60-output", source: "n60", target: "output" },
  { id: "input-n11", source: "input", target: "n11" },
  { id: "n11-n22", source: "n11", target: "n22" },
  { id: "n22-n32", source: "n22", target: "n32" },
  { id: "n32-n41", source: "n32", target: "n41" },
  { id: "n41-n51", source: "n41", target: "n51" },
  { id: "n51-n60", source: "n51", target: "n60" },
  { id: "input-n12", source: "input", target: "n12" },
  { id: "n12-n23", source: "n12", target: "n23" },
  { id: "n23-n34", source: "n23", target: "n34" },
  { id: "n34-n43", source: "n34", target: "n43" },
  { id: "n43-n52", source: "n43", target: "n52" },
  { id: "n52-n61", source: "n52", target: "n61" },
  { id: "n61-output", source: "n61", target: "output" },
  { id: "n10-n21", source: "n10", target: "n21" },
  { id: "n21-n31", source: "n21", target: "n31" },
  { id: "n31-n42", source: "n31", target: "n42" },
  { id: "n42-n52", source: "n42", target: "n52" },
  { id: "n12-n24", source: "n12", target: "n24" },
  { id: "n24-n35", source: "n24", target: "n35" },
  { id: "n35-n44", source: "n35", target: "n44" },
  { id: "n44-n53", source: "n44", target: "n53" },
  { id: "n53-n62", source: "n53", target: "n62" },
  { id: "n62-output", source: "n62", target: "output" },
  { id: "n22-n33", source: "n22", target: "n33" },
  { id: "n33-n42", source: "n33", target: "n42" },
  { id: "n42-n51", source: "n42", target: "n51" },
  { id: "input-n13", source: "input", target: "n13" },
  { id: "n13-n26", source: "n13", target: "n26" },
  { id: "n26-n37", source: "n26", target: "n37" },
  { id: "n37-n46", source: "n37", target: "n46" },
  { id: "n46-n55", source: "n46", target: "n55" },
  { id: "n55-n62", source: "n55", target: "n62" },
  { id: "n13-n25", source: "n13", target: "n25" },
  { id: "n25-n36", source: "n25", target: "n36" },
  { id: "n36-n45", source: "n36", target: "n45" },
  { id: "n45-n54", source: "n45", target: "n54" },
  { id: "n54-n62", source: "n54", target: "n62" },
  { id: "n21-n32", source: "n21", target: "n32" },
  { id: "n23-n33", source: "n23", target: "n33" },
  { id: "n34-n44", source: "n34", target: "n44" },
  { id: "n41-n52", source: "n41", target: "n52" },
  { id: "n43-n53", source: "n43", target: "n53" },
  { id: "n50-n61", source: "n50", target: "n61" },
] as const;

// Explicit illustrative routes: edge coverage is never inferred from node coverage.
const TRIALS = [
  {
    bits: "10100110",
    activeNodeIds: [
      "input",
      "n10",
      "n20",
      "n30",
      "n40",
      "n50",
      "n60",
      "output",
      "n11",
      "n22",
      "n32",
      "n41",
      "n51",
    ],
    activeEdgeIds: [
      "input-n10",
      "n10-n20",
      "n20-n30",
      "n30-n40",
      "n40-n50",
      "n50-n60",
      "n60-output",
      "input-n11",
      "n11-n22",
      "n22-n32",
      "n32-n41",
      "n41-n51",
      "n51-n60",
    ],
  },
  {
    bits: "01101001",
    activeNodeIds: [
      "input",
      "n11",
      "n22",
      "n32",
      "n41",
      "n51",
      "n60",
      "output",
    ],
    activeEdgeIds: [
      "input-n11",
      "n11-n22",
      "n22-n32",
      "n32-n41",
      "n41-n51",
      "n51-n60",
      "n60-output",
    ],
  },
  {
    bits: "11010010",
    activeNodeIds: [
      "input",
      "n12",
      "n23",
      "n34",
      "n43",
      "n52",
      "n61",
      "output",
      "n10",
      "n21",
      "n31",
      "n42",
    ],
    activeEdgeIds: [
      "input-n12",
      "n12-n23",
      "n23-n34",
      "n34-n43",
      "n43-n52",
      "n52-n61",
      "n61-output",
      "input-n10",
      "n10-n21",
      "n21-n31",
      "n31-n42",
      "n42-n52",
    ],
  },
  {
    bits: "00110111",
    activeNodeIds: [
      "input",
      "n10",
      "n21",
      "n31",
      "n42",
      "n52",
      "n61",
      "output",
    ],
    activeEdgeIds: [
      "input-n10",
      "n10-n21",
      "n21-n31",
      "n31-n42",
      "n42-n52",
      "n52-n61",
      "n61-output",
    ],
  },
  {
    bits: "10011000",
    activeNodeIds: [
      "input",
      "n12",
      "n24",
      "n35",
      "n44",
      "n53",
      "n62",
      "output",
      "n11",
      "n22",
      "n33",
      "n42",
      "n51",
      "n60",
    ],
    activeEdgeIds: [
      "input-n12",
      "n12-n24",
      "n24-n35",
      "n35-n44",
      "n44-n53",
      "n53-n62",
      "n62-output",
      "input-n11",
      "n11-n22",
      "n22-n33",
      "n33-n42",
      "n42-n51",
      "n51-n60",
      "n60-output",
    ],
  },
  {
    bits: "01001101",
    activeNodeIds: [
      "input",
      "n11",
      "n22",
      "n33",
      "n42",
      "n51",
      "n60",
      "output",
    ],
    activeEdgeIds: [
      "input-n11",
      "n11-n22",
      "n22-n33",
      "n33-n42",
      "n42-n51",
      "n51-n60",
      "n60-output",
    ],
  },
] as const;
const TRIAL_DURATION = 3400;
const CYCLE_END_DURATION = 5000;

function nodeShape(node: CircuitNode) {
  if (node.kind === "bus")
    return <rect x="-70" y="-14" width="140" height="28" rx="3" />;
  if (node.kind === "register")
    return (
      <>
        <rect x="-13" y="-15" width="26" height="30" />
        <path className="gate-detail" d="M-5 -15L0 -9L5 -15M-6 3H6" />
      </>
    );
  if (node.kind === "and")
    return (
      <path transform="rotate(90)" d="M-15 -14H0Q15 -14 15 0Q15 14 0 14H-15Z" />
    );
  return (
    <>
      <path
        transform="rotate(90)"
        d="M-15 -14Q0 -10 15 0Q0 10 -15 14Q-6 0 -15 -14Z"
      />
      <path
        transform="rotate(90)"
        className="gate-detail"
        d="M-20 -14Q-11 0 -20 14"
      />
    </>
  );
}

function edgePath(source: CircuitNode, target: CircuitNode) {
  const y1 = source.y + (source.kind === "bus" ? 14 : 15);
  const y2 = target.y - (target.kind === "bus" ? 14 : 15);
  const turn = y1 + (y2 - y1) * 0.5;
  return `M${source.x} ${y1}V${turn}H${target.x}V${y2}`;
}

export function CoverageFigure() {
  const root = useRef<HTMLElement>(null);
  const [step, setStep] = useState(0);
  const [playback, setPlayback] = useState<"playing" | "paused" | "manual">(
    "playing",
  );
  const [mounted, setMounted] = useState(false);
  const [motionAllowed, setMotionAllowed] = useState(false);
  const [arrivalsReady, setArrivalsReady] = useState(false);
  const [replay, setReplay] = useState(0);
  const remaining = useRef(TRIAL_DURATION);
  const trial = TRIALS[step];
  const reached = new Set<string>(
    TRIALS.slice(0, step + 1).flatMap((trial) => [...trial.activeNodeIds]),
  );
  const previouslyReached = new Set<string>(
    TRIALS.slice(0, step).flatMap((trial) => [...trial.activeNodeIds]),
  );
  const previousEdges = new Set<string>(
    TRIALS.slice(0, step).flatMap((trial) => [...trial.activeEdgeIds]),
  );
  const reachedEdges = new Set<string>(
    TRIALS.slice(0, step + 1).flatMap((trial) => [...trial.activeEdgeIds]),
  );
  const current = new Set<string>(trial.activeNodeIds);
  const currentEdges = new Set<string>(trial.activeEdgeIds);
  const trialDuration =
    step === TRIALS.length - 1 ? CYCLE_END_DURATION : TRIAL_DURATION;

  useEffect(() => {
    setMounted(true);
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    let inView = false;
    const update = () =>
      setMotionAllowed(inView && !document.hidden && !preference.matches);
    const observer = new IntersectionObserver(
      ([entry]) => {
        inView = entry.isIntersecting;
        update();
      },
      { threshold: 0.2 },
    );
    observer.observe(root.current!);
    preference.addEventListener("change", update);
    document.addEventListener("visibilitychange", update);
    return () => {
      observer.disconnect();
      preference.removeEventListener("change", update);
      document.removeEventListener("visibilitychange", update);
    };
  }, []);

  useEffect(() => {
    remaining.current = trialDuration;
  }, [step, replay, trialDuration]);

  useEffect(() => {
    if (motionAllowed) setArrivalsReady(true);
  }, [motionAllowed]);

  useEffect(() => {
    if (playback !== "playing" || !motionAllowed) return;
    const started = performance.now();
    const timer = window.setTimeout(() => {
      setStep((value) => (value + 1) % TRIALS.length);
    }, remaining.current);
    return () => {
      window.clearTimeout(timer);
      remaining.current = Math.max(
        0,
        remaining.current - (performance.now() - started),
      );
    };
  }, [step, playback, motionAllowed, replay]);

  return (
    <figure
      ref={root}
      className="figure--wide coverage-scene"
      data-asset-kind="programmatic"
      data-arrivals={arrivalsReady ? "ready" : "static"}
      data-motion={motionAllowed && playback !== "paused" ? "on" : "off"}
    >
      <div className="coverage-scene__field">
        <svg
          viewBox="0 0 640 580"
          role="img"
          aria-label={`Illustrative circuit, input ${step + 1}, illustrative bit preview ${trial.bits}, not the full 121-bit serial input. ${reached.size} of ${NODES.length} items reached; ${reachedEdges.size} routes reached.`}
        >
          <text
            className="coverage-scene__input-label"
            x="320"
            y="28"
            textAnchor="middle"
          >
            Input {step + 1}
          </text>
          <text
            className="coverage-scene__count"
            x="602"
            y="28"
            textAnchor="end"
          >
            {NODES.length - reached.size} unreached
          </text>
          <g className="coverage-scene__edges" fill="none">
            {EDGES.map((edge) => {
              const source = NODE_BY_ID[edge.source];
              const target = NODE_BY_ID[edge.target];
              const d = edgePath(source, target);
              return (
                <g key={edge.id}>
                  <path
                    className={previousEdges.has(edge.id) ? "is-reached" : ""}
                    d={d}
                  />
                  {currentEdges.has(edge.id) && (
                    <path
                      key={`${step}-${replay}`}
                      className="is-current coverage-scene__trace"
                      pathLength="1"
                      d={d}
                      style={
                        {
                          "--arrival-delay": `${source.stage * 240}ms`,
                        } as CSSProperties
                      }
                    />
                  )}
                </g>
              );
            })}
          </g>
          {NODES.map((node) => (
            <g
              key={node.id}
              className={
                node.kind === "bus" ? "coverage-scene__bus" : undefined
              }
              transform={`translate(${node.x} ${node.y})`}
            >
              <g
                className={`coverage-scene__node${previouslyReached.has(node.id) ? " is-reached" : ""}`}
              >
                {nodeShape(node)}
              </g>
              {current.has(node.id) && (
                <g
                  key={`${step}-${replay}`}
                  className="coverage-scene__node is-current coverage-scene__arrival"
                  style={
                    {
                      "--arrival-delay": `${node.stage * 240}ms`,
                    } as CSSProperties
                  }
                >
                  {nodeShape(node)}
                </g>
              )}
            </g>
          ))}
          <text
            className="coverage-scene__bits"
            x="320"
            y="65"
            textAnchor="middle"
          >
            {trial.bits}…
          </text>
          <text
            className="coverage-scene__bits"
            x="320"
            y="545"
            textAnchor="middle"
          >
            O[7:0]
          </text>
        </svg>
        <div className="coverage-scene__footer">
          <div className="coverage-scene__controls" hidden={!mounted}>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setPlayback("manual");
                setStep((value) => (value + 1) % TRIALS.length);
              }}
            >
              Next input <ArrowRight />
            </Button>
            <Button
              size="icon-sm"
              variant="ghost"
              aria-label={
                playback === "playing"
                  ? "Pause coverage animation"
                  : "Play coverage animation"
              }
              aria-pressed={playback === "playing"}
              onClick={() =>
                setPlayback((value) =>
                  value === "playing" ? "paused" : "playing",
                )
              }
            >
              {playback === "playing" ? <Pause /> : <Play />}
            </Button>
            <Button
              size="icon-sm"
              variant="ghost"
              aria-label="Replay coverage accumulation"
              onClick={() => {
                setReplay((value) => value + 1);
                setStep(0);
                setPlayback("playing");
              }}
            >
              <RotateCcw />
            </Button>
          </div>
          <div className="coverage-scene__key">
            <span>
              <i />
              Current input
            </span>
            <span>
              <i />
              Previously reached
            </span>
            <span>
              <i />
              Unreached
            </span>
          </div>
        </div>
      </div>
      <figcaption>
        Illustration of coverage accumulation; topology and activation sequence
        are schematic.
      </figcaption>
    </figure>
  );
}
