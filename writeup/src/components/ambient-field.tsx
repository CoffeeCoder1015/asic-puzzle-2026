"use client";

import { useAmbientMotion } from "@/components/ambient-motion";
import { Pause, Play } from "lucide-react";
import LetterGlitch from "@/components/react-bits/LetterGlitch";
import type { PaintRange } from "@/components/react-bits/LetterGlitch";
import { Button } from "@/components/ui/button";

const GLYPH_COLORS = ["#101112", "#101112", "#34473c", "#a4d9bd"];

function getPaintRanges(container: HTMLElement): readonly PaintRange[] {
  const edge = parseFloat(getComputedStyle(container).getPropertyValue("--glyph-edge")) / 100;
  return [{ start: 0, end: edge }, { start: 1 - edge, end: 1 }];
}

export function AmbientField() {
  const { running, motionAllowed, paused, togglePaused } = useAmbientMotion();

  return (
    <>
      <div className="ambient-field" data-running={running} aria-hidden="true">
        {running && (
          <LetterGlitch
            className="ambient-field__glyphs"
            characters="                    01⊕∧∨≠=+−×∑λ"
            glitchColors={GLYPH_COLORS}
            backgroundColor="#101112"
            glitchSpeed={420}
            getPaintRanges={getPaintRanges}
            centerVignette={false}
            outerVignette={false}
            smooth
          />
        )}
        <div className="ambient-field__rings">
          <i className="ambient-field__ring ambient-field__ring--left" />
          <i className="ambient-field__ring ambient-field__ring--right" />
        </div>
      </div>
      {motionAllowed && (
        <Button
          className="ambient-motion-toggle"
          variant="ghost"
          size="icon-sm"
          aria-label={paused ? "Resume ambient motion" : "Pause ambient motion"}
          title={paused ? "Resume ambient motion" : "Pause ambient motion"}
          onClick={togglePaused}
        >
          {paused ? <Play aria-hidden="true" /> : <Pause aria-hidden="true" />}
        </Button>
      )}
    </>
  );
}
