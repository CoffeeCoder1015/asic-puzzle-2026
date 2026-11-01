# Physical layouts

`warmup-layout.json` and `puzzle-layout.json` are generated from the original
GDS files, not illustrative circuit artwork. Regenerate them from the repository
root. Request the puzzle's fallback SVG explicitly:

```powershell
uv run python writeup/scripts/export_writeup_gds.py
uv run python writeup/scripts/export_writeup_gds.py --source puzzle/puzzle.gds --output writeup/public/data/puzzle-layout.json --projection writeup/public/figures/puzzle-layout.svg
```

The exporter records the GDS SHA-256, original cell boundaries, holes, reference
transforms and flattened placements. XY values and translations are integer GDS
database units; multiply by `source.dbuMicrons` for micrometres. Reference rotation
is in degrees: mirror local Y first when `mirror` is true, then rotate, then
translate. `placements` includes the top cell at the identity transform and all
descendant cell placements. Local polygons remain shared.

The physical layer stack and Z heights come from the SKY130 stack in
[Tiny Tapeout GDS Viewer](https://github.com/TinyTapeout/tinytapeout_gds_viewer/blob/2969b5e7b4004cc35875738ee53fa3043fd6b415/src/pdk_layers.js),
under Apache-2.0, reproduced in `LICENSE-tinytapeout-gds-viewer.txt`. The selected
16 layers are those physical layers present in this GDS. Pin labels, text and
nonphysical marker datatypes are omitted. This conversion uses KLayout and its
polygon representation; it does not distribute the upstream viewer's WASM engine.
The upstream repository is a GitHub fork of
`mbalestrini/tinytapeout_gds_viewer` maintained under the TinyTapeout organization.

Every generation independently reconstructs both the serialized reference
hierarchy and the renderer's flattened `placements` using the local cell polygons.
KLayout compares each reconstruction's physical layers against the source: polygon
count, area and geometric XOR. A nonempty XOR (any geometric difference) fails the
export. Both results appear in `statistics.verification`. This establishes
the exported XY mask geometry; Three.js rendering and visual layer separation
are checked separately in the website.

`../figures/puzzle-layout.svg` is the puzzle fallback, showing a top view of the
same polygons and placements in mint and charcoal. It shows only li1, met1, met2
and met3, with that subset disclosed in its SVG description. Colors and displayed
separation are presentation choices; XY mask coordinates are preserved.
