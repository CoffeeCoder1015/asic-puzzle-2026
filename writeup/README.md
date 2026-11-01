# ASIC puzzle writeup

The website, its assets, and its authoring tools live in this Next.js project. Runtime images and layout data are in `public/figures/` and `public/data/`.

From this directory, run:

```sh
npm ci
npm run dev
```

Open [the local writeup](http://127.0.0.1:3001). Next.js reloads changed components during development.

Run `npm run typecheck` to check TypeScript. Run `npm run build` to export the production site to `out/`, then `npm start` to serve the export at the same local address. Stop the development server before starting the static preview on the same port.

The published writeup is at [coffeecoder1015.github.io/asic-puzzle-2026](https://coffeecoder1015.github.io/asic-puzzle-2026/). The [Pages workflow](../.github/workflows/pages.yml) builds and deploys pushes to `master` once the repository's Pages source is set to GitHub Actions. It sets `NEXT_PUBLIC_BASE_PATH=/asic-puzzle-2026` and disables diagnostics. Local builds default to the domain root. The base path is fixed at build time; rebuilding is required to change it. Public image and layout URLs use `src/lib/public-asset.ts` to apply the same prefix as Next.js.

| Change | File |
| --- | --- |
| Article wording, section order, and static figures | `src/components/article.tsx` |
| Warm-up registers and recorded Z3 interactions | `src/components/interactive-explanations.tsx` |
| Five exact input streams and fifteen warm-up pairs | `src/lib/circuit-data.ts` |
| Drawing a board from its input stream | `src/components/board.tsx` |
| Evidence disclosures | `src/components/disclosure.tsx` |
| Type, spacing, palette, and figure layout | `src/app/article.css` |
| Register controls | `src/app/interactions.css` |
| shadcn theme and shared disclosure styles | `src/app/globals.css` |
| Scientific plot PNGs | `public/figures/` |

The controls use the shadcn/ui Button, Input, and Accordion components. Query transitions use React Bits AnimatedContent. Their source is included under `src/components/`. [Third-party notices](THIRD_PARTY_NOTICES.md) record the upstream sources.

The Z3 examples replay recorded outcomes. The browser does not run a solver. The warm-up interaction evaluates the recovered unsigned 8-bit rule directly.

The coverage comparison can be reproduced from the repository root with `uv run python writeup/scripts/compare_activation_coverage.py`. It uses the Python circuit evaluator and the five recorded input streams; it does not train a model.

The opening uses a [one-way scroll entry](docs/patterns/circuit-scroll.md).
Its existing introduction appears in four passages while one persistent circuit
viewer makes two turns. Completion restores ordinary article flow beside the viewer.
The repository file list follows the viewer discussion. Scrolling upward reads the article normally;
Replay entry explicitly returns to the title and restarts the same viewer.
Reduced motion, deep links, short viewports and rendering failures keep normal
article flow available.

## Diagnostic builds

Diagnostics are enabled by default in development and disabled by default in production builds. `NEXT_PUBLIC_WRITEUP_DEBUG=1` enables them explicitly; `0` disables them, including in development. This flag is fixed at build time. Setting it when starting an existing production build does not change that build.

For a diagnostic production build in PowerShell:

```powershell
$env:NEXT_PUBLIC_WRITEUP_DEBUG = "1"
npm run build
Remove-Item Env:NEXT_PUBLIC_WRITEUP_DEBUG
npm start
```

In a debug-enabled build, use `?fps` for the live renderer counter, `?animationProfile` for six-second capture controls, `?sceneDebug=1` for canvas/scroll diagnostics, or `?gdsProfile` for layout timing marks and console records. Query parameters alone cannot enable these tools in a normal production build.

Capture controls require a visible tab. Finish the entry before using article or postscript sweeps. Save reports locally, then run `node scripts/summarize_animation_profile.mjs capture.json` or `node scripts/summarize_gds_profile.mjs capture.json` from this directory. Keep temporary captures and review reports in the repository's ignored `output/` folder.

While the site is running, inspect its image hashes, exact input streams, and headings from the repository root:

```sh
node writeup/scripts/inspect_writeup.cjs http://127.0.0.1:3001
```
