# Differential state-probe experiment

## Stimulus

Baseline: `The night s`

Each mutant flips the least-significant ASCII bit at one character position. That changes exactly one of the 121 serial input cycles.

| Position | Baseline | Mutant | Differing input cycle |
|---:|:---:|:---:|---:|
| 0 | `T` | `U` | 0 |
| 1 | `h` | `i` | 11 |
| 2 | `e` | `d` | 22 |
| 3 | ` ` | `!` | 33 |
| 4 | `n` | `o` | 44 |
| 5 | `i` | `h` | 55 |
| 6 | `g` | `f` | 66 |
| 7 | `h` | `i` | 77 |
| 8 | `t` | `u` | 88 |
| 9 | ` ` | `!` | 99 |
| 10 | `s` | `r` | 110 |

## Structural backward slices

The eight output bits share input nets `3771, 3874`.

The output bus cone contains 166 combinational gates and stops at 23 flip-flops.

The next-state cone for `cell_144` contains 47 combinational gates and stops at 57 upstream flip-flops.

### Output-bus boundary flip-flops

`cell_118`, `cell_122`, `cell_138`, `cell_144`, `cell_146`, `cell_148`, `cell_156`, `cell_162`, `cell_165`, `cell_179`, `cell_181`, `cell_183`, `cell_195`, `cell_2`, `cell_200`, `cell_3`, `cell_334`, `cell_343`, `cell_4`, `cell_478`, `cell_5`, `cell_6`, `cell_7`

### Success next-state boundary flip-flops

`cell_118`, `cell_120`, `cell_122`, `cell_124`, `cell_125`, `cell_126`, `cell_129`, `cell_131`, `cell_132`, `cell_133`, `cell_134`, `cell_135`, `cell_136`, `cell_137`, `cell_139`, `cell_142`, `cell_143`, `cell_144`, `cell_145`, `cell_146`, `cell_147`, `cell_149`, `cell_151`, `cell_152`, `cell_153`, `cell_154`, `cell_155`, `cell_156`, `cell_158`, `cell_160`, `cell_161`, `cell_163`, `cell_164`, `cell_165`, `cell_168`, `cell_169`, `cell_172`, `cell_173`, `cell_174`, `cell_178`, `cell_180`, `cell_181`, `cell_183`, `cell_186`, `cell_187`, `cell_190`, `cell_191`, `cell_192`, `cell_194`, `cell_196`, `cell_197`, `cell_198`, `cell_199`, `cell_200`, `cell_201`, `cell_203`, `cell_334`

## Baseline behavior

Post-input bytes: `TRY AGAIN`

Most active stored bits:

| Flip-flop | Transitions | First | Last |
|---|---:|---:|---:|
| cell_150 | 109 | 1 | 119 |
| cell_148 | 69 | 1 | 135 |
| cell_138 | 67 | 1 | 136 |
| cell_162 | 67 | 1 | 136 |
| cell_6 | 66 | 2 | 134 |
| cell_7 | 66 | 1 | 136 |
| cell_193 | 66 | 1 | 120 |
| cell_343 | 65 | 1 | 136 |
| cell_195 | 64 | 1 | 136 |
| cell_5 | 61 | 1 | 136 |
| cell_130 | 46 | 2 | 117 |
| cell_141 | 46 | 3 | 118 |
| cell_167 | 46 | 5 | 120 |
| cell_189 | 46 | 4 | 119 |
| cell_127 | 45 | 8 | 120 |
| cell_140 | 45 | 6 | 118 |
| cell_166 | 45 | 7 | 119 |
| cell_123 | 44 | 10 | 120 |
| cell_159 | 44 | 9 | 119 |
| cell_182 | 43 | 12 | 120 |

## Recovered serial-frame behavior

`cell_150, cell_193, cell_157, cell_184` form a modulo-11 counter from least- to most-significant bit.

It advances once per serial input bit and repeats every eleven cycles. This independently recovers the 11-cycle character framing seen in the supplied waveform.

## Recovered output-controller behavior

`cell_2, cell_3, cell_4, cell_478` form a four-bit binary counter from least- to most-significant bit.

It remains zero throughout input reception, then counts from 0 through 15 during response cycles 121 through 136. Counts 0 through 8 select the bytes `TRY AGAIN`. Counts 9 through 15 produce zero.

`net_3771` rises when response generation begins. `net_3874` is the NAND of the four counter bits, so it remains high for counts 0 through 14 and falls at terminal count 15.

## Differential propagation

| Pos. | Mutation | First D | First Q | First affected Q bits | Success next-state | First visible | Max Q difference | Final Q difference |
|---:|---|---:|---:|---|---:|---:|---:|---:|
| 0 | `T->U` | 0 | 0 | cell_122, cell_124, cell_130, cell_176 +2 | - | - | 11 | 6 |
| 1 | `h->i` | 11 | 11 | cell_118, cell_122, cell_124, cell_130 +4 | - | - | 12 | 8 |
| 2 | `e->d` | 22 | 22 | cell_122, cell_130, cell_176, cell_190 +1 | - | - | 14 | 4 |
| 3 | ` ->!` | 33 | 33 | cell_122, cell_130, cell_139, cell_176 +2 | - | - | 12 | 6 |
| 4 | `n->o` | 44 | 44 | cell_118, cell_122, cell_130, cell_139 +6 | - | - | 12 | 4 |
| 5 | `i->h` | 55 | 55 | cell_122, cell_130, cell_139, cell_174 +3 | - | - | 13 | 7 |
| 6 | `g->f` | 66 | 66 | cell_122, cell_130, cell_176, cell_190 +1 | - | - | 11 | 8 |
| 7 | `h->i` | 77 | 77 | cell_118, cell_122, cell_130, cell_176 +1 | - | - | 10 | 6 |
| 8 | `t->u` | 88 | 88 | cell_122, cell_130, cell_176, cell_5 | - | - | 10 | 5 |
| 9 | ` ->!` | 99 | 99 | cell_122, cell_130, cell_176, cell_5 | - | - | 9 | 3 |
| 10 | `s->r` | 110 | 110 | cell_118, cell_122, cell_130, cell_176 +1 | - | - | 9 | 7 |

All eleven mutations changed internal stored state, but none changed the success flip-flop's next-state input or the visible `TRY AGAIN` response during this run.

The complete per-mutant spread timelines and structural cone membership are in `analysis.json`.
