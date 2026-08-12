# Regrouped Verilog experiment: `puzzle\reversed_puzzle.v`

Each inferred block is one Louvain community in the directed functional connectivity graph. Pure clock-buffer infrastructure remains at the top level.

## Summary

- Recovered standard cells: **738**
- Inferred functional blocks: **11**
- Clock-infrastructure cells left at top level: **32**
- Total ungrouped cells left at top level: **32**

## Inferred blocks

### inferred_block_0

- Cells: **117**
- Flip-flops: **22**
- Boundary nets: **32**
- Direct top ports: `['I', 'rst_n']`
- Dominant cell families: `[('dfrtp', 22), ('o21a', 11), ('a31o', 8), ('nand4', 7), ('nand2b', 7), ('and2b', 7), ('and4bb', 5), ('nand2', 5)]`
- Members: `cell_19, cell_70, cell_72, cell_73, cell_76, cell_80, cell_83, cell_85, cell_88, cell_92, cell_93, cell_94, cell_96, cell_98, cell_103, cell_105, cell_120, cell_124, cell_131, cell_134, cell_135, cell_137, cell_142, cell_143, cell_153, cell_154, cell_158, cell_160, cell_161, cell_163, cell_164, cell_173, cell_174, cell_175, cell_178, cell_180, cell_194, cell_201, cell_203, cell_211, cell_213, cell_221, cell_229, cell_238, cell_240, cell_243, cell_244, cell_245, cell_252, cell_257, cell_260, cell_261, cell_265, cell_267, cell_268, cell_269, cell_305, cell_308, cell_314, cell_319, cell_323, cell_325, cell_327, cell_330, cell_367, cell_377, cell_378, cell_379, cell_381, cell_382, cell_383, cell_407, cell_429, cell_435, cell_441, cell_445, cell_447, cell_449, cell_450, cell_452, cell_453, cell_475, cell_476, cell_482, cell_483, cell_500, cell_503, cell_504, cell_742, cell_743, cell_754, cell_758, cell_760, cell_763, cell_766, cell_770, cell_771, cell_773, cell_774, cell_785, cell_789, cell_792, cell_794, cell_804, cell_805, cell_815, cell_816, cell_1511, cell_1523, cell_1528, cell_1533, cell_1542, cell_1572, cell_1599, cell_1603, cell_1614, cell_1616`

### inferred_block_1

- Cells: **111**
- Flip-flops: **4**
- Boundary nets: **47**
- Direct top ports: `[]`
- Dominant cell families: `[('nor2', 9), ('and2b', 8), ('nand2', 8), ('xnor2', 7), ('nand2b', 6), ('a21oi', 6), ('inv', 5), ('dfxtp', 4)]`
- Members: `cell_2, cell_3, cell_4, cell_8, cell_10, cell_20, cell_21, cell_22, cell_28, cell_30, cell_53, cell_100, cell_101, cell_104, cell_107, cell_108, cell_114, cell_115, cell_206, cell_209, cell_217, cell_218, cell_219, cell_226, cell_230, cell_235, cell_236, cell_237, cell_258, cell_270, cell_271, cell_272, cell_273, cell_275, cell_277, cell_283, cell_295, cell_310, cell_312, cell_313, cell_321, cell_324, cell_326, cell_331, cell_332, cell_335, cell_345, cell_346, cell_349, cell_357, cell_358, cell_361, cell_362, cell_363, cell_364, cell_390, cell_394, cell_406, cell_412, cell_421, cell_425, cell_428, cell_448, cell_460, cell_461, cell_464, cell_469, cell_470, cell_471, cell_474, cell_477, cell_478, cell_480, cell_487, cell_491, cell_507, cell_508, cell_532, cell_745, cell_767, cell_768, cell_777, cell_779, cell_782, cell_786, cell_798, cell_800, cell_801, cell_802, cell_812, cell_819, cell_820, cell_1513, cell_1514, cell_1515, cell_1520, cell_1525, cell_1526, cell_1532, cell_1537, cell_1565, cell_1568, cell_1576, cell_1581, cell_1583, cell_1586, cell_1587, cell_1592, cell_1602, cell_1613, cell_1615`

### inferred_block_2

