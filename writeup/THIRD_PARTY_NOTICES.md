# Third-party components

`src/components/ui/button.tsx`, `input.tsx`, and `accordion.tsx` come from the official shadcn/ui new-york-v4 registry. The utility import points to this project's `src/lib/utils.ts`. The license is in `licenses/shadcn-ui.txt`.

- [Button source](https://ui.shadcn.com/r/styles/new-york-v4/button.json)
- [Input source](https://ui.shadcn.com/r/styles/new-york-v4/input.json)
- [Accordion source](https://ui.shadcn.com/r/styles/new-york-v4/accordion.json)

`src/components/react-bits/AnimatedContent.tsx` comes from the official [React Bits TypeScript and CSS registry](https://reactbits.dev/r/AnimatedContent-TS-CSS.json). Its license is in `licenses/react-bits.txt`.

`src/components/react-bits/LetterGlitch.tsx` uses the official [React Bits Canvas 2D implementation at commit 1eeb6f1](https://github.com/DavidHDev/react-bits/blob/1eeb6f105c68b964289d85dabbe84a1d551f3797/src/ts-tailwind/Backgrounds/LetterGlitch/LetterGlitch.tsx). The local copy caps pixel ratio at one and clears a pending resize timeout on disposal. `AmbientField` configures its sparse glyphs and adds page masking, motion control, visibility suspension, and CSS ripple rings. The same React Bits license applies.

React Bits uses GSAP and ScrollTrigger. The installed GSAP package includes its license notice. See [GSAP's license](https://gsap.com/standard-license).
`src/components/opening.tsx` and `board.tsx` use the official [Motion for React](https://motion.dev/docs/react) library for finite entry gestures and pointer-driven spring feedback. Its MIT license is in `licenses/motion.txt`.

`src/components/gds-scene.tsx` uses official [Three.js](https://threejs.org/), [React Three Fiber](https://r3f.docs.pmnd.rs/), and [Drei OrbitControls](https://drei.docs.pmnd.rs/controls/introduction). A worker extrudes the puzzle and warm-up GDS polygons and bakes cell placements into physical layers. Geometry comes from `../puzzle/puzzle.gds` and `../warmup/04_final.gds`, converted by `scripts/export_writeup_gds.py`; no browser GDS parser or upstream WASM engine is bundled. Colors and exploded layer spacing are presentation choices. Their MIT licenses are in `licenses/three.txt`, `licenses/react-three-fiber.txt`, and `licenses/react-three-drei.txt`.

The SKY130 physical layer stack is adapted from [TinyTapeout GDS Viewer](https://github.com/TinyTapeout/tinytapeout_gds_viewer/blob/2969b5e7b4004cc35875738ee53fa3043fd6b415/src/pdk_layers.js) under Apache-2.0. Its license and geometry provenance are in `public/data/`.
The single circuit opening uses GSAP ScrollTrigger to coordinate text and the camera/layer poses through one Motion value. CSS sticky holds the viewport; the same scene becomes manually controlled at the end of the sequence.

The opening choreography performs one full scroll-driven revolution, followed by a settled scroll interval and manual orbit controls. A local projection fitter keeps the physical-layout bounds within the authored view; explicit reader zoom remains under reader control.
