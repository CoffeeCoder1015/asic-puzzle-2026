"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "motion/react";
import { gsap } from "gsap";
import { RotateCcw } from "lucide-react";
import { Button } from "./ui/button";
import { useAmbientMotion } from "./ambient-motion";
import "./clock-flow.css";

function RegisterBank({ next = false }: { next?: boolean }) {
  return (
    <svg
      className={`clock-bank${next ? " clock-bank--next" : ""}`}
      viewBox="0 0 180 100"
      aria-hidden="true"
    >
      {Array.from({ length: 8 }, (_, index) => (
        <g
          key={index}
          transform={`translate(${12 + (index % 4) * 42} ${10 + Math.floor(index / 4) * 44})`}
        >
          <rect className="clock-register" width="30" height="32" rx="3" />
          <path d="M0 19l5 4-5 4M10 11h10M15 7v8" />
        </g>
      ))}
    </svg>
  );
}

/** A schematic clock transition, never a simulated circuit trace. */
export function ClockFlow() {
  const root = useRef<HTMLElement>(null);
  const playedReplay = useRef(-1);
  const [replay, setReplay] = useState(0);
  const inView = useInView(root, { amount: 0.4 });
  const { running } = useAmbientMotion();

  useEffect(() => {
    if (!running || !inView || playedReplay.current === replay) return;
    playedReplay.current = replay;
    const context = gsap.context(() => {
      const timeline = gsap.timeline();
      timeline
        .fromTo(
          ".clock-bit",
          { x: -90, opacity: 0 },
          { x: 0, opacity: 1, duration: 0.65, ease: "power2.out" },
        )
        .fromTo(
          ".clock-gate",
          { y: 10, stroke: "#51655a" },
          { y: 0, stroke: "#c0f5d4", stagger: 0.13, duration: 0.4 },
          "-=0.1",
        )
        .fromTo(
          ".clock-travel",
          { strokeDashoffset: 1, opacity: 1 },
          { strokeDashoffset: -1, duration: 1.1, ease: "none" },
          "-=0.65",
        )
        .fromTo(
          ".clock-bank--next .clock-register",
          { fill: "#1c2922", y: -5 },
          {
            fill: "#6b9d80",
            y: 0,
            duration: 0.35,
            stagger: 0,
            ease: "power2.out",
          },
        )
        .to(".clock-bit, .clock-travel", { opacity: 0, duration: 0.3 });
    }, root);
    return () => context.revert();
  }, [inView, running, replay]);

  return (
    <figure
      ref={root}
      className="figure--wide clock-scene"
      data-asset-kind="programmatic"
    >
      <div className="clock-scene__field">
        <Button
          className="clock-replay"
          size="icon-sm"
          variant="ghost"
          aria-label="Replay clock transition"
          disabled={!running}
          onClick={() => setReplay((value) => value + 1)}
        >
          <RotateCcw />
        </Button>
        <div className="clock-stage">
          <span>At clock t</span>
          <RegisterBank />
          <strong>Previous state</strong>
          <code>+ input bit</code>
        </div>
        <div className="clock-stage clock-stage--gates">
          <span>Combinational logic</span>
          <svg className="clock-gates" viewBox="0 0 300 100" aria-hidden="true">
            <path
              className="clock-wire"
              d="M0 50H50M85 50H125M160 50H200M235 50H300"
            />
            <path className="clock-travel" pathLength="1" d="M0 50H300" />
            {[50, 125, 200].map((x, index) => (
              <g
                className="clock-gate"
                key={x}
                transform={`translate(${x} 28)`}
              >
                <path
                  d={
                    index === 1
                      ? "M0 0Q24 2 35 22Q24 42 0 44Q11 22 0 0Z"
                      : "M0 0H13C42 0 42 44 13 44H0Z"
                  }
                />
              </g>
            ))}
            <rect
              className="clock-bit"
              x="8"
              y="44"
              width="12"
              height="12"
              rx="3"
            />
          </svg>
          <strong>Evaluate the gates</strong>
          <small>In dependency order</small>
        </div>
        <div className="clock-stage">
          <span>At clock t + 1</span>
          <RegisterBank next />
          <strong>Next state</strong>
          <small>Output byte during readout</small>
        </div>
      </div>
      <figcaption>
        Input and readout clocks update the same bank of flip-flops.
      </figcaption>
    </figure>
  );
}
