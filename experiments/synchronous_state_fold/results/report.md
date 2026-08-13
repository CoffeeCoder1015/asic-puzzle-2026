# Synchronous state-fold experiment

## Essential representation

The fold replaces each recovered DFF boundary with one transition equation:

```text
old state + current inputs -> evaluate every Q_next -> one simultaneous edge -> new state
```

Reset remains per-state metadata rather than being folded into ordinary combinational logic. Outputs are roots in the same shared expression DAG, evaluated from current state and current inputs.

## Concrete structural change

| Design | Recovered combinational cells | Collapse blocks | Shared DAG nodes | State variables | Recognized mux/hold equations |
|---|---:|---:|---:|---:|---:|
| Warmup | 63 | 18 | 251 | 16 | 16 |
| Puzzle | 636 | 4 | 1738 | 92 | 0 |

The earlier flat puzzle serialization was 125,052,645 bytes. This experiment's complete shared-DAG state representation is 259,121 bytes before pretty-printing. The reduction comes from naming state boundaries and retaining shared expressions once; it is not logic minimization.

## Warmup structural control

The warmup has 16 DFFs and the fold recognizes 16 exact `enable ? source : old_value` equations. Their sources form the two known eight-bit input shift chains. This is the expected source-level behavior and validates that the representation exposes a real synchronous rule rather than merely deleting DFF symbols.

## Puzzle state rules

The puzzle has 92 state variables. Reset recovery is explicit: 84 asynchronously clear, 4 asynchronously preset, and 4 have no recovered reset pin.

Exact exhaustive evaluation of the four-bit serial-cycle state (`cell_150`, `cell_193`, `cell_157`, `cell_184`, least-significant first) shows:

- with `enable=0`, all 16 encodings hold;
- with `enable=1` and `cell_125.Q=0`, reachable values advance `0 -> 1 -> ... -> 10 -> 0`;
- once `cell_125.Q=1`, the state holds. (The full 16-state table is recorded in `state_machines.json`.)

Exact exhaustive evaluation of the four-bit response state (`cell_2`, `cell_3`, `cell_4`, `cell_478`) shows:

- `cell_200.Q=0`: every current encoding maps to zero;
- `cell_200.Q=1`: `0 -> 1 -> ... -> 15`, then 15 holds.

`cell_200.Q_next` depends only on cell_125.Q, cell_200.Q and is the sticky phase rule `cell_125.Q | cell_200.Q`. This makes the handoff mechanism legible as state-machine control.

## Confirmed terminal transition pair

The recovered logic proves:

```text
touch                    = cell_145.Q
qualifier                = net_4166 & net_4201
cell_144.Q_next candidate = qualifier & !touch
cell_179.Q_next candidate = qualifier &  touch
```

Each full next-state equation ORs its candidate with the same-shaped self-retention term. The two cones have supports of 57 and 57 boundary values and share 56 of them. Thus `cell_144` (the `success` output) and `cell_179` are a deliberate mutually selected terminal pair, not merely nearby registers.

The state fold also splits the still-unknown qualifier cleanly:

- `net_4166` is a 21-node predicate over 9 state bits, using six ANDs, two ORs, and four inversions;
- `net_4201` is an exact 46-bit polarity match: 46 state boundaries joined by 45 ANDs, with 23 inverted literals. It explicitly includes `cell_125.Q=1` and `cell_200.Q=0`, placing the decision in the one-edge handoff window.

The two supports are disjoint. This is a substantial reduction in where to look: the qualifier is not one opaque 55-input formula but a small nine-state predicate gated by one large expected-state signature.

Combined with the already-confirmed natural touch behavior and response decoding, this establishes the terminal routing:

- `qualifier & !touch` selects success/`cell_144`;
- `qualifier & touch` selects `cell_179`, whose output path produces the genuine `TWO NOT TOUCH` response;
- horizontal, vertical, and diagonal adjacency can all set the stored `touch` state naturally;
- the semantic meaning of the shared qualifier remains unknown.

## What the fold reveals¡ªand what it does not

**Proven:** state folding exposes two counters, a sticky phase transition, the stored touch bit, and the matched terminal transition pair. It also makes old-state/simultaneous-update semantics explicit, removing a common source of mistaken sequential reasoning.

**Interpretation:** the design appears to have an input-acquisition phase, a one-cycle terminal handoff, and a saturated response-emission phase. This interpretation fits all recovered transition rules but does not name the 57-state-bit qualifier predicate.

**Best next analysis:** slice `net_4166` and `net_4201` separately at state boundaries, then use known board traces to record which contributing state bits become invariant or distinguish valid from invalid boards at the handoff. Static Boolean cofactors around those observed states should be attempted before global minimization: the qualifier's whole support is large, while the terminal decision only needs its behavior on reachable handoff states.