- Cells: **102**
- Flip-flops: **0**
- Boundary nets: **28**
- Direct top ports: `[]`
- Dominant cell families: `[('nor2', 16), ('nand2', 11), ('or2', 7), ('xor2', 6), ('or3', 6), ('xnor2', 6), ('mux2', 5), ('a21oi', 4)]`
- Members: `cell_0, cell_1, cell_102, cell_116, cell_207, cell_208, cell_227, cell_280, cell_339, cell_352, cell_353, cell_354, cell_355, cell_356, cell_359, cell_360, cell_366, cell_385, cell_391, cell_395, cell_397, cell_399, cell_400, cell_402, cell_404, cell_409, cell_411, cell_414, cell_417, cell_431, cell_463, cell_467, cell_473, cell_481, cell_506, cell_509, cell_517, cell_518, cell_527, cell_528, cell_534, cell_536, cell_749, cell_750, cell_751, cell_752, cell_753, cell_762, cell_797, cell_809, cell_810, cell_811, cell_1155, cell_1328, cell_1396, cell_1452, cell_1455, cell_1456, cell_1459, cell_1501, cell_1508, cell_1509, cell_1519, cell_1521, cell_1527, cell_1534, cell_1536, cell_1539, cell_1540, cell_1543, cell_1545, cell_1546, cell_1547, cell_1549, cell_1550, cell_1551, cell_1552, cell_1553, cell_1554, cell_1555, cell_1556, cell_1558, cell_1559, cell_1562, cell_1563, cell_1566, cell_1567, cell_1569, cell_1573, cell_1577, cell_1578, cell_1582, cell_1585, cell_1588, cell_1591, cell_1595, cell_1600, cell_1606, cell_1608, cell_1611, cell_1612, cell_1617`

### inferred_block_3

- Cells: **76**
- Flip-flops: **5**
- Boundary nets: **69**
- Direct top ports: `['I', 'O[0]', 'O[1]', 'O[2]', 'O[3]', 'O[4]', 'O[5]', 'O[6]', 'O[7]', 'rst_n', 'success']`
- Dominant cell families: `[('a22o', 16), ('and3', 9), ('o31a', 8), ('or3', 8), ('dfrtp', 5), ('conb', 5), ('inv', 4), ('nor3b', 3)]`
- Members: `cell_9, cell_12, cell_13, cell_14, cell_16, cell_18, cell_24, cell_25, cell_26, cell_27, cell_29, cell_31, cell_32, cell_33, cell_34, cell_35, cell_36, cell_37, cell_77, cell_78, cell_106, cell_119, cell_125, cell_144, cell_145, cell_179, cell_200, cell_231, cell_274, cell_282, cell_284, cell_286, cell_287, cell_288, cell_289, cell_290, cell_291, cell_292, cell_293, cell_296, cell_297, cell_298, cell_299, cell_300, cell_301, cell_336, cell_337, cell_387, cell_388, cell_389, cell_392, cell_393, cell_396, cell_398, cell_403, cell_439, cell_442, cell_456, cell_493, cell_494, cell_495, cell_496, cell_497, cell_498, cell_511, cell_512, cell_513, cell_775, cell_781, cell_783, cell_784, cell_808, cell_813, cell_1560, cell_1605, cell_1609`

### inferred_block_4

- Cells: **71**
- Flip-flops: **17**
- Boundary nets: **31**
- Direct top ports: `['I', 'enable', 'rst_n']`
- Dominant cell families: `[('dfrtp', 13), ('mux2', 10), ('xnor2', 9), ('xor2', 6), ('a221o', 4), ('dfstp', 4), ('nor2', 4), ('and2b', 3)]`
- Members: `cell_5, cell_6, cell_7, cell_11, cell_23, cell_75, cell_109, cell_111, cell_112, cell_113, cell_117, cell_123, cell_127, cell_130, cell_138, cell_140, cell_141, cell_148, cell_159, cell_162, cell_166, cell_167, cell_189, cell_195, cell_214, cell_220, cell_266, cell_281, cell_285, cell_307, cell_315, cell_318, cell_341, cell_342, cell_343, cell_344, cell_348, cell_350, cell_365, cell_370, cell_371, cell_373, cell_410, cell_413, cell_415, cell_418, cell_420, cell_423, cell_426, cell_446, cell_459, cell_514, cell_515, cell_516, cell_520, cell_521, cell_526, cell_530, cell_531, cell_533, cell_535, cell_748, cell_799, cell_814, cell_1517, cell_1557, cell_1564, cell_1584, cell_1590, cell_1597, cell_1604`

### inferred_block_5

- Cells: **67**
- Flip-flops: **15**
- Boundary nets: **26**
- Direct top ports: `['I', 'rst_n']`
- Dominant cell families: `[('dfrtp', 15), ('and4bb', 6), ('o21a', 4), ('or4b', 4), ('nand4', 3), ('and2b', 3), ('nand2b', 3), ('a31o', 3)]`
- Members: `cell_15, cell_17, cell_38, cell_79, cell_81, cell_82, cell_84, cell_86, cell_87, cell_91, cell_99, cell_110, cell_129, cell_132, cell_133, cell_150, cell_151, cell_152, cell_157, cell_171, cell_182, cell_184, cell_185, cell_188, cell_191, cell_192, cell_193, cell_199, cell_223, cell_232, cell_233, cell_239, cell_241, cell_242, cell_246, cell_247, cell_248, cell_254, cell_262, cell_264, cell_278, cell_294, cell_303, cell_306, cell_320, cell_329, cell_340, cell_375, cell_376, cell_422, cell_433, cell_440, cell_451, cell_465, cell_488, cell_519, cell_523, cell_525, cell_741, cell_747, cell_764, cell_769, cell_776, cell_818, cell_1507, cell_1570, cell_1579`

