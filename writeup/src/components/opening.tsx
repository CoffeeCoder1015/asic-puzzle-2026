"use client";

import { useEffect } from "react";
import { stagger, useAnimate, useReducedMotion } from "motion/react";
import "./opening.css";

/** The complete title is server rendered; motion adds a finite opening gesture. */
export function Opening() {
  const [scope, animate] = useAnimate<HTMLElement>();
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    if (reducedMotion !== false) return;
    const animation = animate(
      ".opening-line",
      { y: [22, 0], rotateX: [12, 0], opacity: [0.45, 1] },
      { duration: 1.1, delay: stagger(0.14), ease: [0.16, 1, 0.3, 1] },
    );
    return () => animation.stop();
  }, [animate, reducedMotion]);

  return (
    <header className="opening" ref={scope}>
      <p className="article-context opening-line">
        Jane Street ASIC puzzle · A reverse-engineering writeup
      </p>
      <h1 id="article-title">
        <span className="opening-line opening-title-main">
          How to reverse engineer an ASIC
        </span>{" "}
        <span className="opening-line opening-title-rest">
          without understanding the circuit
        </span>
      </h1>
      <p className="opening-deck opening-line">
        Recover the wiring. Make the circuit executable. Then search what it can
        say.
      </p>
    </header>
  );
}
