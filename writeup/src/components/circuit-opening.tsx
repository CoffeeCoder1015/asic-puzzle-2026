"use client";

import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";
import { useMotionValue } from "motion/react";
import { gsap } from "gsap";
import { Opening } from "./opening";
import { GdsViewer } from "./gds-viewer";
import { observeCircuit } from "./circuit-diagnostics";
import { observeAnimationProfile } from "./animation-profile-controls";
import { beginAnimationWork, endAnimationWork } from "./animation-profile";
import "./circuit-opening.css";

type EntryPhase = "pending" | "playing" | "complete";

/** One mounted viewer: scroll directs entry once, then the article owns its layout. */
export function CircuitOpening({ children }: { children: React.ReactNode }) {
  const root = useRef<HTMLElement>(null);
  const viewer = useRef<HTMLDivElement>(null);
  const progress = useMotionValue(0);
  const [phase, setPhase] = useState<EntryPhase>("pending");
  const [supported, setSupported] = useState(false);
  const [ready, setReady] = useState(false);
  const [failed, setFailed] = useState(false);
  const releaseTop = useRef<number | null>(null);
  const replaying = useRef(false);
  const trace = useRef<ReturnType<typeof observeCircuit>>(undefined);
  const profile = useRef<ReturnType<typeof observeAnimationProfile>>(undefined);
  const anchor = useRef<string | null>(null);
  const [navigation, setNavigation] = useState(0);
  const playing = phase === "playing";
  const onReady = useCallback(() => {
    setReady(true);
    setFailed(false);
  }, []);
  const release = useCallback(() => {
    releaseTop.current = viewer.current!.getBoundingClientRect().top;
    setPhase("complete");
  }, []);
  const onFailure = useCallback(() => {
    setFailed(true);
    release();
  }, [release]);

  useEffect(() => {
    trace.current = observeCircuit(root.current!);
    profile.current = observeAnimationProfile(root.current!);
    return () => { trace.current?.dispose(); profile.current?.dispose(); };
  }, []);

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const shortViewport = window.matchMedia("(max-height: 599px)");
    const updateSupport = () => {
      const allowed = !preference.matches && !shortViewport.matches;
      setSupported(allowed);
      if (!allowed) release();
    };
    const followAnchor = () => {
      if (!location.hash || location.hash === "#top") return;
      anchor.current = decodeURIComponent(location.hash.slice(1));
      setNavigation((value) => value + 1);
      release();
    };
    updateSupport();
    if (window.scrollY > 64) setPhase("complete");
    followAnchor();
    preference.addEventListener("change", updateSupport);
    shortViewport.addEventListener("change", updateSupport);
    window.addEventListener("hashchange", followAnchor);
    return () => {
      preference.removeEventListener("change", updateSupport);
      shortViewport.removeEventListener("change", updateSupport);
      window.removeEventListener("hashchange", followAnchor);
    };
  }, [release]);

  useLayoutEffect(() => {
    if (phase !== "pending" || !supported || !ready) return;
    setPhase(window.scrollY <= 64 ? "playing" : "complete");
  }, [phase, supported, ready]);

  useLayoutEffect(() => {
    if (!playing) return;
    const element = root.current!;
    const stage = element.querySelector<HTMLElement>(".circuit-opening__stage")!;
    const passages = Array.from(element.querySelectorAll<HTMLElement>("[data-entry-step]"));
    let frame = 0;
    let start = 0;
    let distance = 1;
    let measured = false;
    let origin = { position: 0, progress: 0 };
    let timeline: gsap.core.Timeline;
    const publish = () => {
      const workStart = beginAnimationWork();
      frame = 0;
      const position = Math.max(0, Math.min(1, (window.scrollY - start) / distance));
      const value = position === 0 || position === 1
        ? position
        : position >= origin.position
          ? origin.progress + (1 - origin.progress) * (position - origin.position) / (1 - origin.position)
          : origin.progress * position / origin.position;
      progress.set(value);
      timeline.progress(value);
      trace.current?.record(value);
      profile.current?.record(value);
      endAnimationWork("entry", workStart, 1);
      if (value === 1) release();
    };
    const schedule = () => {
      if (!frame) frame = requestAnimationFrame(publish);
    };
    const measure = () => {
      element.style.setProperty("--entry-page-width", `${document.documentElement.clientWidth}px`);
      start = element.getBoundingClientRect().top + window.scrollY;
      distance = element.offsetHeight - stage.offsetHeight;
      const position = (window.scrollY - start) / distance;
      origin = measured && position > 0 && position < 1
        ? { position, progress: progress.get() }
        : { position: 0, progress: 0 };
      measured = true;
      timeline.invalidate();
      timeline.render(progress.get() * timeline.duration(), true, true);
      publish();
    };
    const scheduleMeasure = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(measure);
    };
    const dockY = () => Math.max(0, stage.offsetHeight - viewer.current!.offsetHeight - 24);
    const context = gsap.context(() => {
      timeline = gsap.timeline({ paused: true });
      timeline.to({}, { duration: 1 }, 0);
      timeline.fromTo(".circuit-opening__title", { y: 0, autoAlpha: 1 },
        { y: -40, autoAlpha: 0, duration: 0.1 }, 0.06);
      timeline.fromTo(viewer.current,
        { x: 0, xPercent: -50, y: () => stage.offsetHeight * (window.innerWidth <= 600 ? 0.52 : window.innerWidth < 1100 ? 0.38 : 0.24) },
        {
          x: () => window.innerWidth < 1100 ? 0 : Math.min(220, Math.max(0, (window.innerWidth - 800) * 0.38)),
          y: () => stage.offsetHeight * (window.innerWidth <= 600 ? 0.48 : window.innerWidth < 1100 ? 0.38 : 0.10),
          duration: 0.16,
          ease: "power2.inOut",
        }, 0.10);
      timeline.fromTo(viewer.current, {
        x: () => window.innerWidth < 1100 ? 0 : Math.min(220, Math.max(0, (window.innerWidth - 800) * 0.38)),
        y: () => stage.offsetHeight * (window.innerWidth <= 600 ? 0.48 : window.innerWidth < 1100 ? 0.38 : 0.10),
      }, { x: 0, y: dockY, duration: 0.26, ease: "power2.inOut", immediateRender: false }, 0.74);
      passages.forEach((passage, index) => {
        const enter = 0.15 + index * 0.2;
        timeline.fromTo(passage, { y: 18, autoAlpha: 0 },
          { y: 0, autoAlpha: 1, duration: 0.06, ease: "power2.out" }, enter);
        if (index === passages.length - 1) {
          timeline.fromTo(passage, { y: 0 }, {
            y: () => dockY() - passage.offsetHeight - passage.offsetTop,
            duration: 1 - (enter + 0.06),
            ease: "power2.inOut",
            immediateRender: false,
          }, enter + 0.06);
        } else {
          timeline.to(passage, { y: -14, autoAlpha: 0, duration: 0.05, ease: "power1.in" }, enter + 0.15);
        }
      });
    }, root);
    if (replaying.current) {
      replaying.current = false;
      window.scrollTo({ top: element.getBoundingClientRect().top + window.scrollY, behavior: "instant" });
      const title = element.querySelector<HTMLElement>("h1")!;
      title.tabIndex = -1;
      title.focus({ preventScroll: true });
    }
    measure();
    const resizeObserver = new ResizeObserver(scheduleMeasure);
    resizeObserver.observe(stage);
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", scheduleMeasure);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", scheduleMeasure);
      resizeObserver.disconnect();
      context.revert();
    };
  }, [playing, progress, release]);

  useLayoutEffect(() => {
    if (playing) return;
    if (releaseTop.current !== null) {
      const delta = viewer.current!.getBoundingClientRect().top - releaseTop.current;
      releaseTop.current = null;
      window.scrollBy({ top: delta, behavior: "instant" });
    }
    if (anchor.current !== null) {
      const target = document.getElementById(anchor.current);
      anchor.current = null;
      target?.focus({ preventScroll: true });
      target?.scrollIntoView({ behavior: "instant" });
    }
    trace.current?.record(progress.get());
  }, [playing, phase, navigation, progress]);

  const replay = () => {
    progress.set(0);
    replaying.current = true;
    setPhase("playing");
  };

  return (
    <section ref={root} className="circuit-opening" data-enhanced={playing} data-interactive={!playing}>
      <div className="circuit-opening__stage">
        <div className="circuit-opening__title"><Opening /></div>
        <div className="circuit-opening__passages">{children}</div>
        <div ref={viewer} className="circuit-opening__viewer">
          <GdsViewer
            activate={supported && phase === "pending"}
            storyProgress={progress}
            interactive={!playing}
            preload={phase === "complete"}
            onSceneReady={onReady}
            onSceneFailure={onFailure}
            onReplay={supported && ready && !failed ? replay : undefined}
          />
        </div>
      </div>
    </section>
  );
}
