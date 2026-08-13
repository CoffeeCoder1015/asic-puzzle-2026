# Synchronous state fold

This experiment reads the existing hierarchical-collapse artifacts and folds
their recovered flip-flops into an explicit synchronous transition system.
It does not modify or regenerate the source netlists.

Run from the repository root:

```powershell
python experiments/synchronous_state_fold/fold_state_machine.py
```

Generated files are written under `results/`:

- `state_machines.json`: machine-readable state, reset, next-state, output,
  and shared-expression DAGs for warmup and puzzle;
- `puzzle_state_machine.txt`: a compact SSA-like rendering of the puzzle's
  terminal transition slice;
- `report.md`: measured structural comparison and interpretations.

The semantic contract is deliberately small: every `*.Q` is an old-state
value, every `next_expression` is evaluated from the same old state and
current inputs, and all states update simultaneously at the clock edge.

