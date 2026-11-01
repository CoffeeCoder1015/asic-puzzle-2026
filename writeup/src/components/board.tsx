"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import {
  motion,
  useInView,
  useMotionValue,
  useReducedMotion,
  useSpring,
} from "motion/react";
import { useAmbientMotion } from "./ambient-motion";
import "./board-motion.css";
import type { CircuitMessage } from "../lib/circuit-data";

type BoardProps = {
  message: CircuitMessage;
  className?: string;
};

/** Plot the recorded serial stream row by row, without reversing its bit order. */
export function Board({ message, className }: BoardProps) {
  const scope = useRef<SVGSVGElement>(null);
  const inView = useInView(scope, { amount: 0.6 });
  const [started, setStarted] = useState(false);
  const { running } = useAmbientMotion();
  const playing = running && inView;
  const reducedMotion = useReducedMotion();
  const tiltX = useMotionValue(0);
  const tiltY = useMotionValue(0);
  const rotateX = useSpring(tiltX, { stiffness: 180, damping: 24 });
  const rotateY = useSpring(tiltY, { stiffness: 180, damping: 24 });

  useEffect(() => {
    if (playing) setStarted(true);
  }, [playing]);

  useEffect(() => {
    if (!running) {
      tiltX.set(0);
      tiltY.set(0);
    }
  }, [running, tiltX, tiltY]);

  const filledPositions = Array.from(message.bits).flatMap((bit, index) =>
    bit === "1" ? [index] : [],
  );

  return (
    <motion.svg
      ref={scope}
      style={
        !running || reducedMotion
          ? undefined
          : { rotateX, rotateY, transformPerspective: 700 }
      }
      onPointerMove={(event) => {
        if (!running || reducedMotion || event.pointerType !== "mouse") return;
        const bounds = event.currentTarget.getBoundingClientRect();
        tiltX.set(((event.clientY - bounds.top) / bounds.height - 0.5) * -7);
        tiltY.set(((event.clientX - bounds.left) / bounds.width - 0.5) * 7);
      }}
      onPointerLeave={() => {
        tiltX.set(0);
        tiltY.set(0);
      }}
      className={["result-board", className].filter(Boolean).join(" ")}
      data-reveal={started ? (message.success ? "stars" : "marks") : undefined}
      data-motion-running={playing}
      viewBox="0 0 220 220"
      role="img"
      aria-label={message.label}
    >
      <rect width="220" height="220" fill="var(--board-paper)" />
      {Array.from({ length: 12 }, (_, index) => {
        const position = index * 20;
        return (
          <path
            key={index}
            d={`M${position} 0V220M0 ${position}H220`}
            className="board-rule"
          />
        );
      })}
      {filledPositions.map((index, order) => (
        <rect
          key={index}
          x={(index % 11) * 20 + 4}
          y={Math.floor(index / 11) * 20 + 4}
          width="12"
          height="12"
          rx="2"
          className="board-mark"
          style={{ "--board-mark-delay": `${order * 0.004}s` } as CSSProperties}
        />
      ))}
      {message.success && (
        <g aria-hidden="true" className="board-stars">
          {filledPositions.map((index, order) => (
            <path
              key={index}
              className="board-star"
              style={{
                transformOrigin: `${(index % 11) * 20 + 10}px ${Math.floor(index / 11) * 20 + 10}px`,
                animationDelay: `${order * 0.045}s`,
              }}
              d={`M${(index % 11) * 20 + 10} ${Math.floor(index / 11) * 20 + 1}l2.5 6.5 6.5 2.5-6.5 2.5-2.5 6.5-2.5-6.5-6.5-2.5 6.5-2.5Z`}
            />
          ))}
        </g>
      )}
    </motion.svg>
  );
}
