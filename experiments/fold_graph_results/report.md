# Directed netlist folding experiment

This is a structural experiment, not a recovered RTL claim. Pin direction comes from `sky130/pin_definitions.json`; flip-flop clock/reset/set arcs are excluded only from functional clustering.

## Graph sizes

- **cells:** 738
- **flip flops:** 92
- **combinational cells:** 646
- **primary inputs:** 4
- **primary outputs:** 9
- **pin graph nodes:** 1468
- **pin graph edges:** 2769
- **collapsed graph nodes:** 751
- **collapsed graph edges:** 2052
- **register dependency nodes:** 103
- **register dependency edges:** 1073
- **functional connected components:** 2
- **register communities:** 12
- **functional communities:** 12
- **undriven loaded nets:** 0
- **multi driver nets:** 0

## Primary-output cones

### O[0]

- 50 combinational cells, 66 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478, cell:cell_5`
- Most common logic families: `[('a21oi', 5), ('nor3b', 4), ('nor2', 4), ('and2b', 4), ('inv', 4), ('and3', 3), ('nor3', 2), ('nand2', 2)]`

### O[1]

- 52 combinational cells, 68 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_195, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478`
- Most common logic families: `[('nor2', 7), ('inv', 5), ('nor3', 3), ('nor3b', 3), ('and2b', 3), ('or3', 3), ('and3', 3), ('nor4b', 2)]`

### O[2]

- 48 combinational cells, 64 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478, cell:cell_7`
- Most common logic families: `[('inv', 6), ('nand2', 4), ('nor3', 3), ('nor3b', 3), ('nor2', 3), ('and2b', 3), ('and3', 3), ('or2', 2)]`

### O[3]

- 58 combinational cells, 74 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_162, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478`
- Most common logic families: `[('nor2', 7), ('and2b', 5), ('nor3b', 3), ('nand2', 3), ('nand2b', 3), ('a21oi', 3), ('and3', 3), ('inv', 3)]`

### O[4]

- 46 combinational cells, 62 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_138, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478`
- Most common logic families: `[('nor3b', 3), ('nor2', 3), ('nand2b', 3), ('and2b', 3), ('inv', 3), ('and2', 3), ('nor3', 2), ('nand2', 2)]`

### O[5]

- 43 combinational cells, 59 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478, cell:cell_6`
- Most common logic families: `[('nor2', 4), ('and3', 4), ('inv', 4), ('nor3b', 3), ('a22o', 3), ('and2b', 3), ('nor3', 2), ('nand2', 2)]`

### O[6]

