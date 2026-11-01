"use client";

import { createContext, useContext, useEffect, useState } from "react";

const AmbientMotionContext = createContext({
  running: false,
  motionAllowed: false,
  paused: false,
  togglePaused: () => {},
});

export function AmbientMotionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [motionAllowed, setMotionAllowed] = useState(false);
  const [paused, setPaused] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const updatePreference = () => setMotionAllowed(!preference.matches);
    const updateVisibility = () => setVisible(!document.hidden);
    updatePreference();
    updateVisibility();
    preference.addEventListener("change", updatePreference);
    document.addEventListener("visibilitychange", updateVisibility);
    return () => {
      preference.removeEventListener("change", updatePreference);
      document.removeEventListener("visibilitychange", updateVisibility);
    };
  }, []);

  return (
    <AmbientMotionContext.Provider
      value={{
        running: motionAllowed && !paused && visible,
        motionAllowed,
        paused,
        togglePaused: () => setPaused((value) => !value),
      }}
    >
      {children}
    </AmbientMotionContext.Provider>
  );
}

export function useAmbientMotion() {
  return useContext(AmbientMotionContext);
}