### inferred_block_6

- Cells: **53**
- Flip-flops: **4**
- Boundary nets: **21**
- Direct top ports: `['rst_n']`
- Dominant cell families: `[('nor2', 7), ('nand2', 7), ('a21oi', 5), ('a21o', 4), ('xnor2', 4), ('dfrtp', 4), ('and3', 3), ('xor2', 3)]`
- Members: `cell_121, cell_128, cell_170, cell_202, cell_204, cell_205, cell_215, cell_216, cell_224, cell_228, cell_249, cell_250, cell_276, cell_317, cell_347, cell_351, cell_368, cell_369, cell_401, cell_405, cell_416, cell_419, cell_424, cell_430, cell_432, cell_434, cell_455, cell_462, cell_466, cell_468, cell_472, cell_479, cell_485, cell_492, cell_499, cell_510, cell_529, cell_780, cell_1510, cell_1516, cell_1518, cell_1522, cell_1524, cell_1531, cell_1541, cell_1571, cell_1574, cell_1575, cell_1580, cell_1589, cell_1593, cell_1598, cell_1601`

### inferred_block_7

- Cells: **36**
- Flip-flops: **8**
- Boundary nets: **13**
- Direct top ports: `['I', 'rst_n']`
- Dominant cell families: `[('dfrtp', 8), ('and3', 3), ('and2b', 3), ('diode', 3), ('nand2', 2), ('o21a', 2), ('a31o', 2), ('and4', 2)]`
- Members: `cell_69, cell_71, cell_74, cell_118, cell_122, cell_146, cell_156, cell_165, cell_181, cell_183, cell_225, cell_234, cell_251, cell_255, cell_311, cell_316, cell_333, cell_334, cell_338, cell_372, cell_386, cell_408, cell_427, cell_438, cell_457, cell_486, cell_489, cell_501, cell_502, cell_757, cell_772, cell_795, cell_806, cell_1530, cell_1538, cell_1610`

### inferred_block_8

- Cells: **33**
- Flip-flops: **8**
- Boundary nets: **11**
- Direct top ports: `['I', 'rst_n']`
- Dominant cell families: `[('dfrtp', 8), ('o21a', 4), ('or4', 2), ('nand2b', 2), ('and2', 2), ('nand2', 2), ('a31o', 2), ('nand4', 2)]`
- Members: `cell_90, cell_97, cell_126, cell_136, cell_139, cell_149, cell_155, cell_187, cell_190, cell_196, cell_210, cell_212, cell_253, cell_256, cell_263, cell_304, cell_322, cell_380, cell_384, cell_437, cell_454, cell_744, cell_746, cell_756, cell_761, cell_787, cell_788, cell_803, cell_817, cell_1529, cell_1535, cell_1594, cell_1596`

### inferred_block_9

- Cells: **25**
- Flip-flops: **6**
- Boundary nets: **11**
- Direct top ports: `['I', 'rst_n']`
- Dominant cell families: `[('dfrtp', 6), ('o21a', 3), ('a31o', 2), ('nand2b', 2), ('and3', 2), ('and2b', 2), ('nand4', 2), ('nand2', 1)]`
- Members: `cell_89, cell_95, cell_147, cell_168, cell_169, cell_186, cell_197, cell_198, cell_222, cell_259, cell_279, cell_309, cell_328, cell_374, cell_436, cell_443, cell_490, cell_505, cell_755, cell_759, cell_765, cell_791, cell_807, cell_1512, cell_1607`

### inferred_block_10

- Cells: **15**
- Flip-flops: **3**
- Boundary nets: **6**
- Direct top ports: `['I', 'rst_n']`
- Dominant cell families: `[('inv', 4), ('dfrtp', 3), ('mux2', 2), ('a22o', 1), ('nand2', 1), ('a31o', 1), ('a21oi', 1), ('or2', 1)]`
- Members: `cell_172, cell_176, cell_177, cell_302, cell_444, cell_458, cell_484, cell_522, cell_524, cell_778, cell_790, cell_793, cell_796, cell_1544, cell_1561`

## Detected mux/hold chains

- **12-bit chain** from `['port:I']`
  - Registers: `cell:cell_130 -> cell:cell_141 -> cell:cell_189 -> cell:cell_167 -> cell:cell_140 -> cell:cell_166 -> cell:cell_127 -> cell:cell_159 -> cell:cell_123 -> cell:cell_188 -> cell:cell_182 -> cell:cell_171`
  - Community path: `[4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5]`
  - Common controls: `['cell:cell_125', 'port:enable']`

## Interpretation boundary

The generated modules are connectivity communities, not recovered source declarations. A source module may be split across communities, and one community may combine logic from several source modules.
