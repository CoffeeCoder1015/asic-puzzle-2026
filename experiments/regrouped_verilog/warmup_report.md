# Regrouped Verilog experiment: `warmup\reversed_04_final.v`

Each inferred block is one Louvain community in the directed functional connectivity graph. Pure clock-buffer infrastructure remains at the top level.

## Summary

- Recovered standard cells: **79**
- Inferred functional blocks: **4**
- Clock-infrastructure cells left at top level: **3**
- Total ungrouped cells left at top level: **3**

## Source-hierarchy comparison

- Source module definitions: **4** ¡ª `adder8, adder_demo, comparator496, shift_register`
- Source child-module instances under the recovered top: **4** ¡ª `[('adder8', 'add0'), ('comparator496', 'cmp0'), ('shift_register', 'sr_a'), ('shift_register', 'sr_b')]`
- Inferred functional block count: **4**

A matching count is only a hypothesis. The shift-chain overlap below checks whether community membership also resembles the source hierarchy.

## Exact warmup ownership through graph isomorphism

The known synthesized warmup retains source-instance prefixes. Structural isomorphism maps each anonymous recovered cell back to one of those source instances.

- inferred_block_0: `[('add0', 7), ('sr_a', 5), ('sr_b', 4), ('cmp0', 1)]`
- inferred_block_1: `[('add0', 13), ('sr_b', 4), ('sr_a', 3), ('cmp0', 1)]`
- inferred_block_2: `[('add0', 11), ('sr_a', 4), ('sr_b', 4), ('cmp0', 1)]`
- inferred_block_3: `[('add0', 10), ('sr_b', 4), ('sr_a', 4)]`

## Inferred blocks

### inferred_block_0

- Cells: **17**
- Flip-flops: **4**
- Boundary nets: **13**
- Direct top ports: `['A', 'B', 'S', 'en', 'rst_n']`
- Dominant cell families: `[('mux2', 5), ('dfrtp', 4), ('and2', 2), ('xnor2', 1), ('and4bb', 1), ('a31o', 1), ('or2', 1), ('xor2', 1)]`
- Members: `cell_4, cell_5, cell_6, cell_7, cell_8, cell_30, cell_31, cell_32, cell_33, cell_37, cell_40, cell_44, cell_47, cell_51, cell_70, cell_75, cell_147`

### inferred_block_1

- Cells: **21**
- Flip-flops: **4**
- Boundary nets: **14**
- Direct top ports: `['en', 'rst_n']`
- Dominant cell families: `[('dfrtp', 4), ('xor2', 3), ('mux2', 3), ('or2', 2), ('nor2', 2), ('and2', 2), ('a31o', 2), ('a21bo', 1)]`
- Members: `cell_0, cell_12, cell_13, cell_16, cell_21, cell_23, cell_24, cell_26, cell_35, cell_38, cell_39, cell_45, cell_50, cell_52, cell_53, cell_54, cell_58, cell_62, cell_66, cell_71, cell_73`

### inferred_block_2

- Cells: **20**
- Flip-flops: **4**
- Boundary nets: **11**
- Direct top ports: `['en', 'rst_n']`
- Dominant cell families: `[('dfrtp', 4), ('mux2', 4), ('xnor2', 2), ('nand2', 2), ('nor2', 2), ('and3', 1), ('a31o', 1), ('and2', 1)]`
- Members: `cell_1, cell_9, cell_11, cell_14, cell_15, cell_22, cell_25, cell_29, cell_36, cell_43, cell_46, cell_48, cell_49, cell_55, cell_61, cell_64, cell_67, cell_69, cell_74, cell_171`

### inferred_block_3

- Cells: **18**
- Flip-flops: **4**
- Boundary nets: **13**
- Direct top ports: `['en', 'rst_n']`
- Dominant cell families: `[('nor2', 4), ('dfrtp', 4), ('mux2', 4), ('and2', 2), ('a21o', 1), ('or2', 1), ('a31o', 1), ('xor2', 1)]`
- Members: `cell_10, cell_17, cell_18, cell_19, cell_20, cell_27, cell_28, cell_34, cell_41, cell_42, cell_56, cell_57, cell_59, cell_60, cell_63, cell_65, cell_68, cell_72`

## Detected mux/hold chains

- **8-bit chain** from `['port:A']`
  - Registers: `cell:cell_30 -> cell:cell_31 -> cell:cell_26 -> cell:cell_23 -> cell:cell_19 -> cell:cell_20 -> cell:cell_25 -> cell:cell_29`
  - Community path: `[0, 0, 1, 1, 3, 3, 2, 2]`
  - Common controls: `['port:en']`
- **8-bit chain** from `['port:B']`
  - Registers: `cell:cell_33 -> cell:cell_32 -> cell:cell_21 -> cell:cell_24 -> cell:cell_27 -> cell:cell_34 -> cell:cell_171 -> cell:cell_22`
  - Community path: `[0, 0, 1, 1, 3, 3, 2, 2]`
  - Common controls: `['port:en']`

## Interpretation boundary

The generated modules are connectivity communities, not recovered source declarations. A source module may be split across communities, and one community may combine logic from several source modules.
