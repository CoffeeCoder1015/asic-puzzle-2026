# Puzzle collapse baseline

This report describes what the original, flat formula collapse reveals before
hierarchical formula sharing is introduced. The source artifact is
`puzzle_collapsed_baseline.json`.

## Overall result

- 92 sequential instances remain as boundaries.
- 636 combinational instances collapse into four connected regions.
- Region sizes are 598, 32, 1, and 5 instances.
- The 32-instance region is clock distribution from the single `clk` input.
- The one-instance region produces `cell_200.D`.
- The five-instance region produces `cell_4.D` and `cell_478.D`.
- The remaining 598 instances form one connected region containing all eight
  `O` outputs, `cell_144.D`, most other sequential inputs, and a few diode
  connections.

The 598-instance region is too coarse to be an informative unit by itself.
Individual formulas inside it have much smaller dependency cones, so the
hierarchical representation needs to expose those shared and output-specific
substructures.

## Four-bit serial-cycle state

Bit order, least to most significant:

`cell_150`, `cell_193`, `cell_157`, `cell_184`

| Destination | Formula characters | Original gates in its cone | Boundary values used |
|---|---:|---:|---|
| `cell_150.D` | 145 | 4 | the four state bits, `cell_125.Q`, `enable` |
| `cell_193.D` | 356 | 5 | the four state bits, `cell_125.Q`, `enable` |
| `cell_157.D` | 141 | 3 | three state bits, `cell_125.Q`, `enable` |
| `cell_184.D` | 919 | 5 | the four state bits, `cell_125.Q`, `enable` |

Evaluating these four formulas together gives:

- When `enable & !cell_125.Q` is false, the four bits retain their value.
- When it is true, reachable values advance
  `0 -> 1 -> ... -> 10 -> 0`.

This statically reproduces the previously observed modulo-11 behavior. It also
exposes the condition controlling it: input framing stops once `cell_125.Q`
becomes one.

## Four-bit response state

Bit order, least to most significant:

`cell_2`, `cell_3`, `cell_4`, `cell_478`

| Destination | Region | Formula characters | Original gates in its cone | Boundary values used |
|---|---|---:|---:|---|
| `cell_2.D` | 598-instance region | 98 | 2 | all four state bits and `cell_200.Q` |
| `cell_3.D` | 598-instance region | 139 | 3 | all four state bits and `cell_200.Q` |
| `cell_4.D` | 5-instance region | 160 | 3 | all four state bits and `cell_200.Q` |
| `cell_478.D` | 5-instance region | 85 | 3 | all four state bits and `cell_200.Q` |

Evaluating the four formulas together gives:

- `cell_200.Q = 0`: the next value is zero, regardless of the current value.
- `cell_200.Q = 1`: values advance `0 -> 1 -> ... -> 15`, with 15 retained.

The separate one-gate region is:

```text
cell_200.D = cell_125.Q | cell_200.Q
```

Consequently `cell_200.Q` becomes permanently set after `cell_125.Q` is set,
and it changes the four-bit state from forced zero to counting. This connects
the two previously observed phases without relying on a waveform.

## `cell_144` relationship

`cell_144.D` has:

- a 47-gate original cone;
- 57 sequential boundary inputs;
- a 906-character flat formula.

Its top-level form is:

```text
cell_144.D = candidate
           | (cell_144.Q & (cell_200.Q | !cell_125.Q))
```

`candidate` is enabled only while `cell_125.Q = 1` and `cell_200.Q = 0`, and
requires one particular polarity pattern across the other boundary state bits.
Because `cell_200.D = cell_125.Q | cell_200.Q`, that combination describes the
handoff cycle before `cell_200.Q` becomes set. Once set, `cell_144.Q` retains
itself through the second term.

`cell_179.D` has the same 57 boundary inputs and an almost identical formula:

- the two original cones share 46 gates;
- `cell_144` has one non-shared gate;
- `cell_179` has two non-shared gates;
- their candidate terms differ at `cell_145.Q`: `cell_144` requires it low,
  while `cell_179` requires it high;
- each formula retains its own previous Q value under the same phase condition.

This is a concrete paired structure. The baseline does not establish what the
pair means, so it is left unnamed.

## Eight output bits

All eight outputs live in the 598-instance connected region, but their actual
formula cones are much smaller:

| Output | Original gates in cone | Formula characters | One input not shared by every output |
|---|---:|---:|---|
| `O[0]` | 50 | 18,436 | `cell_5.Q` |
| `O[1]` | 52 | 18,442 | `cell_195.Q` |
| `O[2]` | 48 | 17,814 | `cell_7.Q` |
| `O[3]` | 58 | 20,492 | `cell_162.Q` |
| `O[4]` | 46 | 18,010 | `cell_138.Q` |
| `O[5]` | 43 | 17,612 | `cell_6.Q` |
| `O[6]` | 43 | 17,921 | `cell_148.Q` |
| `O[7]` | 35 | 17,317 | `cell_343.Q` |

Every output formula has exactly 16 sequential inputs. Fifteen are common to
all eight outputs:

```text
cell_118.Q  cell_122.Q  cell_146.Q  cell_156.Q  cell_165.Q
cell_179.Q  cell_181.Q  cell_183.Q  cell_2.Q    cell_200.Q
cell_3.Q    cell_334.Q  cell_4.Q    cell_478.Q  cell_144.Q/success
```

The sixteenth input is the distinct bit shown in the table. Across all eight
outputs, the formula cones contain 166 original gates, of which 20 occur in
every output cone. This exactly matches the previously measured 166-gate
output slice and its 23 sequential boundaries.

The useful static structure is therefore an eight-lane result: one different
stored bit per output lane, interpreted through a large calculation shared by
all eight lanes. The hierarchical collapse should expose that shared
calculation once instead of repeating it in eight flat formulas.

## Baseline limitation

The JSON is about 125 MB because recursive string substitution duplicates
shared expressions. Some sequential-input formulas expand past eight million
characters even though they originate in the same 598-gate region. This is a
serialization problem rather than evidence of millions of distinct logical
operations. The hierarchical formula graph is required to store each shared
calculation once and make the relationships above directly inspectable.
