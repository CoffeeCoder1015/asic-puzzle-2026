# Design and review guide

The writeup explains a circuit reconstruction and the output search that solved it. Keep the reasoning in one reading path. Give the reader useful things to manipulate beside the explanation.

Use the charcoal page, silver text, and mint connections consistently. Salmon marks an impossible query or a failed condition. Preserve the original palettes and labels of measured plots. Do not make a schematic look like a captured circuit or solver trace.

Keep prose at a readable measure. Use wider figures when the relationships need room. Section headings belong to the article. Do not add separate promotional introductions before them.

Use the shared Board component for every recorded witness. Keep exact streams and warm-up pairs in `circuit-data.ts`. Use shadcn controls for input, buttons, and disclosures. Use React Bits for finite transitions when a query changes. Keep essential content visible with reduced motion.

Button roles share one reset and the page tokens. Use mint fill for the next primary step, a quiet charcoal outline for secondary actions, and transparent ghost buttons for viewer tools and animation controls. Pressed circuit selectors use mint fill; register bits keep their meaningful bit-state treatment. Disclosures remain full-width text rows. Keep keyboard focus visible across every role. Do not rely on native browser button borders or backgrounds.

The GDS viewer keeps one renderer and starts with the puzzle. Load the warm-up during idle time after the introduction, retain both prepared models while the viewer is mounted, and show only the selected model. Static images serve the unactivated or failed viewer, not transitions between models. Keep replay centered between the view tools and layer-spacing control on desktop; move it to the right of the tools on small screens.

Before accepting a revision, review all of these together:

- Research and references. Check that the composition and interaction suit a technical explanation.
- Narrative. Follow physical layout, executable circuit, failed simplification, output search, and the result. Preserve the modeled sequence and experiment limitations.
- Composition. Check hierarchy, alignment, type, spacing, color, figures, and motion across the complete article.
- Communication. Remove captions and labels that repeat the body, describe an obvious visual, or read like visible alt text. Keep operational control names and material qualifications.
- Interaction. Exercise success, failure, invalid input, boundaries, replay, keyboard focus, and disclosures.
- Fidelity. Preserve the measured plots and compare rendered streams, board positions, fifteen pairs, and recorded outcomes with `src/lib/circuit-data.ts`.
- Responsive layout. Inspect a wide and narrow browser view. Check overflow, clipped controls, touch targets, and figure text.

References used in this design:

- [x.ai](https://x.ai/) informs the dark neutral field and typographic scale.
- [shadcn/ui](https://ui.shadcn.com/) supplies the actual controls and disclosures.
- [React Bits AnimatedContent](https://reactbits.dev/animations/animated-content) supplies the actual query transitions.
- [Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html) informs direct manipulation and step-by-step exploration.
- [Bartosz Ciechanowski](https://ciechanow.ski/mechanical-watch/) informs the relationship between a passage, its controls, and its changing illustration.
- [Leon Lin's article](https://x.com/LexnLin/status/2116662591363690999) informs reference-led iteration and independent rendered critique.

Motion and Anime.js were also evaluated. This implementation uses the GSAP dependency supplied by AnimatedContent.
