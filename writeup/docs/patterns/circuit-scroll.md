# One-way circuit entry

CircuitOpening owns a pending / playing / complete lifecycle. Complete is terminal
for ordinary scrolling. Only an explicit Replay entry action starts a new run.
The same DOM paragraphs and GdsViewer remain mounted in every phase. The current
circuitPose stays unchanged. Progress drives both the text timeline and circuit.

## First paint and scene readiness

A small inline script in the root layout marks `html[data-entry-pending]` before
the article is parsed, only for a motion-enabled viewport at least 600px high,
at the top without a destination hash. CSS gives that candidate's pending phase
the same sticky composition as playing. Without this script, the natural article
remains visible. React owns `data-phase`; the marker never changes React state.

Hydration admits the text timeline as soon as eligibility is known, without
waiting for geometry or a GPU frame. The same viewer activates during pending or
playing. It starts noninteractive and renders the current story progress, so a
late first frame cannot reset the camera or restart a completed introduction.
Only a ready canvas fades into the reserved space; the differently framed fallback
image stays reserved for ordinary article/failure presentation. The opening does
not promise zero network or GPU startup time.

The natural DOM is Opening, intro text through TinyTapeout, then GdsViewer.
Playing temporarily positions text passages and the constant-size viewer in a
sticky stage. Four passages introduce the puzzle, the author's Verilog background,
the warm-up, and TinyTapeout. The repository paragraph and tree follow the viewer
discussion in the ordinary article. Intro text fades upward between
passages. No duplicate text, labels
or second canvas is needed. The intro becomes ordinary article content on release.

Completion captures viewer.getBoundingClientRect().top before switching layout.
The next layout effect measures the new top and calls window.scrollBy with
behavior instant and delta = newTop - oldTop. For example a viewer at screen Y280
moves to Y910 after release. Scrolling down630 restores screen Y280 before paint.
Canvas width/height must match in both layouts or this preserves only position.
Both layouts share the same responsive viewer width and stage-height variables.
Viewer controls, including the replay slot, retain their dimensions while playing;
visibility hides them without removing their space.
Set overflow-anchor:none on the temporary/normal section to prevent a second
browser correction. Cleanup the paused GSAP timeline before measuring normal flow.
Do not reset the persistent progress MotionValue to0 in this cleanup.

Replay resets progress0, switches to playing, and scrolls to the section's start
in the resulting layout before paint. It deliberately returns the reader to the
opening instead of preserving the final viewer position. Move keyboard focus to
the title with preventScroll so focus does not remain on hidden viewer controls.
Keep the same Canvas and clear manual damping via interactive=false.

A stable storyProgress prop remains present through completion. SceneView's
interactive transition applies exact circuitPose(1), so no penultimate pose can
leak into the manual view. Same viewer loading must be activated for eligible
entry at the top even though its natural article slot starts below the fold.

Hash navigation releases layout then focuses/scrolls its requested target.
Reduced motion, a too-short viewport or rendering failure restores normal article
content and controls rather than trapping readers in entry. Replay is unavailable
while motion is disabled or rendering cannot support it.

A fixed viewer over a normal-flow placeholder also works, but requires slot and
viewport geometry plus the same release calculation. A second canvas/portal adds
lifetime coordination without eliminating this calculation. Sticky styling of
the natural DOM keeps content order and lifetime directly visible in the source.

## Worked lifecycle and the fixed alternative

The sticky implementation's initial admission, release and replay are these
operations (the component's layout effects supply the before-paint ordering):

```js
// Parser-time marker reserves sticky CSS before hydration on eligible entry.
// No marker means natural article flow. Hydration owns the phase afterward.
supported = !reducedMotion && viewportHeight >= 600;
activate = supported && phase !== "complete";
if (phase === "pending" && supported) {
  if (scrollY <= 64 && !deepHash) phase = "playing";
  else release();
}

// Release: clean up the sticky timeline before measuring the natural layout.
releaseTop = viewer.getBoundingClientRect().top;
phase = "complete";
// Next layout effect, after timeline.revert():
scrollBy({ top: viewer.getBoundingClientRect().top - releaseTop, behavior: "instant" });

// Replay: one existing viewer, no key or portal-target change.
progress.set(0);
phase = "playing";
// Next layout effect, after establishing sticky geometry:
scrollTo({ top: root.getBoundingClientRect().top + scrollY, behavior: "instant" });
title.focus({ preventScroll: true });
```

The last passage remains visible through progress1. Its explicit translation
endpoint is `dockY - passage.offsetHeight - passage.offsetTop`, putting its bottom
immediately above the viewer. Passage wrappers use `display:flow-root` in both
layouts, so their child margins contribute to the same measured height. Release
therefore preserves the last paragraph's position along with the viewer.

Resize records an anchor at the current normalized scroll position and scene
progress. Subsequent samples interpolate from that point to either endpoint:

```js
origin = { position: normalizedScrollY, progress: progress.get() };
function sample(position) {
  if (position <= 0) return 0;
  if (position >= 1) return 1;
  return position >= origin.position
    ? origin.progress + (1 - origin.progress) * (position - origin.position) / (1 - origin.position)
    : origin.progress * position / origin.position;
}
```

Initial measurement uses origin `(0,0)`. An in-range resize replaces the anchor;
resize outside the range selects the corresponding endpoint. A forced timeline
render applies new geometric endpoints even when progress is unchanged. For
example progress0.5 at scrollY880 remains0.5 when height800 becomes700, rather
than recomputing0.571 from the new section distance. Further scrolling still
reaches1 at the new section end.
Native resize and the stage's ResizeObserver queue one shared measurement frame.
This waits for viewport units to settle and remeasures an actual stage-size
change, rather than retaining coordinates from the previous viewport.

A fixed host could preserve one DOM/canvas lifetime without a portal, but requires
additional slot measurements. Its concrete lifecycle would be:

```js
// Initial admission after readiness, with an ordinary-flow slot retained.
slotHeight = viewer.offsetHeight;
slot.style.height = `${slotHeight}px`;
const initial = slot.getBoundingClientRect();
viewer.style.position = "fixed";
viewer.style.left = `${initial.left}px`;
viewer.style.width = `${initial.width}px`;
viewer.style.top = "0px";
viewer.style.transform = `translateY(${openingY}px)`;
phase = "playing";

// Each scroll/resize must also recompute fixed X/width and destination slot Y.
const destination = slot.getBoundingClientRect();
viewer.style.transform = `translateY(${interpolate(openingY, destination.top, progress)}px)`;

// Release still restores normal content height and compensates the viewport.
const before = viewer.getBoundingClientRect().top;
phase = "complete";
viewer.removeAttribute("style");
slot.style.height = "";
restoreNormalIntro();
scrollBy({ top: viewer.getBoundingClientRect().top - before, behavior: "instant" });

// Replay must establish the slot and fixed coordinates again after returning.
progress.set(0);
establishEntryHeight();
scrollTo({ top: root.offsetTop, behavior: "instant" });
measureSlotAndFixExistingViewer();
phase = "playing";
title.focus({ preventScroll: true });
```

The fixed version still needs the chosen implementation's matched dimensions,
release compensation, terminal completion and explicit replay. Its extra slot and
viewport coordinate maintenance does not remove a requirement here, so the
sticky version keeps the mechanism shorter.