- 43 combinational cells, 59 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_148, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_4, cell:cell_478`
- Most common logic families: `[('nor2', 4), ('nor3b', 3), ('nand2', 3), ('a22o', 3), ('or3', 3), ('a21oi', 3), ('nor3', 2), ('nor4b', 2)]`

### O[7]

- 35 combinational cells, 51 nets, backward depth upper bound 7
- Direct sequential/input boundaries: `cell:cell_118, cell:cell_122, cell:cell_144, cell:cell_146, cell:cell_156, cell:cell_165, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_334, cell:cell_343, cell:cell_4, cell:cell_478`
- Most common logic families: `[('conb', 4), ('nor3b', 3), ('inv', 3), ('nor3', 2), ('nor2', 2), ('a22o', 2), ('or3', 2), ('and3', 2)]`

### success

- 0 combinational cells, 1 nets, backward depth upper bound 0
- Direct sequential/input boundaries: `cell:cell_144`
- Most common logic families: `[]`

## Folded functional blocks

### Registered success checker

- `success` is the Q output of `cell:cell_144`. Its D cone has 47 cells and direct support from 57 FFs.
- Logic-family signature: `[('and2b', 14), ('inv', 10), ('and2', 9), ('and4', 5), ('and3', 4), ('and4b', 1), ('nand2b', 1), ('a32o', 1), ('or3', 1), ('nor3', 1)]`
- The checker includes self-feedback: `True`.

### Eight-bit output generator

- The union of O[7:0] contains 166 combinational cells fed directly by 23 FFs.
- All bits share 15 source FFs and 20 combinational cells.
- Per-bit exclusive source FF: `{'O[0]': ['cell:cell_5'], 'O[1]': ['cell:cell_195'], 'O[2]': ['cell:cell_7'], 'O[3]': ['cell:cell_162'], 'O[4]': ['cell:cell_138'], 'O[5]': ['cell:cell_6'], 'O[6]': ['cell:cell_148'], 'O[7]': ['cell:cell_343']}`
- SCC sizes inside its 23-FF support: `[8, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]`
- Nontrivial source SCCs: `[['cell:cell_138', 'cell:cell_148', 'cell:cell_162', 'cell:cell_195', 'cell:cell_343', 'cell:cell_5', 'cell:cell_6', 'cell:cell_7'], ['cell:cell_2', 'cell:cell_3', 'cell:cell_4', 'cell:cell_478']]`

### Mux/hold shift bank

- 12 bits, ordered source-to-sink: `cell:cell_130 -> cell:cell_141 -> cell:cell_189 -> cell:cell_167 -> cell:cell_140 -> cell:cell_166 -> cell:cell_127 -> cell:cell_159 -> cell:cell_123 -> cell:cell_188 -> cell:cell_182 -> cell:cell_171`; common boundaries `['cell:cell_125', 'port:enable']`; serial input `['port:I']`

## Register-dependency communities

- C0: 30 FFs; shapes {'wide-state-dependent': 26, 'mixed': 4}; directly feeds outputs []; members `cell:cell_120, cell:cell_121, cell:cell_124, cell:cell_128, cell:cell_131, cell:cell_134, cell:cell_135, cell:cell_137, cell:cell_142, cell:cell_143, cell:cell_150, cell:cell_153, cell:cell_154, cell:cell_157, cell:cell_158, cell:cell_160, cell:cell_161, cell:cell_163, cell:cell_164, cell:cell_170, cell:cell_173, cell:cell_174, cell:cell_178, cell:cell_180, cell:cell_184, cell:cell_193, cell:cell_194, cell:cell_201, cell:cell_202, cell:cell_203`
- C1: 18 FFs; shapes {'state/counter-like': 2, 'mixed': 12, 'wide-state-dependent': 4}; directly feeds outputs ['O[0]', 'O[1]', 'O[2]', 'O[3]', 'O[4]', 'O[5]', 'O[6]', 'O[7]', 'success']; members `cell:cell_118, cell:cell_122, cell:cell_129, cell:cell_132, cell:cell_144, cell:cell_146, cell:cell_147, cell:cell_152, cell:cell_155, cell:cell_156, cell:cell_165, cell:cell_168, cell:cell_179, cell:cell_181, cell:cell_183, cell:cell_187, cell:cell_192, cell:cell_334`
- C2: 14 FFs; shapes {'state/counter-like': 11, 'wide-state-dependent': 2, 'shift-like': 1}; directly feeds outputs []; members `cell:cell_123, cell:cell_125, cell:cell_127, cell:cell_130, cell:cell_140, cell:cell_141, cell:cell_145, cell:cell_159, cell:cell_166, cell:cell_167, cell:cell_171, cell:cell_182, cell:cell_188, cell:cell_189`
- C3: 13 FFs; shapes {'wide-state-dependent': 8, 'mixed': 4, 'shift-like': 1}; directly feeds outputs ['O[0]', 'O[1]', 'O[2]', 'O[3]', 'O[4]', 'O[5]', 'O[6]', 'O[7]']; members `cell:cell_138, cell:cell_148, cell:cell_162, cell:cell_195, cell:cell_2, cell:cell_200, cell:cell_3, cell:cell_343, cell:cell_4, cell:cell_478, cell:cell_5, cell:cell_6, cell:cell_7`
- C4: 3 FFs; shapes {'wide-state-dependent': 1, 'mixed': 2}; directly feeds outputs []; members `cell:cell_172, cell:cell_176, cell:cell_177`
- C5: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_133, cell:cell_191`
- C6: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_126, cell:cell_136`
- C7: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_149, cell:cell_196`
- C8: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_169, cell:cell_197`
- C9: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_186, cell:cell_198`
- C10: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_139, cell:cell_190`
- C11: 2 FFs; shapes {'mixed': 2}; directly feeds outputs []; members `cell:cell_151, cell:cell_199`

## Full functional-graph communities

- F0: 118 nodes, 22 FFs, ports ['I']; dominant families [('dfrtp', 22), ('o21a', 11), ('a31o', 8), ('and2b', 7), ('nand2b', 7), ('nand4', 7)]
- F1: 111 nodes, 4 FFs, ports []; dominant families [('nor2', 9), ('nand2', 8), ('and2b', 8), ('xnor2', 7), ('a21oi', 6), ('nand2b', 6)]
- F2: 102 nodes, 0 FFs, ports []; dominant families [('nor2', 16), ('nand2', 11), ('or2', 7), ('xor2', 6), ('xnor2', 6), ('or3', 6)]
- F3: 85 nodes, 5 FFs, ports ['O[0]', 'O[1]', 'O[2]', 'O[3]', 'O[4]', 'O[5]', 'O[6]', 'O[7]', 'success']; dominant families [('a22o', 16), ('and3', 9), ('o31a', 8), ('or3', 8), ('conb', 5), ('dfrtp', 5)]
- F4: 72 nodes, 17 FFs, ports ['enable']; dominant families [('dfrtp', 13), ('mux2', 10), ('xnor2', 9), ('xor2', 6), ('a221o', 4), ('dfstp', 4)]
- F5: 67 nodes, 15 FFs, ports []; dominant families [('dfrtp', 15), ('and4bb', 6), ('or4b', 4), ('o21a', 4), ('and2b', 3), ('nand4', 3)]
- F6: 53 nodes, 4 FFs, ports []; dominant families [('nor2', 7), ('nand2', 7), ('a21oi', 5), ('dfrtp', 4), ('xnor2', 4), ('a21o', 4)]
- F7: 36 nodes, 8 FFs, ports []; dominant families [('dfrtp', 8), ('and3', 3), ('and2b', 3), ('diode', 3), ('nand2', 2), ('o21a', 2)]
- F8: 33 nodes, 0 FFs, ports ['clk']; dominant families [('clkbuf', 32)]
- F9: 33 nodes, 8 FFs, ports []; dominant families [('dfrtp', 8), ('o21a', 4), ('a31o', 2), ('a21o', 2), ('inv', 2), ('nor2', 2)]
- F10: 25 nodes, 6 FFs, ports []; dominant families [('dfrtp', 6), ('o21a', 3), ('nand4', 2), ('and3', 2), ('and2b', 2), ('a31o', 2)]
- F11: 15 nodes, 3 FFs, ports []; dominant families [('inv', 4), ('dfrtp', 3), ('mux2', 2), ('a21oi', 1), ('or2', 1), ('o211a', 1)]

## Structural interpretation

- The success pin is the Q output of cell:cell_144; its next-state/predicate cone is 47 cells with 57 direct FF inputs and an AND-heavy signature [('and2b', 14), ('inv', 10), ('and2', 9), ('and4', 5), ('and3', 4), ('and4b', 1)].
- The eight O cones together contain 166 unique combinational cells driven by 23 FFs. Every bit shares 15 FF inputs and 20 logic cells, then has a bit-specific branch.
- The success predicate and O generator share 2 combinational cells and 10 direct FF sources.
- A 12-bit mux/hold chain was recovered from I through cell:cell_130 -> cell:cell_141 -> cell:cell_189 -> cell:cell_167 -> cell:cell_140 -> cell:cell_166 -> cell:cell_127 -> cell:cell_159 -> cell:cell_123 -> cell:cell_188 -> cell:cell_182 -> cell:cell_171; every stage shares control boundaries ['cell:cell_125', 'port:enable'].
- The largest mutually coupled state island has 9 FFs ['cell:cell_121', 'cell:cell_125', 'cell:cell_128', 'cell:cell_150', 'cell:cell_157', 'cell:cell_170', 'cell:cell_184', 'cell:cell_193', 'cell:cell_202']; its 3-to-8-cell next-state cones, XOR/XNOR use, enable dependence, and connection through cell:cell_125 to the shift bank make it the strongest controller/counter candidate, but topology alone cannot distinguish those roles.
- Register shapes by the deliberately simple dependency heuristic: {'state/counter-like': 13, 'wide-state-dependent': 41, 'mixed': 36, 'shift-like': 2}.
- The register-only dependency graph has 801 directed edges and SCC sizes [9, 8, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2]; large SCCs indicate mutually coupled state banks, while chains of singleton SCCs are compatible with shifts/pipelines.
- Raw connectivity anomalies: 0 loaded nets have no recovered driver and 0 nets have multiple recovered drivers.

## Limitations

- Community detection is topology-based and has no physical placement or Boolean semantics.
- A backward cone is the transitive combinational support of one boundary. Shared cells appear in multiple cones, so cone sizes cannot be summed as a partition.
- `shift-like` and `state/counter-like` are structural hints, not proofs of behavior.
- The depth number is a traversal upper bound in the recovered graph; reconvergent logic and combinational cycles can make it differ from timing depth.
