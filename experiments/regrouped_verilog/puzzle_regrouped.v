// Experimental hierarchy inferred from graph communities.
// Standard-cell logic is unchanged; module boundaries are hypotheses.

module puzzle__inferred_block_0 (
    input wire I,
    input wire net_39,
    input wire net_165,
    input wire net_242,
    input wire net_292,
    output wire net_343,
    input wire net_379,
    input wire net_536,
    input wire net_550,
    input wire net_663,
    output wire net_704,
    input wire net_705,
    input wire net_715,
    input wire net_772,
    input wire net_773,
    input wire net_779,
    input wire net_869,
    input wire net_870,
    input wire net_905,
    input wire net_934,
    input wire net_945,
    input wire net_984,
    input wire net_1170,
    input wire net_1441,
    input wire net_1855,
    input wire net_2086,
    input wire net_2275,
    output wire net_2515,
    output wire net_2606,
    input wire net_2700,
    input wire net_2887,
    input wire rst_n
);
    wire net_203;
    wire net_204;
    wire net_226;
    wire net_289;
    wire net_294;
    wire net_341;
    wire net_342;
    wire net_349;
    wire net_392;
    wire net_397;
    wire net_399;
    wire net_401;
    wire net_404;
    wire net_546;
    wire net_736;
    wire net_775;
    wire net_840;
    wire net_857;
    wire net_881;
    wire net_895;
    wire net_944;
    wire net_966;
    wire net_967;
    wire net_985;
    wire net_1032;
    wire net_1033;
    wire net_1034;
    wire net_1055;
    wire net_1112;
    wire net_1185;
    wire net_1190;
    wire net_1191;
    wire net_1193;
    wire net_1194;
    wire net_1195;
    wire net_1196;
    wire net_1198;
    wire net_1213;
    wire net_1219;
    wire net_1221;
    wire net_1226;
    wire net_1235;
    wire net_1240;
    wire net_1246;
    wire net_1249;
    wire net_1267;
    wire net_1273;
    wire net_1283;
    wire net_1288;
    wire net_1289;
    wire net_1290;
    wire net_1293;
    wire net_1329;
    wire net_1394;
    wire net_1399;
    wire net_1400;
    wire net_1432;
    wire net_1438;
    wire net_1481;
    wire net_1482;
    wire net_1488;
    wire net_1497;
    wire net_1521;
    wire net_1522;
    wire net_1567;
    wire net_1593;
    wire net_1594;
    wire net_1647;
    wire net_1654;
    wire net_1672;
    wire net_1720;
    wire net_1748;
    wire net_1749;
    wire net_1765;
    wire net_1770;
    wire net_1777;
    wire net_1856;
    wire net_1857;
    wire net_1908;
    wire net_1920;
    wire net_1921;
    wire net_1922;
    wire net_1958;
    wire net_1960;
    wire net_1965;
    wire net_1966;
    wire net_1967;
    wire net_2019;
    wire net_2020;
    wire net_2035;
    wire net_2038;
    wire net_2039;
    wire net_2062;
    wire net_2066;
    wire net_2067;
    wire net_2080;
    wire net_2085;
    wire net_2126;
    wire net_2142;
    wire net_2145;
    wire net_2197;
    wire net_2202;
    wire net_2204;
    wire net_2221;
    wire net_2243;
    wire net_2274;
    wire net_2276;
    wire net_2626;

    sky130_fd_sc_hd__and4b cell_19 (
        .A_N(net_1034),
        .B(net_985),
        .D(net_857),
        .C(net_736),
        .X(net_1922)
    );

    sky130_fd_sc_hd__diode cell_70 (
        .DIODE(net_343)
    );

    sky130_fd_sc_hd__diode cell_72 (
        .DIODE(net_343)
    );

    sky130_fd_sc_hd__diode cell_73 (
        .DIODE(net_343)
    );

    sky130_fd_sc_hd__diode cell_76 (
        .DIODE(net_343)
    );

    sky130_fd_sc_hd__or4b cell_80 (
        .A(net_857),
        .D_N(net_1034),
        .C(net_985),
        .B(net_736),
        .X(net_2085)
    );

    sky130_fd_sc_hd__or4b cell_83 (
        .A(net_857),
        .D_N(net_985),
        .C(net_1034),
        .B(net_736),
        .X(net_1400)
    );

    sky130_fd_sc_hd__or4b cell_85 (
        .A(net_736),
        .D_N(net_857),
        .C(net_985),
        .B(net_1034),
        .X(net_1289)
    );

    sky130_fd_sc_hd__nand4 cell_88 (
        .A(I),
        .B(net_934),
        .D(net_1922),
        .C(net_1921),
        .Y(net_1920)
    );

    sky130_fd_sc_hd__nand4 cell_92 (
        .A(I),
        .B(net_934),
        .D(net_1267),
        .C(net_1293),
        .Y(net_1283)
    );

    sky130_fd_sc_hd__nand4 cell_93 (
        .A(I),
        .B(net_934),
        .D(net_2035),
        .C(net_1965),
        .Y(net_2062)
    );

    sky130_fd_sc_hd__nand4 cell_94 (
        .A(I),
        .B(net_934),
        .D(net_1432),
        .C(net_1438),
        .Y(net_1594)
    );

    sky130_fd_sc_hd__nand4 cell_96 (
        .A(I),
        .B(net_934),
        .D(net_1720),
        .C(net_1672),
        .Y(net_1749)
    );

    sky130_fd_sc_hd__nand4 cell_98 (
        .A(I),
        .B(net_934),
        .D(net_2145),
        .C(net_2204),
        .Y(net_2274)
    );

    sky130_fd_sc_hd__o21ai cell_103 (
        .A1(I),
        .A2(net_2515),
        .B1(net_2626),
        .Y(net_2606)
    );

    sky130_fd_sc_hd__o21ai cell_105 (
        .A1(net_536),
        .A2(net_663),
        .B1(net_242),
        .Y(net_1055)
    );

    sky130_fd_sc_hd__dfrtp cell_120 (
        .RESET_B(rst_n),
        .Q(net_1226),
        .CLK(net_984),
        .D(net_1213)
    );

    sky130_fd_sc_hd__dfrtp cell_124 (
        .RESET_B(rst_n),
        .Q(net_1672),
        .CLK(net_1441),
        .D(net_1770)
    );

    sky130_fd_sc_hd__dfrtp cell_131 (
        .RESET_B(rst_n),
        .Q(net_2019),
        .CLK(net_2086),
        .D(net_2142)
    );

    sky130_fd_sc_hd__dfrtp cell_134 (
        .RESET_B(rst_n),
        .Q(net_1191),
        .CLK(net_715),
        .D(net_1195)
    );

    sky130_fd_sc_hd__dfrtp cell_135 (
        .RESET_B(rst_n),
        .Q(net_1293),
        .CLK(net_715),
        .D(net_1273)
    );

    sky130_fd_sc_hd__dfrtp cell_137 (
        .RESET_B(rst_n),
        .Q(net_1921),
        .CLK(net_1855),
        .D(net_1960)
    );

    sky130_fd_sc_hd__dfrtp cell_142 (
        .RESET_B(rst_n),
        .Q(net_1593),
        .CLK(net_1441),
        .D(net_1765)
    );

    sky130_fd_sc_hd__dfrtp cell_143 (
        .RESET_B(rst_n),
        .Q(net_840),
        .CLK(net_984),
        .D(net_881)
    );

    sky130_fd_sc_hd__dfrtp cell_153 (
        .RESET_B(rst_n),
        .Q(net_1522),
        .CLK(net_1441),
        .D(net_1567)
    );

    sky130_fd_sc_hd__dfrtp cell_154 (
        .RESET_B(rst_n),
        .Q(net_1288),
        .CLK(net_984),
        .D(net_1329)
    );

    sky130_fd_sc_hd__dfrtp cell_158 (
        .RESET_B(rst_n),
        .Q(net_2038),
        .CLK(net_2086),
        .D(net_2197)
    );

    sky130_fd_sc_hd__dfrtp cell_160 (
        .RESET_B(rst_n),
        .Q(net_2221),
        .CLK(net_2086),
        .D(net_2243)
    );

    sky130_fd_sc_hd__dfrtp cell_161 (
        .RESET_B(rst_n),
        .Q(net_1967),
        .CLK(net_2086),
        .D(net_2020)
    );

    sky130_fd_sc_hd__dfrtp cell_163 (
        .RESET_B(rst_n),
        .Q(net_1748),
        .CLK(net_1441),
        .D(net_1908)
    );

    sky130_fd_sc_hd__dfrtp cell_164 (
        .RESET_B(rst_n),
        .Q(net_1965),
        .CLK(net_2086),
        .D(net_2066)
    );

    sky130_fd_sc_hd__dfrtp cell_173 (
        .RESET_B(rst_n),
        .Q(net_1856),
        .CLK(net_1855),
        .D(net_1857)
    );

    sky130_fd_sc_hd__dfrtp cell_174 (
        .RESET_B(rst_n),
        .Q(net_1032),
        .CLK(net_984),
        .D(net_966)
    );

    sky130_fd_sc_hd__nand4 cell_175 (
        .A(I),
        .B(net_934),
        .D(net_1033),
        .C(net_1032),
        .Y(net_895)
    );

    sky130_fd_sc_hd__dfrtp cell_178 (
        .RESET_B(rst_n),
        .Q(net_2204),
        .CLK(net_2275),
        .D(net_2276)
    );

    sky130_fd_sc_hd__dfrtp cell_180 (
        .RESET_B(rst_n),
        .Q(net_1193),
        .CLK(net_984),
        .D(net_1221)
    );

    sky130_fd_sc_hd__dfrtp cell_194 (
        .RESET_B(rst_n),
        .Q(net_1246),
        .CLK(net_715),
        .D(net_1394)
    );

    sky130_fd_sc_hd__dfrtp cell_201 (
        .RESET_B(rst_n),
        .Q(net_1438),
        .CLK(net_1441),
        .D(net_1647)
    );

    sky130_fd_sc_hd__dfrtp cell_203 (
        .RESET_B(rst_n),
        .Q(net_1488),
        .CLK(net_984),
        .D(net_1521)
    );

    sky130_fd_sc_hd__a21o cell_211 (
        .A2(net_1497),
        .B1(net_1488),
        .A1(net_1522),
        .X(net_1521)
    );

    sky130_fd_sc_hd__a21o cell_213 (
        .A2(net_2080),
        .B1(net_1967),
        .A1(net_2019),
        .X(net_2020)
    );

    sky130_fd_sc_hd__a21o cell_221 (
        .A2(net_1194),
        .B1(net_1288),
        .A1(net_1193),
        .X(net_1329)
    );

    sky130_fd_sc_hd__a21o cell_229 (
        .A2(net_1196),
        .B1(net_1191),
        .A1(net_1226),
        .X(net_1195)
    );

    sky130_fd_sc_hd__and4bb cell_238 (
        .A_N(net_736),
        .B_N(net_1034),
        .D(net_857),
        .C(net_985),
        .X(net_1720)
    );

    sky130_fd_sc_hd__and4bb cell_240 (
        .A_N(net_1034),
        .B_N(net_985),
        .D(net_857),
        .C(net_736),
        .X(net_1267)
    );

    sky130_fd_sc_hd__and4bb cell_243 (
        .A_N(net_736),
        .B_N(net_985),
        .D(net_857),
        .C(net_1034),
        .X(net_2145)
    );

    sky130_fd_sc_hd__and4bb cell_244 (
        .A_N(net_857),
        .B_N(net_1034),
        .D(net_736),
        .C(net_985),
        .X(net_1432)
    );

    sky130_fd_sc_hd__and4bb cell_245 (
        .A_N(net_857),
        .B_N(net_985),
        .D(net_736),
        .C(net_1034),
        .X(net_2035)
    );

    sky130_fd_sc_hd__and4 cell_252 (
        .C(net_204),
        .B(net_294),
        .D(net_203),
        .A(net_226),
        .X(net_289)
    );

    sky130_fd_sc_hd__nand2b cell_257 (
        .B(net_1920),
        .A_N(net_1856),
        .Y(net_1857)
    );

    sky130_fd_sc_hd__nand2b cell_260 (
        .B(net_895),
        .A_N(net_840),
        .Y(net_881)
    );

    sky130_fd_sc_hd__nand2b cell_261 (
        .B(net_1594),
        .A_N(net_1593),
        .Y(net_1765)
    );

    sky130_fd_sc_hd__nand2b cell_265 (
        .B(net_1283),
        .A_N(net_1246),
        .Y(net_1394)
    );

    sky130_fd_sc_hd__nand2b cell_267 (
        .B(net_1749),
        .A_N(net_1748),
        .Y(net_1908)
    );

    sky130_fd_sc_hd__nand2b cell_268 (
        .B(net_2062),
        .A_N(net_2038),
        .Y(net_2197)
    );

    sky130_fd_sc_hd__nand2b cell_269 (
        .B(net_2274),
        .A_N(net_2221),
        .Y(net_2243)
    );

    sky130_fd_sc_hd__and2b cell_305 (
        .A_N(net_1921),
        .B(net_1856),
        .X(net_204)
    );

    sky130_fd_sc_hd__and2b cell_308 (
        .A_N(net_1293),
        .B(net_1246),
        .X(net_401)
    );

    sky130_fd_sc_hd__a21boi cell_314 (
        .A1(I),
        .A2(net_2515),
        .B1_N(net_934),
        .Y(net_2626)
    );

    sky130_fd_sc_hd__and2b cell_319 (
        .A_N(net_1032),
        .B(net_840),
        .X(net_404)
    );

    sky130_fd_sc_hd__and2b cell_323 (
        .A_N(net_1672),
        .B(net_1748),
        .X(net_203)
    );

    sky130_fd_sc_hd__and2b cell_325 (
        .A_N(net_1965),
        .B(net_2038),
        .X(net_1185)
    );

    sky130_fd_sc_hd__and2b cell_327 (
        .A_N(net_2204),
        .B(net_2221),
        .X(net_546)
    );

    sky130_fd_sc_hd__and2b cell_330 (
        .A_N(net_1438),
        .B(net_1593),
        .X(net_226)
    );

    sky130_fd_sc_hd__xnor2 cell_367 (
        .B(net_2887),
        .A(net_2700),
        .Y(net_2515)
    );

    sky130_fd_sc_hd__or4 cell_377 (
        .D(net_2039),
        .C(net_2085),
        .B(net_1966),
        .A(net_1967),
        .X(net_2126)
    );

    sky130_fd_sc_hd__or4 cell_378 (
        .D(net_1240),
        .C(net_1289),
        .B(net_1290),
        .A(net_1288),
        .X(net_1235)
    );

    sky130_fd_sc_hd__or4 cell_379 (
        .D(net_1399),
        .C(net_1400),
        .B(net_1482),
        .A(net_1488),
        .X(net_1481)
    );

    sky130_fd_sc_hd__or4 cell_381 (
        .D(net_1198),
        .C(net_1112),
        .B(net_1190),
        .A(net_1191),
        .X(net_1219)
    );

    sky130_fd_sc_hd__or4b cell_382 (
        .A(net_857),
        .D_N(net_736),
        .C(net_985),
        .B(net_1034),
        .X(net_1112)
    );

    sky130_fd_sc_hd__diode cell_383 (
        .DIODE(net_736)
    );

    sky130_fd_sc_hd__xor2 cell_407 (
        .A(net_772),
        .B(net_773),
        .X(net_704)
    );

    sky130_fd_sc_hd__a31o cell_429 (
        .A2(net_934),
        .A1(I),
        .B1(net_1672),
        .A3(net_1720),
        .X(net_1777)
    );

    sky130_fd_sc_hd__a31o cell_435 (
        .A2(net_934),
        .A1(I),
        .B1(net_1965),
        .A3(net_2035),
        .X(net_2067)
    );

    sky130_fd_sc_hd__a31o cell_441 (
        .A2(net_934),
        .A1(I),
        .B1(net_1293),
        .A3(net_1267),
        .X(net_1249)
    );

    sky130_fd_sc_hd__a31o cell_445 (
        .A2(net_934),
        .A1(I),
        .B1(net_1921),
        .A3(net_1922),
        .X(net_1958)
    );

    sky130_fd_sc_hd__a31o cell_447 (
        .A2(net_165),
        .A1(net_536),
        .B1(net_704),
        .A3(net_392),
        .X(net_944)
    );

    sky130_fd_sc_hd__a31o cell_449 (
        .A2(net_934),
        .A1(I),
        .B1(net_1438),
        .A3(net_1432),
        .X(net_1654)
    );

    sky130_fd_sc_hd__a31o cell_450 (
        .A2(net_934),
        .A1(I),
        .B1(net_2204),
        .A3(net_2145),
        .X(net_2202)
    );

    sky130_fd_sc_hd__a31o cell_452 (
        .A2(net_934),
        .A1(I),
        .B1(net_1032),
        .A3(net_1033),
        .X(net_967)
    );

    sky130_fd_sc_hd__nor4 cell_453 (
        .D(net_985),
        .C(net_1034),
        .B(net_736),
        .A(net_857),
        .Y(net_1033)
    );

    sky130_fd_sc_hd__o211a cell_475 (
        .A1(net_704),
        .C1(net_775),
        .B1(net_870),
        .A2(net_1055),
        .X(net_985)
    );

    sky130_fd_sc_hd__o211a cell_476 (
        .A1(net_550),
        .C1(net_945),
        .B1(net_775),
        .A2(net_944),
        .X(net_736)
    );

    sky130_fd_sc_hd__o211a cell_482 (
        .A1(net_704),
        .C1(net_775),
        .B1(net_905),
        .A2(net_869),
        .X(net_1034)
    );

    sky130_fd_sc_hd__o211a cell_483 (
        .A1(net_704),
        .C1(net_775),
        .B1(net_705),
        .A2(net_779),
        .X(net_857)
    );

    sky130_fd_sc_hd__and3 cell_500 (
        .C(net_546),
        .A(net_1185),
        .B(net_341),
        .X(net_397)
    );

    sky130_fd_sc_hd__and3 cell_503 (
        .C(net_397),
        .A(net_289),
        .B(net_342),
        .X(net_343)
    );

    sky130_fd_sc_hd__and4 cell_504 (
        .C(net_401),
        .B(net_404),
        .D(net_399),
        .A(net_349),
        .X(net_342)
    );

    sky130_fd_sc_hd__o21a cell_742 (
        .B1(net_1219),
        .A2(net_1196),
        .A1(net_1226),
        .X(net_1213)
    );

    sky130_fd_sc_hd__o21a cell_743 (
        .B1(net_1235),
        .A2(net_1194),
        .A1(net_1193),
        .X(net_1221)
    );

    sky130_fd_sc_hd__o21a cell_754 (
        .B1(net_1777),
        .A2(net_1749),
        .A1(net_1748),
        .X(net_1770)
    );

    sky130_fd_sc_hd__o21a cell_758 (
        .B1(net_1958),
        .A2(net_1920),
        .A1(net_1856),
        .X(net_1960)
    );

    sky130_fd_sc_hd__o21a cell_760 (
        .B1(net_967),
        .A2(net_895),
        .A1(net_840),
        .X(net_966)
    );

    sky130_fd_sc_hd__o21a cell_763 (
        .B1(net_1249),
        .A2(net_1283),
        .A1(net_1246),
        .X(net_1273)
    );

    sky130_fd_sc_hd__o21a cell_766 (
        .B1(net_1654),
        .A2(net_1594),
        .A1(net_1593),
        .X(net_1647)
    );

    sky130_fd_sc_hd__o21a cell_770 (
        .B1(net_1481),
        .A2(net_1497),
        .A1(net_1522),
        .X(net_1567)
    );

    sky130_fd_sc_hd__o21a cell_771 (
        .B1(net_2126),
        .A2(net_2080),
        .A1(net_2019),
        .X(net_2142)
    );

    sky130_fd_sc_hd__o21a cell_773 (
        .B1(net_2067),
        .A2(net_2062),
        .A1(net_2038),
        .X(net_2066)
    );

    sky130_fd_sc_hd__o21a cell_774 (
        .B1(net_2202),
        .A2(net_2274),
        .A1(net_2221),
        .X(net_2276)
    );

    sky130_fd_sc_hd__inv cell_785 (
        .A(net_2019),
        .Y(net_1966)
    );

    sky130_fd_sc_hd__inv cell_789 (
        .A(net_1226),
        .Y(net_1190)
    );

    sky130_fd_sc_hd__inv cell_792 (
        .A(net_1193),
        .Y(net_1290)
    );

    sky130_fd_sc_hd__inv cell_794 (
        .A(net_1522),
        .Y(net_1482)
    );

    sky130_fd_sc_hd__and2 cell_804 (
        .A(net_1488),
        .B(net_1482),
        .X(net_294)
    );

    sky130_fd_sc_hd__and2 cell_805 (
        .A(net_1288),
        .B(net_1290),
        .X(net_399)
    );

    sky130_fd_sc_hd__and2 cell_815 (
        .A(net_1191),
        .B(net_1190),
        .X(net_349)
    );

    sky130_fd_sc_hd__and2 cell_816 (
        .A(net_1967),
        .B(net_1966),
        .X(net_341)
    );

    sky130_fd_sc_hd__nand2 cell_1511 (
        .A(I),
        .B(net_934),
        .Y(net_2039)
    );

    sky130_fd_sc_hd__nand2 cell_1523 (
        .A(net_39),
        .B(net_292),
        .Y(net_392)
    );

    sky130_fd_sc_hd__nand2 cell_1528 (
        .A(I),
        .B(net_934),
        .Y(net_1399)
    );

    sky130_fd_sc_hd__nand2 cell_1533 (
        .A(I),
        .B(net_934),
        .Y(net_1240)
    );

    sky130_fd_sc_hd__nand2 cell_1542 (
        .A(I),
        .B(net_934),
        .Y(net_1198)
    );

    sky130_fd_sc_hd__nor2 cell_1572 (
        .A(net_1400),
        .B(net_1399),
        .Y(net_1497)
    );

    sky130_fd_sc_hd__nor2 cell_1599 (
        .A(net_1170),
        .B(net_379),
        .Y(net_775)
    );

    sky130_fd_sc_hd__nor2 cell_1603 (
        .A(net_1112),
        .B(net_1198),
        .Y(net_1196)
    );

    sky130_fd_sc_hd__nor2 cell_1614 (
        .A(net_2085),
        .B(net_2039),
        .Y(net_2080)
    );

    sky130_fd_sc_hd__nor2 cell_1616 (
        .A(net_1289),
        .B(net_1240),
        .Y(net_1194)
    );

endmodule

module puzzle__inferred_block_1 (
    output wire net_1351,
    output wire net_1419,
    output wire net_1472,
    output wire net_1516,
    output wire net_1559,
    output wire net_1629,
    output wire net_1693,
    output wire net_1694,
    output wire net_1816,
    output wire net_1822,
    output wire net_1906,
    output wire net_1907,
    output wire net_1927,
    output wire net_1928,
    output wire net_1936,
    output wire net_1978,
    output wire net_2008,
    output wire net_2088,
    output wire net_2119,
    output wire net_2120,
    output wire net_2154,
    output wire net_2189,
    output wire net_2231,
    output wire net_2298,
    output wire net_2313,
    output wire net_2315,
    output wire net_2460,
    output wire net_2462,
    output wire net_2637,
    output wire net_2652,
    input wire net_2674,
    input wire net_2676,
    output wire net_2684,
    input wire net_2689,
    output wire net_2706,
    input wire net_2752,
    input wire net_2825,
    output wire net_2892,
    output wire net_2905,
    input wire net_2949,
    input wire net_3101,
    output wire net_3190,
    output wire net_3293,
    input wire net_3591,
    input wire net_3771,
    output wire net_3874,
    input wire net_3922
);
    wire net_1363;
    wire net_1365;
    wire net_1408;
    wire net_1409;
    wire net_1410;
    wire net_1412;
    wire net_1415;
    wire net_1418;
    wire net_1420;
    wire net_1443;
    wire net_1445;
    wire net_1448;
    wire net_1449;
    wire net_1458;
    wire net_1470;
    wire net_1484;
    wire net_1490;
    wire net_1505;
    wire net_1598;
    wire net_1599;
    wire net_1817;
    wire net_1827;
    wire net_1834;
    wire net_1871;
    wire net_1880;
    wire net_1974;
    wire net_1977;
    wire net_1992;
    wire net_2003;
    wire net_2043;
    wire net_2044;
    wire net_2102;
    wire net_2158;
    wire net_2223;
    wire net_2224;
    wire net_2283;
    wire net_2303;
    wire net_2306;
    wire net_2369;
    wire net_2456;
    wire net_2513;
    wire net_2544;
    wire net_2546;
    wire net_2547;
    wire net_2555;
    wire net_2574;
    wire net_2593;
    wire net_2597;
    wire net_2599;
    wire net_2604;
    wire net_2612;
    wire net_2648;
    wire net_2654;
    wire net_2667;
    wire net_2671;
    wire net_2695;
    wire net_2711;
    wire net_2720;
    wire net_2794;
    wire net_2806;
    wire net_2808;
    wire net_2881;
    wire net_2912;
    wire net_2927;
    wire net_2930;
    wire net_3047;
    wire net_3052;
    wire net_3809;
    wire net_3833;
    wire net_3834;
    wire net_3870;
    wire net_3893;
    wire net_3983;
    wire net_4000;

    sky130_fd_sc_hd__dfxtp cell_2 (
        .CLK(net_3591),
        .D(net_3922),
        .Q(net_1351)
    );

    sky130_fd_sc_hd__dfxtp cell_3 (
        .CLK(net_3591),
        .D(net_3983),
        .Q(net_1363)
    );

    sky130_fd_sc_hd__dfxtp cell_4 (
        .CLK(net_3101),
        .D(net_4000),
        .Q(net_1365)
    );

    sky130_fd_sc_hd__a21boi cell_8 (
        .A1(net_3834),
        .A2(net_3809),
        .B1_N(net_3771),
        .Y(net_3833)
    );

    sky130_fd_sc_hd__a21boi cell_10 (
        .A1(net_3874),
        .A2(net_3893),
        .B1_N(net_3771),
        .Y(net_3983)
    );

    sky130_fd_sc_hd__nand3 cell_20 (
        .C(net_1351),
        .A(net_1365),
        .B(net_1363),
        .Y(net_3809)
    );

    sky130_fd_sc_hd__and3b cell_21 (
        .B(net_1974),
        .C(net_1365),
        .A_N(net_1505),
        .X(net_2120)
    );

    sky130_fd_sc_hd__and3b cell_22 (
        .B(net_1365),
        .C(net_1363),
        .A_N(net_1505),
        .X(net_2088)
    );

    sky130_fd_sc_hd__o31a cell_28 (
        .A2(net_2667),
        .A1(net_1365),
        .B1(net_2671),
        .A3(net_2599),
        .X(net_2794)
    );

    sky130_fd_sc_hd__o31a cell_30 (
        .A2(net_2306),
        .A1(net_2224),
        .B1(net_2223),
        .A3(net_2369),
        .X(net_2231)
    );

    sky130_fd_sc_hd__or3b cell_53 (
        .B(net_1365),
        .A(net_1351),
        .C_N(net_1363),
        .X(net_2808)
    );

    sky130_fd_sc_hd__nand4 cell_100 (
        .A(net_1505),
        .B(net_1365),
        .D(net_1351),
        .C(net_1363),
        .Y(net_3874)
    );

    sky130_fd_sc_hd__o21ai cell_101 (
        .A1(net_1363),
        .A2(net_1365),
        .B1(net_1505),
        .Y(net_2158)
    );

    sky130_fd_sc_hd__o21ai cell_104 (
        .A1(net_2604),
        .A2(net_2547),
        .B1(net_2612),
        .Y(net_2695)
    );

    sky130_fd_sc_hd__nor3 cell_107 (
        .A(net_1351),
        .B(net_1363),
        .C(net_1365),
        .Y(net_1834)
    );

    sky130_fd_sc_hd__nor3 cell_108 (
        .A(net_1365),
        .B(net_1470),
        .C(net_1415),
        .Y(net_1418)
    );

    sky130_fd_sc_hd__nor4b cell_114 (
        .D_N(net_1505),
        .A(net_1351),
        .C(net_1365),
        .B(net_1363),
        .Y(net_1827)
    );

    sky130_fd_sc_hd__o32a cell_115 (
        .B1(net_2555),
        .B2(net_2547),
        .A2(net_2574),
        .A3(net_2648),
        .A1(net_2604),
        .X(net_2637)
    );

    sky130_fd_sc_hd__a211o cell_206 (
        .C1(net_1880),
        .A2(net_1927),
        .A1(net_1363),
        .B1(net_1827),
        .X(net_1936)
    );

    sky130_fd_sc_hd__a211o cell_209 (
        .C1(net_2599),
        .A2(net_1365),
        .A1(net_1351),
        .B1(net_2593),
        .X(net_2612)
    );

    sky130_fd_sc_hd__a21o cell_217 (
        .A2(net_1420),
        .B1(net_1363),
        .A1(net_1443),
        .X(net_1490)
    );

    sky130_fd_sc_hd__and3b cell_218 (
        .B(net_1443),
        .C(net_1445),
        .A_N(net_1470),
        .X(net_1484)
    );

    sky130_fd_sc_hd__a31oi cell_219 (
        .B1(net_1445),
        .A1(net_1415),
        .A3(net_1449),
        .A2(net_1448),
        .Y(net_1410)
    );

    sky130_fd_sc_hd__a21o cell_226 (
        .A2(net_1817),
        .B1(net_1827),
        .A1(net_1351),
        .X(net_1822)
    );

    sky130_fd_sc_hd__a21o cell_230 (
        .A2(net_1351),
        .B1(net_1365),
        .A1(net_1363),
        .X(net_3870)
    );

    sky130_fd_sc_hd__and4bb cell_235 (
        .A_N(net_1365),
        .B_N(net_1505),
        .D(net_1363),
        .C(net_1351),
        .X(net_1906)
    );

    sky130_fd_sc_hd__and4b cell_236 (
        .A_N(net_1505),
        .B(net_1365),
        .D(net_1351),
        .C(net_1363),
        .X(net_1880)
    );

    sky130_fd_sc_hd__a211oi cell_237 (
        .A2(net_1363),
        .A1(net_1351),
        .B1(net_1365),
        .C1(net_1505),
        .Y(net_1927)
    );

    sky130_fd_sc_hd__nand2b cell_258 (
        .B(net_1365),
        .A_N(net_1351),
        .Y(net_1443)
    );

    sky130_fd_sc_hd__nand2b cell_270 (
        .B(net_1505),
        .A_N(net_1365),
        .Y(net_1448)
    );

    sky130_fd_sc_hd__nand2b cell_271 (
        .B(net_1363),
        .A_N(net_1351),
        .Y(net_1977)
    );

    sky130_fd_sc_hd__nand2b cell_272 (
        .B(net_1351),
        .A_N(net_1365),
        .Y(net_1420)
    );

    sky130_fd_sc_hd__o31a cell_273 (
        .A2(net_1410),
        .A1(net_1409),
        .B1(net_1412),
        .A3(net_1418),
        .X(net_1419)
    );

    sky130_fd_sc_hd__nand2b cell_275 (
        .B(net_1351),
        .A_N(net_1363),
        .Y(net_2927)
    );

    sky130_fd_sc_hd__nand2b cell_277 (
        .B(net_1365),
        .A_N(net_1505),
        .Y(net_1449)
    );

    sky130_fd_sc_hd__a22o cell_283 (
        .B2(net_1365),
        .B1(net_2927),
        .A1(net_1351),
        .A2(net_3052),
        .X(net_3047)
    );

    sky130_fd_sc_hd__a22o cell_295 (
        .B2(net_2808),
        .B1(net_2574),
        .A1(net_2667),
        .A2(net_2544),
        .X(net_2720)
    );

    sky130_fd_sc_hd__and2b cell_310 (
        .A_N(net_1351),
        .B(net_1363),
        .X(net_2599)
    );

    sky130_fd_sc_hd__and2b cell_312 (
        .A_N(net_1363),
        .B(net_1351),
        .X(net_2306)
    );

    sky130_fd_sc_hd__and2b cell_313 (
        .A_N(net_2546),
        .B(net_2513),
        .X(net_2555)
    );

    sky130_fd_sc_hd__and2b cell_321 (
        .A_N(net_1363),
        .B(net_1351),
        .X(net_1974)
    );

    sky130_fd_sc_hd__and2b cell_324 (
        .A_N(net_1992),
        .B(net_1977),
        .X(net_1978)
    );

    sky130_fd_sc_hd__and2b cell_326 (
        .A_N(net_1365),
        .B(net_1363),
        .X(net_2303)
    );

    sky130_fd_sc_hd__and2b cell_331 (
        .A_N(net_1365),
        .B(net_1351),
        .X(net_1458)
    );

    sky130_fd_sc_hd__o32ai cell_332 (
        .A3(net_1408),
        .B2(net_1351),
        .A2(net_1410),
        .B1(net_1448),
        .A1(net_1409),
        .Y(net_1472)
    );

    sky130_fd_sc_hd__and2b cell_335 (
        .A_N(net_1363),
        .B(net_1365),
        .X(net_1409)
    );

    sky130_fd_sc_hd__a22oi cell_345 (
        .B2(net_2513),
        .B1(net_2544),
        .A1(net_1351),
        .A2(net_2593),
        .Y(net_2597)
    );

    sky130_fd_sc_hd__xnor2 cell_346 (
        .B(net_2881),
        .A(net_1505),
        .Y(net_2574)
    );

    sky130_fd_sc_hd__xnor2 cell_349 (
        .B(net_3047),
        .A(net_2676),
        .Y(net_3293)
    );

    sky130_fd_sc_hd__xnor2 cell_357 (
        .B(net_2806),
        .A(net_2912),
        .Y(net_2905)
    );

    sky130_fd_sc_hd__xnor2 cell_358 (
        .B(net_2695),
        .A(net_2689),
        .Y(net_2684)
    );

    sky130_fd_sc_hd__xnor2 cell_361 (
        .B(net_2711),
        .A(net_2674),
        .Y(net_2706)
    );

    sky130_fd_sc_hd__xnor2 cell_362 (
        .B(net_1351),
        .A(net_1363),
        .Y(net_3893)
    );

    sky130_fd_sc_hd__xnor2 cell_363 (
        .B(net_1490),
        .A(net_1484),
        .Y(net_1516)
    );

    sky130_fd_sc_hd__o21bai cell_364 (
        .A1(net_1470),
        .A2(net_1448),
        .B1_N(net_1484),
        .Y(net_1559)
    );

    sky130_fd_sc_hd__or3 cell_390 (
        .B(net_2546),
        .A(net_2667),
        .C(net_3052),
        .X(net_2912)
    );

    sky130_fd_sc_hd__or3 cell_394 (
        .B(net_1880),
        .A(net_1871),
        .C(net_1827),
        .X(net_1928)
    );

    sky130_fd_sc_hd__xor2 cell_406 (
        .A(net_2949),
        .B(net_2544),
        .X(net_2806)
    );

    sky130_fd_sc_hd__xor2 cell_412 (
        .A(net_2752),
        .B(net_2794),
        .X(net_2892)
    );

    sky130_fd_sc_hd__xor2 cell_421 (
        .A(net_2825),
        .B(net_2930),
        .X(net_3190)
    );

    sky130_fd_sc_hd__o221a cell_425 (
        .C1(net_1977),
        .A2(net_1974),
        .B1(net_2044),
        .B2(net_2043),
        .A1(net_1992),
        .X(net_2119)
    );

    sky130_fd_sc_hd__a31o cell_428 (
        .A2(net_1365),
        .A1(net_1351),
        .B1(net_1834),
        .A3(net_1817),
        .X(net_1907)
    );

    sky130_fd_sc_hd__a31o cell_448 (
        .A2(net_2593),
        .A1(net_1365),
        .B1(net_2597),
        .A3(net_2513),
        .X(net_2652)
    );

    sky130_fd_sc_hd__a21oi cell_460 (
        .A1(net_1351),
        .A2(net_1363),
        .B1(net_1505),
        .Y(net_1871)
    );

    sky130_fd_sc_hd__a21oi cell_461 (
        .A1(net_1351),
        .A2(net_2303),
        .B1(net_1505),
        .Y(net_2462)
    );

    sky130_fd_sc_hd__a21oi cell_464 (
        .A1(net_1992),
        .A2(net_1974),
        .B1(net_2003),
        .Y(net_2008)
    );

    sky130_fd_sc_hd__a21oi cell_469 (
        .A1(net_2654),
        .A2(net_2671),
        .B1(net_2667),
        .Y(net_2711)
    );

    sky130_fd_sc_hd__a21oi cell_470 (
        .A1(net_1351),
        .A2(net_1505),
        .B1(net_1365),
        .Y(net_2043)
    );

    sky130_fd_sc_hd__a21oi cell_471 (
        .A1(net_1351),
        .A2(net_1363),
        .B1(net_1505),
        .Y(net_1445)
    );

    sky130_fd_sc_hd__o211a cell_474 (
        .A1(net_2283),
        .C1(net_1363),
        .B1(net_2223),
        .A2(net_1365),
        .X(net_2313)
    );

    sky130_fd_sc_hd__o211a cell_477 (
        .A1(net_1505),
        .C1(net_3771),
        .B1(net_3870),
        .A2(net_3809),
        .X(net_4000)
    );

    sky130_fd_sc_hd__dfxtp cell_478 (
        .CLK(net_3101),
        .D(net_3833),
        .Q(net_1505)
    );

    sky130_fd_sc_hd__o211a cell_480 (
        .A1(net_1363),
        .C1(net_2158),
        .B1(net_2102),
        .A2(net_1992),
        .X(net_2189)
    );

    sky130_fd_sc_hd__and3 cell_487 (
        .C(net_2303),
        .A(net_1351),
        .B(net_2223),
        .X(net_2298)
    );

    sky130_fd_sc_hd__and3 cell_491 (
        .C(net_1365),
        .A(net_1351),
        .B(net_1363),
        .X(net_2881)
    );

    sky130_fd_sc_hd__and3 cell_507 (
        .C(net_1365),
        .A(net_1351),
        .B(net_1363),
        .X(net_2224)
    );

    sky130_fd_sc_hd__a2111oi cell_508 (
        .D1(net_2456),
        .A1(net_1351),
        .B1(net_1505),
        .C1(net_2303),
        .A2(net_1365),
        .Y(net_2460)
    );

    sky130_fd_sc_hd__mux2 cell_532 (
        .A1(net_1505),
        .A0(net_1363),
        .X(net_2003),
        .S(net_1365)
    );

    sky130_fd_sc_hd__o21a cell_745 (
        .B1(net_2158),
        .A2(net_2102),
        .A1(net_1363),
        .X(net_2154)
    );

    sky130_fd_sc_hd__o21a cell_767 (
        .B1(net_2223),
        .A2(net_2224),
        .A1(net_2283),
        .X(net_2315)
    );

    sky130_fd_sc_hd__nor3b cell_768 (
        .C_N(net_1363),
        .B(net_1365),
        .A(net_1351),
        .Y(net_2369)
    );

    sky130_fd_sc_hd__inv cell_777 (
        .A(net_1351),
        .Y(net_2283)
    );

    sky130_fd_sc_hd__inv cell_779 (
        .A(net_2654),
        .Y(net_2604)
    );

    sky130_fd_sc_hd__inv cell_782 (
        .A(net_1505),
        .Y(net_2593)
    );

    sky130_fd_sc_hd__inv cell_786 (
        .A(net_1505),
        .Y(net_2223)
    );

    sky130_fd_sc_hd__inv cell_798 (
        .A(net_1505),
        .Y(net_3834)
    );

    sky130_fd_sc_hd__o22a cell_800 (
        .A2(net_1598),
        .B1(net_1599),
        .B2(net_1470),
        .A1(net_1505),
        .X(net_1629)
    );

    sky130_fd_sc_hd__o22a cell_801 (
        .A2(net_1365),
        .B1(net_1871),
        .B2(net_1880),
        .A1(net_1363),
        .X(net_1816)
    );

    sky130_fd_sc_hd__a311o cell_802 (
        .C1(net_1445),
        .B1(net_1458),
        .A1(net_1415),
        .A2(net_1448),
        .A3(net_1449),
        .X(net_1412)
    );

    sky130_fd_sc_hd__and2 cell_812 (
        .A(net_1351),
        .B(net_1363),
        .X(net_1415)
    );

    sky130_fd_sc_hd__and2 cell_819 (
        .A(net_1598),
        .B(net_1599),
        .X(net_1694)
    );

    sky130_fd_sc_hd__and2 cell_820 (
        .A(net_1363),
        .B(net_1443),
        .X(net_1408)
    );

    sky130_fd_sc_hd__nand2 cell_1513 (
        .A(net_2927),
        .B(net_2720),
        .Y(net_2930)
    );

    sky130_fd_sc_hd__nand2 cell_1514 (
        .A(net_1365),
        .B(net_1505),
        .Y(net_1599)
    );

    sky130_fd_sc_hd__nand2 cell_1515 (
        .A(net_1365),
        .B(net_2599),
        .Y(net_2654)
    );

    sky130_fd_sc_hd__nand2 cell_1520 (
        .A(net_1351),
        .B(net_1992),
        .Y(net_2102)
    );

    sky130_fd_sc_hd__nand2 cell_1525 (
        .A(net_1351),
        .B(net_1363),
        .Y(net_2513)
    );

    sky130_fd_sc_hd__nand2 cell_1526 (
        .A(net_1363),
        .B(net_1505),
        .Y(net_2671)
    );

    sky130_fd_sc_hd__nand2 cell_1532 (
        .A(net_1351),
        .B(net_1363),
        .Y(net_1598)
    );

    sky130_fd_sc_hd__nand2 cell_1537 (
        .A(net_2544),
        .B(net_2574),
        .Y(net_2547)
    );

    sky130_fd_sc_hd__or2 cell_1565 (
        .A(net_1363),
        .B(net_1365),
        .X(net_2544)
    );

    sky130_fd_sc_hd__or2 cell_1568 (
        .A(net_1365),
        .B(net_1505),
        .X(net_1992)
    );

    sky130_fd_sc_hd__nor2 cell_1576 (
        .A(net_1505),
        .B(net_1598),
        .Y(net_1693)
    );

    sky130_fd_sc_hd__nor2 cell_1581 (
        .A(net_1351),
        .B(net_2593),
        .Y(net_2667)
    );

    sky130_fd_sc_hd__nor2 cell_1583 (
        .A(net_1351),
        .B(net_1363),
        .Y(net_2456)
    );

    sky130_fd_sc_hd__nor2 cell_1586 (
        .A(net_1365),
        .B(net_1505),
        .Y(net_3052)
    );

    sky130_fd_sc_hd__nor2 cell_1587 (
        .A(net_1351),
        .B(net_1363),
        .Y(net_2546)
    );

    sky130_fd_sc_hd__nor2 cell_1592 (
        .A(net_1363),
        .B(net_1505),
        .Y(net_1817)
    );

    sky130_fd_sc_hd__nor2 cell_1602 (
        .A(net_1351),
        .B(net_1363),
        .Y(net_1470)
    );

    sky130_fd_sc_hd__nor2 cell_1613 (
        .A(net_1505),
        .B(net_1974),
        .Y(net_2044)
    );

    sky130_fd_sc_hd__nor2 cell_1615 (
        .A(net_1365),
        .B(net_2555),
        .Y(net_2648)
    );

endmodule

module puzzle__inferred_block_2 (
    input wire net_20,
    output wire net_39,
    output wire net_165,
    output wire net_242,
    output wire net_270,
    output wire net_292,
    input wire net_319,
    input wire net_323,
    input wire net_357,
    input wire net_377,
    input wire net_380,
    input wire net_462,
    input wire net_466,
    input wire net_531,
    output wire net_536,
    output wire net_550,
    input wire net_558,
    input wire net_561,
    output wire net_663,
    input wire net_704,
    output wire net_705,
    input wire net_772,
    input wire net_773,
    output wire net_779,
    output wire net_869,
    output wire net_870,
    output wire net_905,
    output wire net_945
);
    wire net_1;
    wire net_14;
    wire net_15;
    wire net_16;
    wire net_17;
    wire net_21;
    wire net_22;
    wire net_23;
    wire net_25;
    wire net_27;
    wire net_28;
    wire net_38;
    wire net_40;
    wire net_42;
    wire net_43;
    wire net_44;
    wire net_45;
    wire net_50;
    wire net_51;
    wire net_53;
    wire net_57;
    wire net_58;
    wire net_59;
    wire net_60;
    wire net_76;
    wire net_80;
    wire net_83;
    wire net_84;
    wire net_85;
    wire net_91;
    wire net_92;
    wire net_94;
    wire net_97;
    wire net_98;
    wire net_101;
    wire net_102;
    wire net_103;
    wire net_104;
    wire net_109;
    wire net_114;
    wire net_123;
    wire net_128;
    wire net_138;
    wire net_145;
    wire net_151;
    wire net_156;
    wire net_163;
    wire net_172;
    wire net_176;
    wire net_179;
    wire net_198;
    wire net_200;
    wire net_201;
    wire net_240;
    wire net_267;
    wire net_283;
    wire net_290;
    wire net_314;
    wire net_322;
    wire net_347;
    wire net_348;
    wire net_359;
    wire net_364;
    wire net_371;
    wire net_386;
    wire net_394;
    wire net_406;
    wire net_414;
    wire net_440;
    wire net_457;
    wire net_487;
    wire net_492;
    wire net_515;
    wire net_538;
    wire net_549;
    wire net_624;
    wire net_627;
    wire net_631;
    wire net_675;
    wire net_701;
    wire net_735;
    wire net_777;
    wire net_783;
    wire net_810;
    wire net_811;
    wire net_823;
    wire net_953;
    wire net_1000;

    sky130_fd_sc_hd__o21a cell_0 (
        .B1(net_17),
        .A2(net_1),
        .A1(net_23),
        .X(net_104)
    );

    sky130_fd_sc_hd__and2 cell_1 (
        .A(net_103),
        .B(net_21),
        .X(net_1)
    );

    sky130_fd_sc_hd__o21ai cell_102 (
        .A1(net_23),
        .A2(net_27),
        .B1(net_39),
        .Y(net_201)
    );

    sky130_fd_sc_hd__o32a cell_116 (
        .B1(net_414),
        .B2(net_347),
        .A2(net_492),
        .A3(net_44),
        .A1(net_39),
        .X(net_783)
    );

    sky130_fd_sc_hd__a211o cell_207 (
        .C1(net_102),
        .A2(net_45),
        .A1(net_39),
        .B1(net_549),
        .X(net_675)
    );

    sky130_fd_sc_hd__a211o cell_208 (
        .C1(net_823),
        .A2(net_953),
        .A1(net_536),
        .B1(net_200),
        .X(net_905)
    );

    sky130_fd_sc_hd__a21o cell_227 (
        .A2(net_735),
        .B1(net_777),
        .A1(net_536),
        .X(net_779)
    );

    sky130_fd_sc_hd__o31ai cell_280 (
        .B1(net_39),
        .A1(net_25),
        .A3(net_27),
        .A2(net_138),
        .Y(net_347)
    );

    sky130_fd_sc_hd__a32o cell_339 (
        .A1(net_20),
        .A3(net_314),
        .B2(net_151),
        .B1(net_57),
        .A2(net_51),
        .X(net_270)
    );

    sky130_fd_sc_hd__xnor2 cell_352 (
        .B(net_773),
        .A(net_772),
        .Y(net_823)
    );

    sky130_fd_sc_hd__xnor2 cell_353 (
        .B(net_151),
        .A(net_57),
        .Y(net_53)
    );

    sky130_fd_sc_hd__a32o cell_354 (
        .A1(net_39),
        .A3(net_17),
        .B2(net_172),
        .B1(net_28),
        .A2(net_43),
        .X(net_953)
    );

    sky130_fd_sc_hd__xnor2 cell_355 (
        .B(net_466),
        .A(net_270),
        .Y(net_25)
    );

    sky130_fd_sc_hd__a211o cell_356 (
        .C1(net_39),
        .A2(net_91),
        .A1(net_25),
        .B1(net_198),
        .X(net_701)
    );

    sky130_fd_sc_hd__xnor2 cell_359 (
        .B(net_314),
        .A(net_22),
        .Y(net_57)
    );

    sky130_fd_sc_hd__a22o cell_360 (
        .B2(net_25),
        .B1(net_16),
        .A1(net_15),
        .A2(net_40),
        .X(net_348)
    );

    sky130_fd_sc_hd__xnor2 cell_366 (
        .B(net_531),
        .A(net_561),
        .Y(net_102)
    );

    sky130_fd_sc_hd__a21bo cell_385 (
        .B1_N(net_701),
        .A2(net_359),
        .A1(net_39),
        .X(net_735)
    );

    sky130_fd_sc_hd__or3 cell_391 (
        .B(net_364),
        .A(net_39),
        .C(net_114),
        .X(net_440)
    );

    sky130_fd_sc_hd__or3 cell_395 (
        .B(net_23),
        .A(net_42),
        .C(net_16),
        .X(net_163)
    );

    sky130_fd_sc_hd__or3 cell_397 (
        .B(net_14),
        .A(net_42),
        .C(net_138),
        .X(net_283)
    );

    sky130_fd_sc_hd__or3 cell_399 (
        .B(net_53),
        .A(net_42),
        .C(net_14),
        .X(net_60)
    );

    sky130_fd_sc_hd__and2b cell_400 (
        .A_N(net_151),
        .B(net_267),
        .X(net_38)
    );

    sky130_fd_sc_hd__or3 cell_402 (
        .B(net_515),
        .A(net_823),
        .C(net_631),
        .X(net_945)
    );

    sky130_fd_sc_hd__xor2 cell_404 (
        .A(net_323),
        .B(net_377),
        .X(net_51)
    );

    sky130_fd_sc_hd__xor2 cell_409 (
        .A(net_561),
        .B(net_531),
        .X(net_536)
    );

    sky130_fd_sc_hd__xor2 cell_411 (
        .A(net_462),
        .B(net_558),
        .X(net_39)
    );

    sky130_fd_sc_hd__xor2 cell_414 (
        .A(net_380),
        .B(net_357),
        .X(net_314)
    );

    sky130_fd_sc_hd__xor2 cell_417 (
        .A(net_270),
        .B(net_466),
        .X(net_23)
    );

    sky130_fd_sc_hd__o311a cell_431 (
        .A1(net_371),
        .A2(net_39),
        .A3(net_492),
        .C1(net_394),
        .B1(net_102),
        .X(net_550)
    );

    sky130_fd_sc_hd__a21oi cell_463 (
        .A1(net_457),
        .A2(net_156),
        .B1(net_102),
        .Y(net_631)
    );

    sky130_fd_sc_hd__a21oi cell_467 (
        .A1(net_536),
        .A2(net_406),
        .B1(net_39),
        .Y(net_811)
    );

    sky130_fd_sc_hd__a21oi cell_473 (
        .A1(net_23),
        .A2(net_179),
        .B1(net_39),
        .Y(net_172)
    );

    sky130_fd_sc_hd__o211a cell_481 (
        .A1(net_457),
        .C1(net_440),
        .B1(net_102),
        .A2(net_40),
        .X(net_515)
    );

    sky130_fd_sc_hd__and3 cell_506 (
        .C(net_1000),
        .A(net_102),
        .B(net_94),
        .X(net_777)
    );

    sky130_fd_sc_hd__and3 cell_509 (
        .C(net_21),
        .A(net_25),
        .B(net_538),
        .X(net_85)
    );

    sky130_fd_sc_hd__mux2 cell_517 (
        .A1(net_283),
        .A0(net_60),
        .X(net_386),
        .S(net_23)
    );

    sky130_fd_sc_hd__o21ba cell_518 (
        .B1_N(net_359),
        .A1(net_25),
        .A2(net_91),
        .X(net_406)
    );

    sky130_fd_sc_hd__mux2 cell_527 (
        .A1(net_348),
        .A0(net_627),
        .X(net_624),
        .S(net_39)
    );

    sky130_fd_sc_hd__o32a cell_528 (
        .B1(net_347),
        .B2(net_176),
        .A2(net_492),
        .A3(net_76),
        .A1(net_39),
        .X(net_663)
    );

    sky130_fd_sc_hd__mux2 cell_534 (
        .A1(net_25),
        .A0(net_40),
        .X(net_549),
        .S(net_50)
    );

    sky130_fd_sc_hd__mux2 cell_536 (
        .A1(net_92),
        .A0(net_783),
        .X(net_869),
        .S(net_536)
    );

    sky130_fd_sc_hd__o21a cell_749 (
        .B1(net_23),
        .A2(net_16),
        .A1(net_42),
        .X(net_198)
    );

    sky130_fd_sc_hd__o221a cell_750 (
        .C1(net_102),
        .A2(net_201),
        .B1(net_104),
        .B2(net_39),
        .A1(net_138),
        .X(net_200)
    );

    sky130_fd_sc_hd__xor2 cell_751 (
        .A(net_57),
        .B(net_151),
        .X(net_98)
    );

    sky130_fd_sc_hd__or3 cell_752 (
        .B(net_40),
        .A(net_39),
        .C(net_83),
        .X(net_156)
    );

    sky130_fd_sc_hd__xnor2 cell_753 (
        .B(net_51),
        .A(net_20),
        .Y(net_145)
    );

    sky130_fd_sc_hd__o21a cell_762 (
        .B1(net_45),
        .A2(net_101),
        .A1(net_23),
        .X(net_290)
    );

    sky130_fd_sc_hd__inv cell_797 (
        .A(net_101),
        .Y(net_538)
    );

    sky130_fd_sc_hd__and2 cell_809 (
        .A(net_123),
        .B(net_38),
        .X(net_58)
    );

    sky130_fd_sc_hd__or4 cell_810 (
        .D(net_198),
        .C(net_283),
        .B(net_102),
        .A(net_39),
        .X(net_242)
    );

    sky130_fd_sc_hd__and2 cell_811 (
        .A(net_319),
        .B(net_323),
        .X(net_322)
    );

    sky130_fd_sc_hd__o22ai cell_1155 (
        .B1(net_163),
        .B2(net_536),
        .A1(net_25),
        .A2(net_15),
        .Y(net_487)
    );

    sky130_fd_sc_hd__a221o cell_1328 (
        .C1(net_823),
        .B1(net_810),
        .B2(net_811),
        .A1(net_39),
        .A2(net_487),
        .X(net_870)
    );

    sky130_fd_sc_hd__o21ai cell_1396 (
        .A1(net_40),
        .A2(net_85),
        .B1(net_39),
        .Y(net_1000)
    );

    sky130_fd_sc_hd__a21bo cell_1452 (
        .B1_N(net_172),
        .A2(net_59),
        .A1(net_53),
        .X(net_165)
    );

    sky130_fd_sc_hd__o31ai cell_1455 (
        .B1(net_109),
        .A1(net_42),
        .A3(net_98),
        .A2(net_23),
        .Y(net_292)
    );

    sky130_fd_sc_hd__nand2b cell_1456 (
        .B(net_45),
        .A_N(net_58),
        .Y(net_50)
    );

    sky130_fd_sc_hd__o21a cell_1459 (
        .B1(net_59),
        .A2(net_43),
        .A1(net_42),
        .X(net_80)
    );

    sky130_fd_sc_hd__o211ai cell_1501 (
        .C1(net_704),
        .A2(net_624),
        .B1(net_675),
        .A1(net_536),
        .Y(net_705)
    );

    sky130_fd_sc_hd__nand2 cell_1508 (
        .A(net_57),
        .B(net_42),
        .Y(net_109)
    );

    sky130_fd_sc_hd__nand2 cell_1509 (
        .A(net_57),
        .B(net_38),
        .Y(net_103)
    );

    sky130_fd_sc_hd__nand2 cell_1519 (
        .A(net_57),
        .B(net_101),
        .Y(net_91)
    );

    sky130_fd_sc_hd__nand2 cell_1521 (
        .A(net_319),
        .B(net_323),
        .Y(net_97)
    );

    sky130_fd_sc_hd__nand2 cell_1527 (
        .A(net_145),
        .B(net_97),
        .Y(net_267)
    );

    sky130_fd_sc_hd__nand2 cell_1534 (
        .A(net_53),
        .B(net_14),
        .Y(net_15)
    );

    sky130_fd_sc_hd__nand2 cell_1536 (
        .A(net_123),
        .B(net_53),
        .Y(net_21)
    );

    sky130_fd_sc_hd__nand2 cell_1539 (
        .A(net_39),
        .B(net_43),
        .Y(net_457)
    );

    sky130_fd_sc_hd__nand2 cell_1540 (
        .A(net_39),
        .B(net_386),
        .Y(net_394)
    );

    sky130_fd_sc_hd__nand2 cell_1543 (
        .A(net_25),
        .B(net_15),
        .Y(net_43)
    );

    sky130_fd_sc_hd__nor2 cell_1545 (
        .A(net_53),
        .B(net_14),
        .Y(net_179)
    );

    sky130_fd_sc_hd__or2 cell_1546 (
        .A(net_98),
        .B(net_14),
        .X(net_16)
    );

    sky130_fd_sc_hd__nand2 cell_1547 (
        .A(net_20),
        .B(net_51),
        .Y(net_22)
    );

    sky130_fd_sc_hd__a311o cell_1549 (
        .C1(net_85),
        .B1(net_40),
        .A1(net_57),
        .A2(net_39),
        .A3(net_38),
        .X(net_94)
    );

    sky130_fd_sc_hd__o22a cell_1550 (
        .A2(net_50),
        .B1(net_17),
        .B2(net_84),
        .A1(net_23),
        .X(net_28)
    );

    sky130_fd_sc_hd__inv cell_1551 (
        .A(net_16),
        .Y(net_27)
    );

    sky130_fd_sc_hd__mux2 cell_1552 (
        .A1(net_128),
        .A0(net_80),
        .X(net_92),
        .S(net_39)
    );

    sky130_fd_sc_hd__and3 cell_1553 (
        .C(net_58),
        .A(net_25),
        .B(net_53),
        .X(net_492)
    );

    sky130_fd_sc_hd__o211a cell_1554 (
        .A1(net_42),
        .C1(net_109),
        .B1(net_25),
        .A2(net_98),
        .X(net_83)
    );

    sky130_fd_sc_hd__a21oi cell_1555 (
        .A1(net_25),
        .A2(net_58),
        .B1(net_60),
        .Y(net_76)
    );

    sky130_fd_sc_hd__a31o cell_1556 (
        .A2(net_103),
        .A1(net_23),
        .B1(net_58),
        .A3(net_21),
        .X(net_128)
    );

    sky130_fd_sc_hd__or2 cell_1558 (
        .A(net_25),
        .B(net_45),
        .X(net_17)
    );

    sky130_fd_sc_hd__or2 cell_1559 (
        .A(net_536),
        .B(net_364),
        .X(net_810)
    );

    sky130_fd_sc_hd__or2 cell_1562 (
        .A(net_25),
        .B(net_14),
        .X(net_59)
    );

    sky130_fd_sc_hd__or2 cell_1563 (
        .A(net_322),
        .B(net_240),
        .X(net_123)
    );

    sky130_fd_sc_hd__or2 cell_1566 (
        .A(net_114),
        .B(net_290),
        .X(net_627)
    );

    sky130_fd_sc_hd__or2 cell_1567 (
        .A(net_98),
        .B(net_38),
        .X(net_45)
    );

    sky130_fd_sc_hd__nor2 cell_1569 (
        .A(net_179),
        .B(net_43),
        .Y(net_414)
    );

    sky130_fd_sc_hd__nor2 cell_1573 (
        .A(net_23),
        .B(net_45),
        .Y(net_114)
    );

    sky130_fd_sc_hd__nor2 cell_1577 (
        .A(net_84),
        .B(net_38),
        .Y(net_14)
    );

    sky130_fd_sc_hd__nor2 cell_1578 (
        .A(net_23),
        .B(net_103),
        .Y(net_364)
    );

    sky130_fd_sc_hd__nor2 cell_1582 (
        .A(net_109),
        .B(net_23),
        .Y(net_359)
    );

    sky130_fd_sc_hd__nor2 cell_1585 (
        .A(net_25),
        .B(net_179),
        .Y(net_40)
    );

    sky130_fd_sc_hd__nor2 cell_1588 (
        .A(net_319),
        .B(net_323),
        .Y(net_240)
    );

    sky130_fd_sc_hd__nor2 cell_1591 (
        .A(net_145),
        .B(net_123),
        .Y(net_42)
    );

    sky130_fd_sc_hd__nor2 cell_1595 (
        .A(net_322),
        .B(net_240),
        .Y(net_84)
    );

    sky130_fd_sc_hd__nor2 cell_1600 (
        .A(net_53),
        .B(net_101),
        .Y(net_138)
    );

    sky130_fd_sc_hd__nor2 cell_1606 (
        .A(net_23),
        .B(net_179),
        .Y(net_176)
    );

    sky130_fd_sc_hd__nor2 cell_1608 (
        .A(net_109),
        .B(net_25),
        .Y(net_371)
    );

    sky130_fd_sc_hd__nor2 cell_1611 (
        .A(net_145),
        .B(net_97),
        .Y(net_151)
    );

    sky130_fd_sc_hd__nor2 cell_1612 (
        .A(net_240),
        .B(net_267),
        .Y(net_101)
    );

    sky130_fd_sc_hd__nor2 cell_1617 (
        .A(net_25),
        .B(net_60),
        .Y(net_44)
    );

endmodule

module puzzle__inferred_block_3 (
    input wire I,
    output wire O_0,
    output wire O_1,
    output wire O_2,
    output wire O_3,
    output wire O_4,
    output wire O_5,
    output wire O_6,
    output wire O_7,
    input wire net_343,
    input wire net_612,
    input wire net_684,
    input wire net_686,
    input wire net_716,
    input wire net_719,
    input wire net_888,
    input wire net_934,
    input wire net_1029,
    input wire net_1076,
    input wire net_1351,
    input wire net_1419,
    input wire net_1472,
    input wire net_1508,
    input wire net_1516,
    input wire net_1526,
    input wire net_1558,
    input wire net_1559,
    input wire net_1629,
    input wire net_1693,
    input wire net_1694,
    input wire net_1816,
    input wire net_1822,
    input wire net_1906,
    input wire net_1907,
    input wire net_1927,
    input wire net_1928,
    input wire net_1936,
    input wire net_1978,
    input wire net_2008,
    input wire net_2088,
    input wire net_2119,
    input wire net_2120,
    input wire net_2154,
    input wire net_2189,
    input wire net_2231,
    input wire net_2270,
    input wire net_2275,
    input wire net_2298,
    input wire net_2313,
    input wire net_2315,
    input wire net_2388,
    input wire net_2460,
    input wire net_2462,
    input wire net_2505,
    input wire net_2607,
    input wire net_2684,
    input wire net_2706,
    input wire net_2746,
    input wire net_2892,
    input wire net_2905,
    output wire net_3136,
    input wire net_3190,
    input wire net_3293,
    input wire net_3591,
    output wire net_3771,
    input wire net_3874,
    output wire net_3922,
    input wire rst_n,
    output wire success
);
    wire net_791;
    wire net_1084;
    wire net_1424;
    wire net_1815;
    wire net_2005;
    wire net_2239;
    wire net_2255;
    wire net_2258;
    wire net_2403;
    wire net_2479;
    wire net_3173;
    wire net_3251;
    wire net_3257;
    wire net_3258;
    wire net_3265;
    wire net_3278;
    wire net_3284;
    wire net_3303;
    wire net_3357;
    wire net_3361;
    wire net_3377;
    wire net_3396;
    wire net_3408;
    wire net_3419;
    wire net_3420;
    wire net_3426;
    wire net_3430;
    wire net_3433;
    wire net_3435;
    wire net_3443;
    wire net_3457;
    wire net_3465;
    wire net_3483;
    wire net_3485;
    wire net_3488;
    wire net_3510;
    wire net_3516;
    wire net_3518;
    wire net_3521;
    wire net_3529;
    wire net_3543;
    wire net_3549;
    wire net_3552;
    wire net_3593;
    wire net_3613;
    wire net_3617;
    wire net_3641;
    wire net_3659;
    wire net_3705;
    wire net_3709;
    wire net_3710;
    wire net_3818;
    wire net_3866;
    wire net_3920;
    wire net_3949;
    wire net_4031;
    wire net_4166;
    wire net_4176;
    wire net_4201;
    wire net_4209;
    wire net_4236;
    wire net_4240;
    wire net_4298;

    sky130_fd_sc_hd__a21boi cell_9 (
        .A1(net_1351),
        .A2(net_3874),
        .B1_N(net_3771),
        .Y(net_3922)
    );

    sky130_fd_sc_hd__nor3b cell_12 (
        .C_N(net_3419),
        .B(net_3420),
        .A(net_3377),
        .Y(net_3488)
    );

    sky130_fd_sc_hd__nor3b cell_13 (
        .C_N(net_3420),
        .B(net_3419),
        .A(net_3377),
        .Y(net_3258)
    );

    sky130_fd_sc_hd__nor3b cell_14 (
        .C_N(net_3377),
        .B(net_3420),
        .A(net_3419),
        .Y(net_3251)
    );

    sky130_fd_sc_hd__a211oi cell_16 (
        .A2(net_3920),
        .A1(net_3949),
        .B1(net_1084),
        .C1(net_791),
        .Y(net_3377)
    );

    sky130_fd_sc_hd__and4b cell_18 (
        .A_N(net_3771),
        .B(net_3136),
        .D(net_2505),
        .C(net_343),
        .X(net_4201)
    );

    sky130_fd_sc_hd__o31a cell_24 (
        .A2(net_3659),
        .A1(net_3408),
        .B1(net_3257),
        .A3(net_3396),
        .X(net_3818)
    );

    sky130_fd_sc_hd__o31a cell_25 (
        .A2(net_3709),
        .A1(net_3408),
        .B1(net_3485),
        .A3(net_3465),
        .X(net_3613)
    );

    sky130_fd_sc_hd__o31a cell_26 (
        .A2(net_3710),
        .A1(net_3408),
        .B1(net_3521),
        .A3(net_3457),
        .X(net_3543)
    );

    sky130_fd_sc_hd__o31a cell_27 (
        .A2(net_3529),
        .A1(net_3408),
        .B1(net_3443),
        .A3(net_3278),
        .X(net_3435)
    );

    sky130_fd_sc_hd__o31a cell_29 (
        .A2(net_3705),
        .A1(net_3408),
        .B1(net_3303),
        .A3(net_3483),
        .X(net_3617)
    );

    sky130_fd_sc_hd__o31a cell_31 (
        .A2(net_3641),
        .A1(net_3408),
        .B1(net_3510),
        .A3(net_3552),
        .X(net_3549)
    );

    sky130_fd_sc_hd__o31a cell_32 (
        .A2(net_3426),
        .A1(net_3408),
        .B1(net_3357),
        .A3(net_3361),
        .X(net_3516)
    );

    sky130_fd_sc_hd__o31a cell_33 (
        .A2(net_3430),
        .A1(net_3408),
        .B1(net_3433),
        .A3(net_3284),
        .X(net_3518)
    );

    sky130_fd_sc_hd__conb cell_34 (
        .LO(net_1815)
    );

    sky130_fd_sc_hd__conb cell_35 (
        .LO(net_2479)
    );

    sky130_fd_sc_hd__conb cell_36 (
        .LO(net_2005)
    );

    sky130_fd_sc_hd__conb cell_37 (
        .LO(net_2239)
    );

    sky130_fd_sc_hd__diode cell_77 (
        .DIODE(net_2239)
    );

    sky130_fd_sc_hd__or4b cell_78 (
        .A(net_791),
        .D_N(net_3920),
        .C(net_1084),
        .B(success),
        .X(net_3866)
    );

    sky130_fd_sc_hd__nor3 cell_106 (
        .A(net_3377),
        .B(net_3419),
        .C(net_3420),
        .Y(net_3593)
    );

    sky130_fd_sc_hd__nor4b cell_119 (
        .D_N(net_716),
        .A(net_684),
        .C(net_612),
        .B(net_686),
        .Y(net_791)
    );

    sky130_fd_sc_hd__dfrtp cell_125 (
        .RESET_B(rst_n),
        .Q(net_3136),
        .CLK(net_2275),
        .D(net_3173)
    );

    sky130_fd_sc_hd__dfrtp cell_144 (
        .RESET_B(rst_n),
        .Q(success),
        .CLK(net_3591),
        .D(net_4240)
    );

    sky130_fd_sc_hd__dfrtp cell_145 (
        .RESET_B(rst_n),
        .Q(net_2255),
        .CLK(net_2270),
        .D(net_2403)
    );

    sky130_fd_sc_hd__dfrtp cell_179 (
        .RESET_B(rst_n),
        .Q(net_3920),
        .CLK(net_3591),
        .D(net_4176)
    );

    sky130_fd_sc_hd__dfrtp cell_200 (
        .RESET_B(rst_n),
        .Q(net_3771),
        .CLK(net_3591),
        .D(net_4298)
    );

    sky130_fd_sc_hd__o21ba cell_231 (
        .B1_N(net_1084),
        .A1(success),
        .A2(net_3920),
        .X(net_4031)
    );

    sky130_fd_sc_hd__nand2b cell_274 (
        .B(net_3136),
        .A_N(net_3771),
        .Y(net_4236)
    );

    sky130_fd_sc_hd__a22o cell_282 (
        .B2(net_1978),
        .B1(net_3593),
        .A1(net_2313),
        .A2(net_3488),
        .X(net_3426)
    );

    sky130_fd_sc_hd__a22o cell_284 (
        .B2(net_1559),
        .B1(net_3258),
        .A1(net_2706),
        .A2(net_3251),
        .X(net_3483)
    );

    sky130_fd_sc_hd__a22o cell_286 (
        .B2(net_1516),
        .B1(net_3258),
        .A1(net_2746),
        .A2(net_3251),
        .X(net_3465)
    );

    sky130_fd_sc_hd__a22o cell_287 (
        .B2(net_2119),
        .B1(net_3593),
        .A1(net_2460),
        .A2(net_3488),
        .X(net_3709)
    );

    sky130_fd_sc_hd__a22o cell_288 (
        .B2(net_1694),
        .B1(net_3258),
        .A1(net_2684),
        .A2(net_3251),
        .X(net_3361)
    );

    sky130_fd_sc_hd__a22o cell_289 (
        .B2(net_2005),
        .B1(net_3593),
        .A1(net_2479),
        .A2(net_3488),
        .X(net_3529)
    );

    sky130_fd_sc_hd__a22o cell_290 (
        .B2(net_1472),
        .B1(net_3258),
        .A1(net_2892),
        .A2(net_3251),
        .X(net_3552)
    );

    sky130_fd_sc_hd__a22o cell_291 (
        .B2(net_2088),
        .B1(net_3593),
        .A1(net_2315),
        .A2(net_3488),
        .X(net_3659)
    );

    sky130_fd_sc_hd__a22o cell_292 (
        .B2(net_1419),
        .B1(net_3258),
        .A1(net_2905),
        .A2(net_3251),
        .X(net_3396)
    );

    sky130_fd_sc_hd__a22o cell_293 (
        .B2(net_2189),
        .B1(net_3593),
        .A1(net_2239),
        .A2(net_3488),
        .X(net_3641)
    );

    sky130_fd_sc_hd__a22o cell_296 (
        .B2(net_1629),
        .B1(net_3258),
        .A1(net_3293),
        .A2(net_3251),
        .X(net_3284)
    );

    sky130_fd_sc_hd__a22o cell_297 (
        .B2(net_2154),
        .B1(net_3593),
        .A1(net_2462),
        .A2(net_3488),
        .X(net_3430)
    );

    sky130_fd_sc_hd__a22o cell_298 (
        .B2(net_2120),
        .B1(net_3593),
        .A1(net_2298),
        .A2(net_3488),
        .X(net_3710)
    );

    sky130_fd_sc_hd__a22o cell_299 (
        .B2(net_1693),
        .B1(net_3258),
        .A1(net_3190),
        .A2(net_3251),
        .X(net_3457)
    );

    sky130_fd_sc_hd__a22o cell_300 (
        .B2(net_1424),
        .B1(net_3258),
        .A1(net_2607),
        .A2(net_3251),
        .X(net_3278)
    );

    sky130_fd_sc_hd__a22o cell_301 (
        .B2(net_2008),
        .B1(net_3593),
        .A1(net_2231),
        .A2(net_3488),
        .X(net_3705)
    );

    sky130_fd_sc_hd__a32o cell_336 (
        .A1(net_2258),
        .A3(net_4201),
        .B2(net_4236),
        .B1(success),
        .A2(net_4166),
        .X(net_4240)
    );

    sky130_fd_sc_hd__a32o cell_337 (
        .A1(net_4209),
        .A3(net_4201),
        .B2(net_4236),
        .B1(net_3920),
        .A2(net_4166),
        .X(net_4176)
    );

    sky130_fd_sc_hd__or3 cell_387 (
        .B(net_3251),
        .A(net_1822),
        .C(net_3265),
        .X(net_3257)
    );

    sky130_fd_sc_hd__or3 cell_388 (
        .B(net_3251),
        .A(net_1936),
        .C(net_3265),
        .X(net_3485)
    );

    sky130_fd_sc_hd__or3 cell_389 (
        .B(net_3251),
        .A(net_1928),
        .C(net_3265),
        .X(net_3433)
    );

    sky130_fd_sc_hd__or3 cell_392 (
        .B(net_3251),
        .A(net_1927),
        .C(net_3265),
        .X(net_3510)
    );

    sky130_fd_sc_hd__or3 cell_393 (
        .B(net_3251),
        .A(net_1907),
        .C(net_3265),
        .X(net_3357)
    );

    sky130_fd_sc_hd__or3 cell_396 (
        .B(net_3251),
        .A(net_1906),
        .C(net_3265),
        .X(net_3521)
    );

    sky130_fd_sc_hd__or3 cell_398 (
        .B(net_3251),
        .A(net_1816),
        .C(net_3265),
        .X(net_3303)
    );

    sky130_fd_sc_hd__or3 cell_403 (
        .B(net_3251),
        .A(net_1815),
        .C(net_3265),
        .X(net_3443)
    );

    sky130_fd_sc_hd__a31o cell_439 (
        .A2(net_934),
        .A1(I),
        .B1(net_2255),
        .A3(net_2388),
        .X(net_2403)
    );

    sky130_fd_sc_hd__a31o cell_442 (
        .A2(net_1508),
        .A1(net_1526),
        .B1(net_3136),
        .A3(net_934),
        .X(net_3173)
    );

    sky130_fd_sc_hd__a21oi cell_456 (
        .A1(net_3419),
        .A2(net_3420),
        .B1(net_3377),
        .Y(net_3265)
    );

    sky130_fd_sc_hd__and3 cell_493 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3818),
        .X(O_1)
    );

    sky130_fd_sc_hd__and3 cell_494 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3549),
        .X(O_4)
    );

    sky130_fd_sc_hd__and3 cell_495 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3543),
        .X(O_5)
    );

    sky130_fd_sc_hd__and3 cell_496 (
        .C(net_888),
        .A(net_1029),
        .B(net_1076),
        .X(net_1084)
    );

    sky130_fd_sc_hd__and3 cell_497 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3613),
        .X(O_3)
    );

    sky130_fd_sc_hd__and3 cell_498 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3518),
        .X(O_6)
    );

    sky130_fd_sc_hd__and3 cell_511 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3617),
        .X(O_0)
    );

    sky130_fd_sc_hd__and3 cell_512 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3516),
        .X(O_2)
    );

    sky130_fd_sc_hd__and3 cell_513 (
        .C(net_3874),
        .A(net_3771),
        .B(net_3435),
        .X(O_7)
    );

    sky130_fd_sc_hd__inv cell_775 (
        .A(net_3866),
        .Y(net_3420)
    );

    sky130_fd_sc_hd__inv cell_781 (
        .A(net_2255),
        .Y(net_2258)
    );

    sky130_fd_sc_hd__inv cell_783 (
        .A(net_2258),
        .Y(net_4209)
    );

    sky130_fd_sc_hd__inv cell_784 (
        .A(success),
        .Y(net_3949)
    );

    sky130_fd_sc_hd__and2 cell_808 (
        .A(net_1558),
        .B(net_719),
        .X(net_4166)
    );

    sky130_fd_sc_hd__conb cell_813 (
        .LO(net_1424)
    );

    sky130_fd_sc_hd__or2 cell_1560 (
        .A(net_3136),
        .B(net_3771),
        .X(net_4298)
    );

    sky130_fd_sc_hd__nor2 cell_1605 (
        .A(net_3251),
        .B(net_3265),
        .Y(net_3408)
    );

    sky130_fd_sc_hd__nor2 cell_1609 (
        .A(net_791),
        .B(net_4031),
        .Y(net_3419)
    );

endmodule

module puzzle__inferred_block_4 (
    input wire I,
    input wire enable,
    output wire net_934,
    input wire net_1855,
    input wire net_2086,
    input wire net_2140,
    output wire net_2141,
    input wire net_2213,
    input wire net_2270,
    input wire net_2275,
    output wire net_2422,
    input wire net_2515,
    input wire net_2606,
    output wire net_2607,
    input wire net_2637,
    input wire net_2652,
    output wire net_2674,
    output wire net_2676,
    output wire net_2689,
    output wire net_2700,
    input wire net_2722,
    output wire net_2746,
    output wire net_2752,
    output wire net_2825,
    output wire net_2887,
    output wire net_2949,
    input wire net_3101,
    input wire net_3136,
    input wire net_3771,
    input wire net_3874,
    input wire rst_n
);
    wire net_2073;
    wire net_2074;
    wire net_2109;
    wire net_2112;
    wire net_2173;
    wire net_2183;
    wire net_2217;
    wire net_2252;
    wire net_2254;
    wire net_2396;
    wire net_2407;
    wire net_2417;
    wire net_2419;
    wire net_2477;
    wire net_2491;
    wire net_2507;
    wire net_2537;
    wire net_2556;
    wire net_2609;
    wire net_2610;
    wire net_2618;
    wire net_2678;
    wire net_2687;
    wire net_2688;
    wire net_2709;
    wire net_2710;
    wire net_2743;
    wire net_2750;
    wire net_2754;
    wire net_2766;
    wire net_2810;
    wire net_2826;
    wire net_2829;
    wire net_2834;
    wire net_2856;
    wire net_2904;
    wire net_2915;
    wire net_2931;
    wire net_2944;
    wire net_2951;
    wire net_2973;
    wire net_2992;
    wire net_2997;
    wire net_3037;
    wire net_3041;
    wire net_3046;
    wire net_3050;
    wire net_3051;
    wire net_3057;
    wire net_3061;
    wire net_3078;
    wire net_3079;
    wire net_3119;
    wire net_3127;
    wire net_3128;
    wire net_3171;
    wire net_3189;

    sky130_fd_sc_hd__dfstp cell_5 (
        .D(net_3051),
        .SET_B(rst_n),
        .Q(net_2674),
        .CLK(net_3101)
    );

    sky130_fd_sc_hd__dfstp cell_6 (
        .D(net_2997),
        .SET_B(rst_n),
        .Q(net_2825),
        .CLK(net_2722)
    );

    sky130_fd_sc_hd__dfstp cell_7 (
        .D(net_2992),
        .SET_B(rst_n),
        .Q(net_2689),
        .CLK(net_2722)
    );

    sky130_fd_sc_hd__nor3b cell_11 (
        .C_N(net_2515),
        .B(net_2610),
        .A(net_934),
        .Y(net_2618)
    );

    sky130_fd_sc_hd__and3b cell_23 (
        .B(net_2515),
        .C(net_2678),
        .A_N(net_934),
        .X(net_2710)
    );

    sky130_fd_sc_hd__diode cell_75 (
        .DIODE(enable)
    );

    sky130_fd_sc_hd__a221o cell_109 (
        .C1(net_2754),
        .B1(net_2537),
        .B2(net_2610),
        .A1(net_934),
        .A2(net_2689),
        .X(net_3061)
    );

    sky130_fd_sc_hd__a221o cell_111 (
        .C1(net_3046),
        .B1(net_2949),
        .B2(net_2754),
        .A1(net_934),
        .A2(net_2674),
        .X(net_3041)
    );

    sky130_fd_sc_hd__a221o cell_112 (
        .C1(net_2688),
        .B1(net_2743),
        .B2(net_2754),
        .A1(net_934),
        .A2(net_2676),
        .X(net_2750)
    );

    sky130_fd_sc_hd__a221o cell_113 (
        .C1(net_2951),
        .B1(net_2754),
        .B2(net_2752),
        .A1(net_934),
        .A2(net_2609),
        .X(net_2856)
    );

    sky130_fd_sc_hd__o32a cell_117 (
        .B1(net_2829),
        .B2(net_2689),
        .A2(net_2710),
        .A3(net_3119),
        .A1(net_2766),
        .X(net_2992)
    );

    sky130_fd_sc_hd__dfrtp cell_123 (
        .RESET_B(rst_n),
        .Q(net_2109),
        .CLK(net_1855),
        .D(net_2074)
    );

    sky130_fd_sc_hd__dfrtp cell_127 (
        .RESET_B(rst_n),
        .Q(net_2173),
        .CLK(net_2270),
        .D(net_2252)
    );

    sky130_fd_sc_hd__dfrtp cell_130 (
        .RESET_B(rst_n),
        .Q(net_2422),
        .CLK(net_2275),
        .D(net_2491)
    );

    sky130_fd_sc_hd__dfrtp cell_138 (
        .RESET_B(rst_n),
        .Q(net_2752),
        .CLK(net_2722),
        .D(net_2856)
    );

    sky130_fd_sc_hd__dfrtp cell_140 (
        .RESET_B(rst_n),
        .Q(net_2254),
        .CLK(net_2213),
        .D(net_2396)
    );

    sky130_fd_sc_hd__dfrtp cell_141 (
        .RESET_B(rst_n),
        .Q(net_2419),
        .CLK(net_2213),
        .D(net_2477)
    );

    sky130_fd_sc_hd__dfrtp cell_148 (
        .RESET_B(rst_n),
        .Q(net_2676),
        .CLK(net_2086),
        .D(net_2709)
    );

    sky130_fd_sc_hd__dfrtp cell_159 (
        .RESET_B(rst_n),
        .Q(net_2073),
        .CLK(net_1855),
        .D(net_2112)
    );

    sky130_fd_sc_hd__dfrtp cell_162 (
        .RESET_B(rst_n),
        .Q(net_2609),
        .CLK(net_2722),
        .D(net_3078)
    );

    sky130_fd_sc_hd__dfrtp cell_166 (
        .RESET_B(rst_n),
        .Q(net_2217),
        .CLK(net_1855),
        .D(net_2183)
    );

    sky130_fd_sc_hd__dfrtp cell_167 (
        .RESET_B(rst_n),
        .Q(net_2417),
        .CLK(net_2270),
        .D(net_2407)
    );

    sky130_fd_sc_hd__dfrtp cell_189 (
        .RESET_B(rst_n),
        .Q(net_2507),
        .CLK(net_2275),
        .D(net_2556)
    );

    sky130_fd_sc_hd__dfrtp cell_195 (
        .RESET_B(rst_n),
        .Q(net_2949),
        .CLK(net_2722),
        .D(net_3041)
    );

    sky130_fd_sc_hd__a21o cell_214 (
        .A2(net_2949),
        .B1(net_2754),
        .A1(net_934),
        .X(net_3119)
    );

    sky130_fd_sc_hd__a21o cell_220 (
        .A2(net_3128),
        .B1(net_3127),
        .A1(net_2931),
        .X(net_2997)
    );

    sky130_fd_sc_hd__nand2b cell_266 (
        .B(net_3037),
        .A_N(net_934),
        .Y(net_2687)
    );

    sky130_fd_sc_hd__a22o cell_281 (
        .B2(net_2754),
        .B1(net_2825),
        .A1(net_934),
        .A2(net_2752),
        .X(net_3127)
    );

    sky130_fd_sc_hd__a22o cell_285 (
        .B2(net_2676),
        .B1(net_2754),
        .A1(net_934),
        .A2(net_2825),
        .X(net_2904)
    );

    sky130_fd_sc_hd__and2b cell_307 (
        .A_N(net_934),
        .B(net_3037),
        .X(net_2931)
    );

    sky130_fd_sc_hd__and2b cell_315 (
        .A_N(net_2678),
        .B(net_2537),
        .X(net_2766)
    );

    sky130_fd_sc_hd__and2b cell_318 (
        .A_N(net_3136),
        .B(enable),
        .X(net_934)
    );

    sky130_fd_sc_hd__xnor2 cell_341 (
        .B(net_3050),
        .A(net_2944),
        .Y(net_3128)
    );

    sky130_fd_sc_hd__xnor2 cell_342 (
        .B(net_2944),
        .A(net_2676),
        .Y(net_2810)
    );

    sky130_fd_sc_hd__dfstp cell_343 (
        .D(net_2750),
        .SET_B(rst_n),
        .Q(net_2743),
        .CLK(net_2722)
    );

    sky130_fd_sc_hd__xnor2 cell_344 (
        .B(net_2700),
        .A(net_2676),
        .Y(net_2834)
    );

    sky130_fd_sc_hd__xnor2 cell_348 (
        .B(net_2973),
        .A(net_2676),
        .Y(net_3189)
    );

    sky130_fd_sc_hd__xnor2 cell_350 (
        .B(net_2652),
        .A(net_2743),
        .Y(net_2607)
    );

    sky130_fd_sc_hd__xnor2 cell_365 (
        .B(net_2825),
        .A(net_2689),
        .Y(net_2944)
    );

    sky130_fd_sc_hd__xnor2 cell_370 (
        .B(net_2609),
        .A(net_2752),
        .Y(net_2700)
    );

    sky130_fd_sc_hd__xnor2 cell_371 (
        .B(net_3050),
        .A(net_2674),
        .Y(net_2610)
    );

    sky130_fd_sc_hd__xnor2 cell_373 (
        .B(net_2743),
        .A(net_2825),
        .Y(net_2887)
    );

    sky130_fd_sc_hd__xor2 cell_410 (
        .A(net_2674),
        .B(net_2834),
        .X(net_2678)
    );

    sky130_fd_sc_hd__xor2 cell_413 (
        .A(net_2689),
        .B(net_2949),
        .X(net_3079)
    );

    sky130_fd_sc_hd__xor2 cell_415 (
        .A(net_2609),
        .B(net_2743),
        .X(net_2973)
    );

    sky130_fd_sc_hd__xor2 cell_418 (
        .A(net_2609),
        .B(net_2637),
        .X(net_2746)
    );

    sky130_fd_sc_hd__xor2 cell_420 (
        .A(net_2609),
        .B(net_2949),
        .X(net_3050)
    );

    sky130_fd_sc_hd__xor2 cell_423 (
        .A(net_2674),
        .B(net_2752),
        .X(net_3057)
    );

    sky130_fd_sc_hd__o221a cell_426 (
        .C1(net_2606),
        .A2(net_2829),
        .B1(net_2687),
        .B2(net_2810),
        .A1(net_2674),
        .X(net_3051)
    );

    sky130_fd_sc_hd__a31o cell_446 (
        .A2(net_2915),
        .A1(net_2931),
        .B1(net_2904),
        .A3(net_2826),
        .X(net_2709)
    );

    sky130_fd_sc_hd__a21oi cell_459 (
        .A1(net_3079),
        .A2(net_3057),
        .B1(net_2687),
        .Y(net_3171)
    );

    sky130_fd_sc_hd__mux2 cell_514 (
        .A1(net_2173),
        .A0(net_2073),
        .X(net_2112),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_515 (
        .A1(net_2109),
        .A0(net_2140),
        .X(net_2141),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_516 (
        .A1(net_2254),
        .A0(net_2217),
        .X(net_2183),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_520 (
        .A1(net_2073),
        .A0(net_2109),
        .X(net_2074),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_521 (
        .A1(net_2419),
        .A0(net_2507),
        .X(net_2556),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_526 (
        .A1(net_2507),
        .A0(net_2417),
        .X(net_2407),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_530 (
        .A1(net_2217),
        .A0(net_2173),
        .X(net_2252),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_531 (
        .A1(I),
        .A0(net_2422),
        .X(net_2491),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_533 (
        .A1(net_2417),
        .A0(net_2254),
        .X(net_2396),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_535 (
        .A1(net_2422),
        .A0(net_2419),
        .X(net_2477),
        .S(net_934)
    );

    sky130_fd_sc_hd__o21a cell_748 (
        .B1(net_3171),
        .A2(net_3057),
        .A1(net_3079),
        .X(net_2951)
    );

    sky130_fd_sc_hd__o22a cell_799 (
        .A2(net_2829),
        .B1(net_2618),
        .B2(net_3061),
        .A1(net_2609),
        .X(net_3078)
    );

    sky130_fd_sc_hd__and2 cell_814 (
        .A(net_3771),
        .B(net_3874),
        .X(net_3037)
    );

    sky130_fd_sc_hd__nand2 cell_1517 (
        .A(net_2689),
        .B(net_2834),
        .Y(net_2915)
    );

    sky130_fd_sc_hd__or2 cell_1557 (
        .A(net_2689),
        .B(net_2834),
        .X(net_2826)
    );

    sky130_fd_sc_hd__or2 cell_1564 (
        .A(net_3037),
        .B(net_934),
        .X(net_2829)
    );

    sky130_fd_sc_hd__nor2 cell_1584 (
        .A(net_2687),
        .B(net_3189),
        .Y(net_3046)
    );

    sky130_fd_sc_hd__nor2 cell_1590 (
        .A(net_3037),
        .B(net_934),
        .Y(net_2754)
    );

    sky130_fd_sc_hd__nor2 cell_1597 (
        .A(net_934),
        .B(net_2515),
        .Y(net_2537)
    );

    sky130_fd_sc_hd__nor2 cell_1604 (
        .A(net_2515),
        .B(net_2687),
        .Y(net_2688)
    );

endmodule

module puzzle__inferred_block_5 (
    input wire I,
    output wire net_20,
    output wire net_319,
    output wire net_380,
    output wire net_832,
    input wire net_934,
    output wire net_1526,
    input wire net_1855,
    output wire net_2140,
    input wire net_2141,
    input wire net_2213,
    input wire net_2270,
    output wire net_2388,
    input wire net_2422,
    output wire net_2467,
    output wire net_2985,
    output wire net_3145,
    input wire net_3247,
    output wire net_3249,
    output wire net_3502,
    input wire net_3799,
    input wire net_3842,
    output wire net_4122,
    output wire net_4229,
    output wire net_4325,
    input wire rst_n
);
    wire net_1627;
    wire net_1718;
    wire net_1723;
    wire net_1738;
    wire net_2164;
    wire net_2218;
    wire net_2235;
    wire net_2268;
    wire net_2296;
    wire net_2302;
    wire net_2333;
    wire net_2355;
    wire net_2374;
    wire net_2393;
    wire net_2409;
    wire net_2421;
    wire net_2440;
    wire net_2471;
    wire net_2475;
    wire net_2501;
    wire net_2521;
    wire net_3675;
    wire net_3676;
    wire net_3677;
    wire net_3682;
    wire net_3683;
    wire net_3685;
    wire net_3686;
    wire net_3720;
    wire net_3751;
    wire net_3753;
    wire net_3755;
    wire net_3756;
    wire net_3759;
    wire net_3790;
    wire net_3808;
    wire net_3830;
    wire net_3847;
    wire net_3860;
    wire net_3861;
    wire net_3863;
    wire net_3902;
    wire net_3958;
    wire net_3962;
    wire net_3968;
    wire net_3970;
    wire net_4023;
    wire net_4027;
    wire net_4028;
    wire net_4054;
    wire net_4100;
    wire net_4108;

    sky130_fd_sc_hd__a211oi cell_15 (
        .A2(net_1526),
        .A1(net_934),
        .B1(net_2374),
        .C1(net_2164),
        .Y(net_2302)
    );

    sky130_fd_sc_hd__and4b cell_17 (
        .A_N(net_832),
        .B(net_380),
        .D(net_20),
        .C(net_319),
        .X(net_3968)
    );

    sky130_fd_sc_hd__conb cell_38 (
        .HI(net_1627)
    );

    sky130_fd_sc_hd__or4b cell_79 (
        .A(net_319),
        .D_N(net_20),
        .C(net_380),
        .B(net_832),
        .X(net_3249)
    );

    sky130_fd_sc_hd__or4b cell_81 (
        .A(net_20),
        .D_N(net_832),
        .C(net_380),
        .B(net_319),
        .X(net_4122)
    );

    sky130_fd_sc_hd__or4b cell_82 (
        .A(net_20),
        .D_N(net_319),
        .C(net_380),
        .B(net_832),
        .X(net_3145)
    );

    sky130_fd_sc_hd__or4b cell_84 (
        .A(net_20),
        .D_N(net_380),
        .C(net_832),
        .B(net_319),
        .X(net_3686)
    );

    sky130_fd_sc_hd__nor4 cell_86 (
        .D(net_380),
        .C(net_832),
        .B(net_319),
        .A(net_20),
        .Y(net_2985)
    );

    sky130_fd_sc_hd__nand4 cell_87 (
        .A(I),
        .B(net_934),
        .D(net_3968),
        .C(net_4028),
        .Y(net_4054)
    );

    sky130_fd_sc_hd__nand4 cell_91 (
        .A(I),
        .B(net_934),
        .D(net_3756),
        .C(net_3755),
        .Y(net_3790)
    );

    sky130_fd_sc_hd__nand4 cell_99 (
        .A(I),
        .B(net_934),
        .D(net_3970),
        .C(net_3902),
        .Y(net_3863)
    );

    sky130_fd_sc_hd__a221o cell_110 (
        .C1(net_2268),
        .B1(net_1627),
        .B2(net_2218),
        .A1(net_1738),
        .A2(net_2140),
        .X(net_2388)
    );

    sky130_fd_sc_hd__dfrtp cell_129 (
        .RESET_B(rst_n),
        .Q(net_3902),
        .CLK(net_3799),
        .D(net_3962)
    );

    sky130_fd_sc_hd__dfrtp cell_132 (
        .RESET_B(rst_n),
        .Q(net_3861),
        .CLK(net_3842),
        .D(net_3860)
    );

    sky130_fd_sc_hd__dfrtp cell_133 (
        .RESET_B(rst_n),
        .Q(net_3676),
        .CLK(net_3247),
        .D(net_3720)
    );

    sky130_fd_sc_hd__dfrtp cell_150 (
        .RESET_B(rst_n),
        .Q(net_319),
        .CLK(net_2213),
        .D(net_2440)
    );

    sky130_fd_sc_hd__dfrtp cell_151 (
        .RESET_B(rst_n),
        .Q(net_4023),
        .CLK(net_3842),
        .D(net_4108)
    );

    sky130_fd_sc_hd__dfrtp cell_152 (
        .RESET_B(rst_n),
        .Q(net_3751),
        .CLK(net_3799),
        .D(net_3753)
    );

    sky130_fd_sc_hd__dfrtp cell_157 (
        .RESET_B(rst_n),
        .Q(net_380),
        .CLK(net_2213),
        .D(net_2235)
    );

    sky130_fd_sc_hd__dfrtp cell_171 (
        .RESET_B(rst_n),
        .Q(net_2421),
        .CLK(net_2270),
        .D(net_2355)
    );

    sky130_fd_sc_hd__dfrtp cell_182 (
        .RESET_B(rst_n),
        .Q(net_2218),
        .CLK(net_2270),
        .D(net_2333)
    );

    sky130_fd_sc_hd__dfrtp cell_184 (
        .RESET_B(rst_n),
        .Q(net_832),
        .CLK(net_2213),
        .D(net_2501)
    );

    sky130_fd_sc_hd__a221oi cell_185 (
        .B1(net_2296),
        .B2(net_832),
        .C1(net_2521),
        .A2(net_1526),
        .A1(net_934),
        .Y(net_2501)
    );

    sky130_fd_sc_hd__dfrtp cell_188 (
        .RESET_B(rst_n),
        .Q(net_2140),
        .CLK(net_1855),
        .D(net_2141)
    );

    sky130_fd_sc_hd__dfrtp cell_191 (
        .RESET_B(rst_n),
        .Q(net_3675),
        .CLK(net_3247),
        .D(net_3683)
    );

    sky130_fd_sc_hd__dfrtp cell_192 (
        .RESET_B(rst_n),
        .Q(net_3755),
        .CLK(net_3247),
        .D(net_3847)
    );

    sky130_fd_sc_hd__dfrtp cell_193 (
        .RESET_B(rst_n),
        .Q(net_20),
        .CLK(net_2213),
        .D(net_2302)
    );

    sky130_fd_sc_hd__dfrtp cell_199 (
        .RESET_B(rst_n),
        .Q(net_4028),
        .CLK(net_3799),
        .D(net_4027)
    );

    sky130_fd_sc_hd__a21o cell_223 (
        .A2(net_3677),
        .B1(net_3675),
        .A1(net_3676),
        .X(net_3683)
    );

    sky130_fd_sc_hd__and4bb cell_232 (
        .A_N(net_20),
        .B_N(net_380),
        .D(net_319),
        .C(net_832),
        .X(net_4229)
    );

    sky130_fd_sc_hd__and4bb cell_233 (
        .A_N(net_832),
        .B_N(net_380),
        .D(net_20),
        .C(net_319),
        .X(net_3502)
    );

    sky130_fd_sc_hd__and4bb cell_239 (
        .A_N(net_319),
        .B_N(net_832),
        .D(net_20),
        .C(net_380),
        .X(net_3970)
    );

    sky130_fd_sc_hd__and4bb cell_241 (
        .A_N(net_319),
        .B_N(net_380),
        .D(net_20),
        .C(net_832),
        .X(net_1526)
    );

    sky130_fd_sc_hd__a41oi cell_242 (
        .A4(net_934),
        .A1(net_20),
        .B1(net_832),
        .A2(net_319),
        .A3(net_380),
        .Y(net_2521)
    );

    sky130_fd_sc_hd__and4bb cell_246 (
        .A_N(net_319),
        .B_N(net_380),
        .D(net_20),
        .C(net_832),
        .X(net_4325)
    );

    sky130_fd_sc_hd__and4bb cell_247 (
        .A_N(net_20),
        .B_N(net_832),
        .D(net_319),
        .C(net_380),
        .X(net_3756)
    );

    sky130_fd_sc_hd__and4 cell_248 (
        .C(net_2475),
        .B(net_2393),
        .D(net_2471),
        .A(net_3830),
        .X(net_2467)
    );

    sky130_fd_sc_hd__and4 cell_254 (
        .C(net_380),
        .B(net_319),
        .D(net_934),
        .A(net_20),
        .X(net_2296)
    );

    sky130_fd_sc_hd__nand2b cell_262 (
        .B(net_3863),
        .A_N(net_3861),
        .Y(net_3860)
    );

    sky130_fd_sc_hd__nand2b cell_264 (
        .B(net_4054),
        .A_N(net_4023),
        .Y(net_4108)
    );

    sky130_fd_sc_hd__nand2b cell_278 (
        .B(net_3790),
        .A_N(net_3751),
        .Y(net_3753)
    );

    sky130_fd_sc_hd__a22o cell_294 (
        .B2(net_2421),
        .B1(net_1723),
        .A1(net_1718),
        .A2(net_2422),
        .X(net_2268)
    );

    sky130_fd_sc_hd__or4bb cell_303 (
        .D_N(net_20),
        .C_N(net_832),
        .B(net_380),
        .A(net_319),
        .X(net_1738)
    );

    sky130_fd_sc_hd__and2b cell_306 (
        .A_N(net_3755),
        .B(net_3751),
        .X(net_3830)
    );

    sky130_fd_sc_hd__and2b cell_320 (
        .A_N(net_4028),
        .B(net_4023),
        .X(net_2475)
    );

    sky130_fd_sc_hd__and2b cell_329 (
        .A_N(net_3902),
        .B(net_3861),
        .X(net_2471)
    );

    sky130_fd_sc_hd__xnor2 cell_340 (
        .B(net_934),
        .A(net_319),
        .Y(net_2409)
    );

    sky130_fd_sc_hd__or4 cell_375 (
        .D(net_3759),
        .C(net_3686),
        .B(net_3685),
        .A(net_3675),
        .X(net_3682)
    );

    sky130_fd_sc_hd__or4 cell_376 (
        .D(net_832),
        .C(net_380),
        .B(net_20),
        .A(net_319),
        .X(net_1718)
    );

    sky130_fd_sc_hd__xor2 cell_422 (
        .A(net_380),
        .B(net_2164),
        .X(net_2235)
    );

    sky130_fd_sc_hd__a31o cell_433 (
        .A2(net_934),
        .A1(I),
        .B1(net_3902),
        .A3(net_3970),
        .X(net_3958)
    );

    sky130_fd_sc_hd__a31o cell_440 (
        .A2(net_934),
        .A1(I),
        .B1(net_3755),
        .A3(net_3756),
        .X(net_3808)
    );

    sky130_fd_sc_hd__a31o cell_451 (
        .A2(net_934),
        .A1(I),
        .B1(net_4028),
        .A3(net_3968),
        .X(net_4100)
    );

    sky130_fd_sc_hd__a21oi cell_465 (
        .A1(net_319),
        .A2(net_934),
        .B1(net_20),
        .Y(net_2374)
    );

    sky130_fd_sc_hd__and3 cell_488 (
        .C(net_934),
        .A(net_20),
        .B(net_319),
        .X(net_2164)
    );

    sky130_fd_sc_hd__mux2 cell_519 (
        .A1(net_2218),
        .A0(net_2421),
        .X(net_2355),
        .S(net_934)
    );

    sky130_fd_sc_hd__mux2 cell_523 (
        .A1(net_2140),
        .A0(net_2218),
        .X(net_2333),
        .S(net_934)
    );

    sky130_fd_sc_hd__buf cell_525 (
        .A(net_1718),
        .X(net_1723)
    );

    sky130_fd_sc_hd__o21a cell_741 (
        .B1(net_3682),
        .A2(net_3677),
        .A1(net_3676),
        .X(net_3720)
    );

    sky130_fd_sc_hd__o21a cell_747 (
        .B1(net_3808),
        .A2(net_3790),
        .A1(net_3751),
        .X(net_3847)
    );

    sky130_fd_sc_hd__o21a cell_764 (
        .B1(net_3958),
        .A2(net_3863),
        .A1(net_3861),
        .X(net_3962)
    );

    sky130_fd_sc_hd__o21a cell_769 (
        .B1(net_4100),
        .A2(net_4054),
        .A1(net_4023),
        .X(net_4027)
    );

    sky130_fd_sc_hd__inv cell_776 (
        .A(net_3676),
        .Y(net_3685)
    );

    sky130_fd_sc_hd__and2 cell_818 (
        .A(net_3675),
        .B(net_3685),
        .X(net_2393)
    );

    sky130_fd_sc_hd__nand2 cell_1507 (
        .A(I),
        .B(net_934),
        .Y(net_3759)
    );

    sky130_fd_sc_hd__nor2 cell_1570 (
        .A(net_3686),
        .B(net_3759),
        .Y(net_3677)
    );

    sky130_fd_sc_hd__nor2 cell_1579 (
        .A(net_1526),
        .B(net_2409),
        .Y(net_2440)
    );

endmodule

module puzzle__inferred_block_6 (
    input wire net_270,
    output wire net_323,
    output wire net_357,
    output wire net_377,
    output wire net_379,
    input wire net_380,
    output wire net_462,
    output wire net_466,
    output wire net_531,
    output wire net_558,
    output wire net_561,
    input wire net_771,
    output wire net_772,
    output wire net_773,
    input wire net_832,
    input wire net_934,
    output wire net_1170,
    output wire net_1508,
    input wire net_1526,
    input wire net_1588,
    input wire rst_n
);
    wire net_325;
    wire net_378;
    wire net_382;
    wire net_436;
    wire net_445;
    wire net_454;
    wire net_456;
    wire net_510;
    wire net_523;
    wire net_565;
    wire net_574;
    wire net_579;
    wire net_606;
    wire net_639;
    wire net_646;
    wire net_652;
    wire net_653;
    wire net_659;
    wire net_677;
    wire net_694;
    wire net_695;
    wire net_828;
    wire net_873;
    wire net_874;
    wire net_878;
    wire net_987;
    wire net_1006;
    wire net_1038;
    wire net_1510;
    wire net_1527;
    wire net_1528;
    wire net_1531;
    wire net_1554;
    wire net_1581;
    wire net_1663;
    wire net_1688;
    wire net_1700;
    wire net_1773;
    wire net_1799;
    wire net_1825;

    sky130_fd_sc_hd__dfrtp cell_121 (
        .RESET_B(rst_n),
        .Q(net_377),
        .CLK(net_1588),
        .D(net_1700)
    );

    sky130_fd_sc_hd__dfrtp cell_128 (
        .RESET_B(rst_n),
        .Q(net_323),
        .CLK(net_771),
        .D(net_1554)
    );

    sky130_fd_sc_hd__dfrtp cell_170 (
        .RESET_B(rst_n),
        .Q(net_378),
        .CLK(net_1588),
        .D(net_1581)
    );

    sky130_fd_sc_hd__dfrtp cell_202 (
        .RESET_B(rst_n),
        .Q(net_436),
        .CLK(net_1588),
        .D(net_1799)
    );

    sky130_fd_sc_hd__o22ai cell_204 (
        .B1(net_677),
        .B2(net_579),
        .A1(net_377),
        .A2(net_523),
        .Y(net_646)
    );

    sky130_fd_sc_hd__o311a cell_205 (
        .A1(net_323),
        .A2(net_1510),
        .A3(net_1531),
        .C1(net_1527),
        .B1(net_1825),
        .X(net_1581)
    );

    sky130_fd_sc_hd__a21o cell_215 (
        .A2(net_1688),
        .B1(net_378),
        .A1(net_436),
        .X(net_1527)
    );

    sky130_fd_sc_hd__nand3 cell_216 (
        .C(net_1688),
        .A(net_436),
        .B(net_378),
        .Y(net_1825)
    );

    sky130_fd_sc_hd__a21o cell_224 (
        .A2(net_558),
        .B1(net_1006),
        .A1(net_462),
        .X(net_561)
    );

    sky130_fd_sc_hd__a21o cell_228 (
        .A2(net_574),
        .B1(net_694),
        .A1(net_606),
        .X(net_773)
    );

    sky130_fd_sc_hd__and4 cell_249 (
        .C(net_377),
        .B(net_934),
        .D(net_323),
        .A(net_1526),
        .X(net_1688)
    );

    sky130_fd_sc_hd__nand3b cell_250 (
        .C(net_377),
        .B(net_378),
        .A_N(net_436),
        .Y(net_1510)
    );

    sky130_fd_sc_hd__nand2b cell_276 (
        .B(net_639),
        .A_N(net_606),
        .Y(net_873)
    );

    sky130_fd_sc_hd__and2b cell_317 (
        .A_N(net_382),
        .B(net_646),
        .X(net_531)
    );

    sky130_fd_sc_hd__xnor2 cell_347 (
        .B(net_378),
        .A(net_377),
        .Y(net_653)
    );

    sky130_fd_sc_hd__xnor2 cell_351 (
        .B(net_639),
        .A(net_606),
        .Y(net_828)
    );

    sky130_fd_sc_hd__xnor2 cell_368 (
        .B(net_565),
        .A(net_659),
        .Y(net_466)
    );

    sky130_fd_sc_hd__xnor2 cell_369 (
        .B(net_828),
        .A(net_832),
        .Y(net_659)
    );

    sky130_fd_sc_hd__or3 cell_401 (
        .B(net_574),
        .A(net_878),
        .C(net_695),
        .X(net_874)
    );

    sky130_fd_sc_hd__and4bb cell_405 (
        .A_N(net_323),
        .B_N(net_377),
        .D(net_378),
        .C(net_436),
        .X(net_382)
    );

    sky130_fd_sc_hd__xor2 cell_416 (
        .A(net_323),
        .B(net_436),
        .X(net_510)
    );

    sky130_fd_sc_hd__xor2 cell_419 (
        .A(net_378),
        .B(net_510),
        .X(net_639)
    );

    sky130_fd_sc_hd__xor2 cell_424 (
        .A(net_436),
        .B(net_1688),
        .X(net_1799)
    );

    sky130_fd_sc_hd__a31o cell_430 (
        .A2(net_436),
        .A1(net_377),
        .B1(net_574),
        .A3(net_378),
        .X(net_579)
    );

    sky130_fd_sc_hd__o2bb2a cell_432 (
        .B1(net_445),
        .A1_N(net_380),
        .B2(net_436),
        .A2_N(net_357),
        .X(net_565)
    );

    sky130_fd_sc_hd__a31o cell_434 (
        .A2(net_934),
        .A1(net_1526),
        .B1(net_377),
        .A3(net_323),
        .X(net_1663)
    );

    sky130_fd_sc_hd__a21oi cell_455 (
        .A1(net_873),
        .A2(net_987),
        .B1(net_874),
        .Y(net_1006)
    );

    sky130_fd_sc_hd__a21oi cell_462 (
        .A1(net_377),
        .A2(net_378),
        .B1(net_436),
        .Y(net_677)
    );

    sky130_fd_sc_hd__a21oi cell_466 (
        .A1(net_561),
        .A2(net_646),
        .B1(net_382),
        .Y(net_772)
    );

    sky130_fd_sc_hd__a21oi cell_468 (
        .A1(net_377),
        .A2(net_510),
        .B1(net_325),
        .Y(net_357)
    );

    sky130_fd_sc_hd__a21oi cell_472 (
        .A1(net_378),
        .A2(net_606),
        .B1(net_574),
        .Y(net_694)
    );

    sky130_fd_sc_hd__o211a cell_479 (
        .A1(net_1510),
        .C1(net_1773),
        .B1(net_1663),
        .A2(net_1531),
        .X(net_1700)
    );

    sky130_fd_sc_hd__o211a cell_485 (
        .A1(net_323),
        .C1(net_378),
        .B1(net_436),
        .A2(net_377),
        .X(net_379)
    );

    sky130_fd_sc_hd__and3 cell_492 (
        .C(net_1510),
        .A(net_1526),
        .B(net_934),
        .X(net_1528)
    );

    sky130_fd_sc_hd__and3 cell_499 (
        .C(net_874),
        .A(net_873),
        .B(net_987),
        .X(net_1038)
    );

    sky130_fd_sc_hd__and3 cell_510 (
        .C(net_653),
        .A(net_652),
        .B(net_523),
        .X(net_695)
    );

    sky130_fd_sc_hd__mux2 cell_529 (
        .A1(net_1531),
        .A0(net_1528),
        .X(net_1554),
        .S(net_323)
    );

    sky130_fd_sc_hd__inv cell_780 (
        .A(net_1688),
        .Y(net_1773)
    );

    sky130_fd_sc_hd__nand2 cell_1510 (
        .A(net_832),
        .B(net_828),
        .Y(net_987)
    );

    sky130_fd_sc_hd__nand2 cell_1516 (
        .A(net_1526),
        .B(net_934),
        .Y(net_1531)
    );

    sky130_fd_sc_hd__nand2 cell_1518 (
        .A(net_378),
        .B(net_510),
        .Y(net_523)
    );

    sky130_fd_sc_hd__nand2 cell_1522 (
        .A(net_323),
        .B(net_436),
        .Y(net_652)
    );

    sky130_fd_sc_hd__nand2 cell_1524 (
        .A(net_377),
        .B(net_436),
        .Y(net_606)
    );

    sky130_fd_sc_hd__nand2 cell_1531 (
        .A(net_659),
        .B(net_565),
        .Y(net_456)
    );

    sky130_fd_sc_hd__nand2 cell_1541 (
        .A(net_323),
        .B(net_377),
        .Y(net_445)
    );

    sky130_fd_sc_hd__nor2 cell_1571 (
        .A(net_652),
        .B(net_653),
        .Y(net_574)
    );

    sky130_fd_sc_hd__nor2 cell_1574 (
        .A(net_377),
        .B(net_523),
        .Y(net_878)
    );

    sky130_fd_sc_hd__a21o cell_1575 (
        .A2(net_456),
        .B1(net_454),
        .A1(net_270),
        .X(net_462)
    );

    sky130_fd_sc_hd__nor2 cell_1580 (
        .A(net_1006),
        .B(net_1038),
        .Y(net_558)
    );

    sky130_fd_sc_hd__nor2 cell_1589 (
        .A(net_377),
        .B(net_436),
        .Y(net_325)
    );

    sky130_fd_sc_hd__nor2 cell_1593 (
        .A(net_659),
        .B(net_565),
        .Y(net_454)
    );

    sky130_fd_sc_hd__nor2 cell_1598 (
        .A(net_772),
        .B(net_773),
        .Y(net_1170)
    );

    sky130_fd_sc_hd__nor2 cell_1601 (
        .A(net_323),
        .B(net_1510),
        .Y(net_1508)
    );

endmodule

module puzzle__inferred_block_7 (
    input wire I,
    output wire net_612,
    output wire net_684,
    output wire net_686,
    input wire net_715,
    output wire net_716,
    output wire net_719,
    input wire net_771,
    output wire net_888,
    input wire net_934,
    output wire net_1029,
    output wire net_1076,
    input wire rst_n
);
    wire net_519;
    wire net_548;
    wire net_648;
    wire net_683;
    wire net_718;
    wire net_769;
    wire net_795;
    wire net_800;
    wire net_802;
    wire net_803;
    wire net_842;
    wire net_887;
    wire net_919;
    wire net_923;
    wire net_971;
    wire net_977;
    wire net_979;
    wire net_982;
    wire net_1022;
    wire net_1028;
    wire net_1062;
    wire net_1068;
    wire net_1104;
    wire net_1136;
    wire net_1138;

    sky130_fd_sc_hd__diode cell_69 (
        .DIODE(net_719)
    );

    sky130_fd_sc_hd__diode cell_71 (
        .DIODE(net_719)
    );

    sky130_fd_sc_hd__diode cell_74 (
        .DIODE(net_719)
    );

    sky130_fd_sc_hd__dfrtp cell_118 (
        .RESET_B(rst_n),
        .Q(net_684),
        .CLK(net_715),
        .D(net_683)
    );

    sky130_fd_sc_hd__dfrtp cell_122 (
        .RESET_B(rst_n),
        .Q(net_1104),
        .CLK(net_715),
        .D(net_1022)
    );

    sky130_fd_sc_hd__dfrtp cell_146 (
        .RESET_B(rst_n),
        .Q(net_919),
        .CLK(net_771),
        .D(net_979)
    );

    sky130_fd_sc_hd__dfrtp cell_156 (
        .RESET_B(rst_n),
        .Q(net_769),
        .CLK(net_771),
        .D(net_718)
    );

    sky130_fd_sc_hd__dfrtp cell_165 (
        .RESET_B(rst_n),
        .Q(net_982),
        .CLK(net_715),
        .D(net_1068)
    );

    sky130_fd_sc_hd__dfrtp cell_181 (
        .RESET_B(rst_n),
        .Q(net_802),
        .CLK(net_771),
        .D(net_923)
    );

    sky130_fd_sc_hd__dfrtp cell_183 (
        .RESET_B(rst_n),
        .Q(net_686),
        .CLK(net_771),
        .D(net_842)
    );

    sky130_fd_sc_hd__a21o cell_225 (
        .A2(net_803),
        .B1(net_686),
        .A1(net_684),
        .X(net_519)
    );

    sky130_fd_sc_hd__and4bb cell_234 (
        .A_N(net_686),
        .B_N(net_982),
        .D(net_802),
        .C(net_919),
        .X(net_1029)
    );

    sky130_fd_sc_hd__and4 cell_251 (
        .C(net_803),
        .B(net_888),
        .D(net_971),
        .A(net_919),
        .X(net_1028)
    );

    sky130_fd_sc_hd__and4 cell_255 (
        .C(net_612),
        .B(net_686),
        .D(net_716),
        .A(net_684),
        .X(net_719)
    );

    sky130_fd_sc_hd__and2b cell_311 (
        .A_N(net_684),
        .B(net_1104),
        .X(net_1076)
    );

    sky130_fd_sc_hd__and2b cell_316 (
        .A_N(net_1028),
        .B(net_1138),
        .X(net_979)
    );

    sky130_fd_sc_hd__and2b cell_333 (
        .A_N(net_548),
        .B(net_519),
        .X(net_842)
    );

    sky130_fd_sc_hd__dfrtp cell_334 (
        .RESET_B(rst_n),
        .Q(net_612),
        .CLK(net_771),
        .D(net_648)
    );

    sky130_fd_sc_hd__a32o cell_338 (
        .A1(I),
        .A3(net_1076),
        .B2(net_684),
        .B1(net_887),
        .A2(net_934),
        .X(net_683)
    );

    sky130_fd_sc_hd__xnor2 cell_372 (
        .B(net_800),
        .A(net_612),
        .Y(net_648)
    );

    sky130_fd_sc_hd__or3 cell_386 (
        .B(net_802),
        .A(net_1104),
        .C(net_982),
        .X(net_1136)
    );

    sky130_fd_sc_hd__xor2 cell_408 (
        .A(net_982),
        .B(net_1028),
        .X(net_1068)
    );

    sky130_fd_sc_hd__a31o cell_427 (
        .A2(net_803),
        .A1(net_612),
        .B1(net_769),
        .A3(net_971),
        .X(net_977)
    );

    sky130_fd_sc_hd__a31o cell_438 (
        .A2(net_803),
        .A1(net_888),
        .B1(net_919),
        .A3(net_971),
        .X(net_1138)
    );

    sky130_fd_sc_hd__a21oi cell_457 (
        .A1(I),
        .A2(net_934),
        .B1(net_1104),
        .Y(net_1062)
    );

    sky130_fd_sc_hd__and3 cell_486 (
        .C(net_934),
        .A(net_1104),
        .B(I),
        .X(net_803)
    );

    sky130_fd_sc_hd__and3 cell_489 (
        .C(net_802),
        .A(net_684),
        .B(net_686),
        .X(net_971)
    );

    sky130_fd_sc_hd__and3 cell_501 (
        .C(net_803),
        .A(net_684),
        .B(net_686),
        .X(net_548)
    );

    sky130_fd_sc_hd__nor3 cell_502 (
        .A(net_769),
        .B(net_919),
        .C(net_1136),
        .Y(net_716)
    );

    sky130_fd_sc_hd__o21a cell_757 (
        .B1(net_977),
        .A2(net_800),
        .A1(net_795),
        .X(net_718)
    );

    sky130_fd_sc_hd__o21a cell_772 (
        .B1(net_800),
        .A2(net_548),
        .A1(net_802),
        .X(net_923)
    );

    sky130_fd_sc_hd__inv cell_795 (
        .A(net_803),
        .Y(net_887)
    );

    sky130_fd_sc_hd__and2 cell_806 (
        .A(net_612),
        .B(net_769),
        .X(net_888)
    );

    sky130_fd_sc_hd__nand2 cell_1530 (
        .A(net_803),
        .B(net_971),
        .Y(net_800)
    );

    sky130_fd_sc_hd__nand2 cell_1538 (
        .A(net_612),
        .B(net_769),
        .Y(net_795)
    );

    sky130_fd_sc_hd__nor2 cell_1610 (
        .A(net_803),
        .B(net_1062),
        .Y(net_1022)
    );

endmodule

module puzzle__inferred_block_8 (
    input wire I,
    input wire net_934,
    input wire net_2275,
    output wire net_2545,
    input wire net_2985,
    input wire net_3101,
    input wire net_3145,
    input wire net_3247,
    input wire net_3249,
    input wire net_3502,
    input wire rst_n
);
    wire net_2416;
    wire net_2474;
    wire net_2480;
    wire net_2818;
    wire net_2819;
    wire net_2821;
    wire net_2880;
    wire net_2923;
    wire net_2924;
    wire net_3139;
    wire net_3142;
    wire net_3143;
    wire net_3144;
    wire net_3146;
    wire net_3148;
    wire net_3207;
    wire net_3223;
    wire net_3283;
    wire net_3320;
    wire net_3323;
    wire net_3325;
    wire net_3326;
    wire net_3369;
    wire net_3370;
    wire net_3378;
    wire net_3414;
    wire net_3462;
    wire net_3470;
    wire net_3471;
    wire net_3496;
    wire net_3561;
    wire net_3628;

    sky130_fd_sc_hd__nand4 cell_90 (
        .A(I),
        .B(net_934),
        .D(net_2985),
        .C(net_2923),
        .Y(net_2821)
    );

    sky130_fd_sc_hd__nand4 cell_97 (
        .A(I),
        .B(net_934),
        .D(net_3502),
        .C(net_3470),
        .Y(net_3496)
    );

    sky130_fd_sc_hd__dfrtp cell_126 (
        .RESET_B(rst_n),
        .Q(net_3320),
        .CLK(net_3101),
        .D(net_3370)
    );

    sky130_fd_sc_hd__dfrtp cell_136 (
        .RESET_B(rst_n),
        .Q(net_3326),
        .CLK(net_3247),
        .D(net_3378)
    );

    sky130_fd_sc_hd__dfrtp cell_139 (
        .RESET_B(rst_n),
        .Q(net_2818),
        .CLK(net_2275),
        .D(net_2819)
    );

    sky130_fd_sc_hd__dfrtp cell_149 (
        .RESET_B(rst_n),
        .Q(net_3471),
        .CLK(net_3247),
        .D(net_3462)
    );

    sky130_fd_sc_hd__dfrtp cell_155 (
        .RESET_B(rst_n),
        .Q(net_3148),
        .CLK(net_3101),
        .D(net_3223)
    );

    sky130_fd_sc_hd__dfrtp cell_187 (
        .RESET_B(rst_n),
        .Q(net_3139),
        .CLK(net_3101),
        .D(net_3146)
    );

    sky130_fd_sc_hd__dfrtp cell_190 (
        .RESET_B(rst_n),
        .Q(net_2923),
        .CLK(net_2275),
        .D(net_2880)
    );

    sky130_fd_sc_hd__dfrtp cell_196 (
        .RESET_B(rst_n),
        .Q(net_3470),
        .CLK(net_3247),
        .D(net_3628)
    );

    sky130_fd_sc_hd__a21o cell_210 (
        .A2(net_3142),
        .B1(net_3148),
        .A1(net_3139),
        .X(net_3223)
    );

    sky130_fd_sc_hd__a21o cell_212 (
        .A2(net_3323),
        .B1(net_3326),
        .A1(net_3320),
        .X(net_3378)
    );

    sky130_fd_sc_hd__and4 cell_253 (
        .C(net_2480),
        .B(net_2416),
        .D(net_2474),
        .A(net_3283),
        .X(net_2545)
    );

    sky130_fd_sc_hd__nand2b cell_256 (
        .B(net_3496),
        .A_N(net_3471),
        .Y(net_3462)
    );

    sky130_fd_sc_hd__nand2b cell_263 (
        .B(net_2821),
        .A_N(net_2818),
        .Y(net_2819)
    );

    sky130_fd_sc_hd__and2b cell_304 (
        .A_N(net_3470),
        .B(net_3471),
        .X(net_2480)
    );

    sky130_fd_sc_hd__and2b cell_322 (
        .A_N(net_2923),
        .B(net_2818),
        .X(net_2416)
    );

    sky130_fd_sc_hd__or4 cell_380 (
        .D(net_3144),
        .C(net_3145),
        .B(net_3207),
        .A(net_3148),
        .X(net_3143)
    );

    sky130_fd_sc_hd__or4 cell_384 (
        .D(net_3325),
        .C(net_3249),
        .B(net_3414),
        .A(net_3326),
        .X(net_3369)
    );

    sky130_fd_sc_hd__a31o cell_437 (
        .A2(net_934),
        .A1(I),
        .B1(net_3470),
        .A3(net_3502),
        .X(net_3561)
    );

    sky130_fd_sc_hd__a31o cell_454 (
        .A2(net_934),
        .A1(I),
        .B1(net_2923),
        .A3(net_2985),
        .X(net_2924)
    );

    sky130_fd_sc_hd__o21a cell_744 (
        .B1(net_3143),
        .A2(net_3142),
        .A1(net_3139),
        .X(net_3146)
    );

    sky130_fd_sc_hd__o21a cell_746 (
        .B1(net_3561),
        .A2(net_3496),
        .A1(net_3471),
        .X(net_3628)
    );

    sky130_fd_sc_hd__o21a cell_756 (
        .B1(net_2924),
        .A2(net_2821),
        .A1(net_2818),
        .X(net_2880)
    );

    sky130_fd_sc_hd__o21a cell_761 (
        .B1(net_3369),
        .A2(net_3323),
        .A1(net_3320),
        .X(net_3370)
    );

    sky130_fd_sc_hd__inv cell_787 (
        .A(net_3139),
        .Y(net_3207)
    );

    sky130_fd_sc_hd__inv cell_788 (
        .A(net_3320),
        .Y(net_3414)
    );

    sky130_fd_sc_hd__and2 cell_803 (
        .A(net_3148),
        .B(net_3207),
        .X(net_3283)
    );

    sky130_fd_sc_hd__and2 cell_817 (
        .A(net_3326),
        .B(net_3414),
        .X(net_2474)
    );

    sky130_fd_sc_hd__nand2 cell_1529 (
        .A(I),
        .B(net_934),
        .Y(net_3144)
    );

    sky130_fd_sc_hd__nand2 cell_1535 (
        .A(I),
        .B(net_934),
        .Y(net_3325)
    );

    sky130_fd_sc_hd__nor2 cell_1594 (
        .A(net_3145),
        .B(net_3144),
        .Y(net_3142)
    );

    sky130_fd_sc_hd__nor2 cell_1596 (
        .A(net_3249),
        .B(net_3325),
        .Y(net_3323)
    );

endmodule

module puzzle__inferred_block_9 (
    input wire I,
    input wire net_934,
    input wire net_2467,
    output wire net_2505,
    input wire net_2545,
    input wire net_3799,
    input wire net_3842,
    input wire net_4122,
    input wire net_4229,
    input wire net_4325,
    input wire rst_n
);
    wire net_2386;
    wire net_2415;
    wire net_2459;
    wire net_2463;
    wire net_4127;
    wire net_4147;
    wire net_4155;
    wire net_4158;
    wire net_4159;
    wire net_4160;
    wire net_4162;
    wire net_4163;
    wire net_4178;
    wire net_4193;
    wire net_4195;
    wire net_4199;
    wire net_4231;
    wire net_4251;
    wire net_4274;
    wire net_4276;
    wire net_4300;
    wire net_4304;
    wire net_4322;
    wire net_4331;

    sky130_fd_sc_hd__nand4 cell_89 (
        .A(I),
        .B(net_934),
        .D(net_4229),
        .C(net_4199),
        .Y(net_4195)
    );

    sky130_fd_sc_hd__nand4 cell_95 (
        .A(I),
        .B(net_934),
        .D(net_4325),
        .C(net_4274),
        .Y(net_4331)
    );

    sky130_fd_sc_hd__dfrtp cell_147 (
        .RESET_B(rst_n),
        .Q(net_4147),
        .CLK(net_3842),
        .D(net_4159)
    );

    sky130_fd_sc_hd__dfrtp cell_168 (
        .RESET_B(rst_n),
        .Q(net_4160),
        .CLK(net_3799),
        .D(net_4193)
    );

    sky130_fd_sc_hd__dfrtp cell_169 (
        .RESET_B(rst_n),
        .Q(net_4300),
        .CLK(net_3799),
        .D(net_4304)
    );

    sky130_fd_sc_hd__dfrtp cell_186 (
        .RESET_B(rst_n),
        .Q(net_4163),
        .CLK(net_3842),
        .D(net_4162)
    );

    sky130_fd_sc_hd__dfrtp cell_197 (
        .RESET_B(rst_n),
        .Q(net_4274),
        .CLK(net_3842),
        .D(net_4276)
    );

    sky130_fd_sc_hd__dfrtp cell_198 (
        .RESET_B(rst_n),
        .Q(net_4199),
        .CLK(net_3842),
        .D(net_4231)
    );

    sky130_fd_sc_hd__a21o cell_222 (
        .A2(net_4155),
        .B1(net_4160),
        .A1(net_4147),
        .X(net_4193)
    );

    sky130_fd_sc_hd__nand2b cell_259 (
        .B(net_4195),
        .A_N(net_4163),
        .Y(net_4162)
    );

    sky130_fd_sc_hd__nand2b cell_279 (
        .B(net_4331),
        .A_N(net_4300),
        .Y(net_4304)
    );

    sky130_fd_sc_hd__and2b cell_309 (
        .A_N(net_4274),
        .B(net_4300),
        .X(net_2386)
    );

    sky130_fd_sc_hd__and2b cell_328 (
        .A_N(net_4199),
        .B(net_4163),
        .X(net_2463)
    );

    sky130_fd_sc_hd__or4 cell_374 (
        .D(net_4158),
        .C(net_4122),
        .B(net_4178),
        .A(net_4160),
        .X(net_4127)
    );

    sky130_fd_sc_hd__a31o cell_436 (
        .A2(net_934),
        .A1(I),
        .B1(net_4199),
        .A3(net_4229),
        .X(net_4251)
    );

    sky130_fd_sc_hd__a31o cell_443 (
        .A2(net_934),
        .A1(I),
        .B1(net_4274),
        .A3(net_4325),
        .X(net_4322)
    );

    sky130_fd_sc_hd__and3 cell_490 (
        .C(net_2386),
        .A(net_2463),
        .B(net_2459),
        .X(net_2415)
    );

    sky130_fd_sc_hd__and3 cell_505 (
        .C(net_2415),
        .A(net_2467),
        .B(net_2545),
        .X(net_2505)
    );

    sky130_fd_sc_hd__o21a cell_755 (
        .B1(net_4322),
        .A2(net_4331),
        .A1(net_4300),
        .X(net_4276)
    );

    sky130_fd_sc_hd__o21a cell_759 (
        .B1(net_4127),
        .A2(net_4155),
        .A1(net_4147),
        .X(net_4159)
    );

    sky130_fd_sc_hd__o21a cell_765 (
        .B1(net_4251),
        .A2(net_4195),
        .A1(net_4163),
        .X(net_4231)
    );

    sky130_fd_sc_hd__inv cell_791 (
        .A(net_4147),
        .Y(net_4178)
    );

    sky130_fd_sc_hd__and2 cell_807 (
        .A(net_4160),
        .B(net_4178),
        .X(net_2459)
    );

    sky130_fd_sc_hd__nand2 cell_1512 (
        .A(I),
        .B(net_934),
        .Y(net_4158)
    );

    sky130_fd_sc_hd__nor2 cell_1607 (
        .A(net_4122),
        .B(net_4158),
        .Y(net_4155)
    );

endmodule

module puzzle__inferred_block_10 (
    input wire I,
    input wire net_934,
    input wire net_1526,
    output wire net_1558,
    input wire net_1588,
    input wire rst_n
);
    wire net_1495;
    wire net_1568;
    wire net_1587;
    wire net_1628;
    wire net_1639;
    wire net_1668;
    wire net_1669;
    wire net_1705;
    wire net_1706;
    wire net_1714;
    wire net_1719;
    wire net_1734;
    wire net_1735;
    wire net_1785;

    sky130_fd_sc_hd__dfrtp cell_172 (
        .RESET_B(rst_n),
        .Q(net_1495),
        .CLK(net_1588),
        .D(net_1568)
    );

    sky130_fd_sc_hd__dfrtp cell_176 (
        .RESET_B(rst_n),
        .Q(net_1735),
        .CLK(net_1588),
        .D(net_1785)
    );

    sky130_fd_sc_hd__dfrtp cell_177 (
        .RESET_B(rst_n),
        .Q(net_1639),
        .CLK(net_1588),
        .D(net_1587)
    );

    sky130_fd_sc_hd__a22o cell_302 (
        .B2(net_1628),
        .B1(net_1734),
        .A1(net_1668),
        .A2(net_1735),
        .X(net_1785)
    );

    sky130_fd_sc_hd__a31o cell_444 (
        .A2(net_934),
        .A1(net_1526),
        .B1(net_1495),
        .A3(net_1714),
        .X(net_1568)
    );

    sky130_fd_sc_hd__a21oi cell_458 (
        .A1(net_1706),
        .A2(net_1669),
        .B1(net_1705),
        .Y(net_1587)
    );

    sky130_fd_sc_hd__o211a cell_484 (
        .A1(net_1639),
        .C1(net_934),
        .B1(net_1719),
        .A2(net_1669),
        .X(net_1734)
    );

    sky130_fd_sc_hd__mux2 cell_522 (
        .A1(net_1706),
        .A0(net_1526),
        .X(net_1705),
        .S(net_1668)
    );

    sky130_fd_sc_hd__mux2 cell_524 (
        .A1(net_1719),
        .A0(net_1669),
        .X(net_1714),
        .S(net_1639)
    );

    sky130_fd_sc_hd__inv cell_778 (
        .A(net_1495),
        .Y(net_1558)
    );

    sky130_fd_sc_hd__inv cell_790 (
        .A(net_1526),
        .Y(net_1628)
    );

    sky130_fd_sc_hd__inv cell_793 (
        .A(net_1639),
        .Y(net_1706)
    );

    sky130_fd_sc_hd__inv cell_796 (
        .A(net_934),
        .Y(net_1668)
    );

    sky130_fd_sc_hd__nand2 cell_1544 (
        .A(net_1735),
        .B(I),
        .Y(net_1669)
    );

    sky130_fd_sc_hd__or2 cell_1561 (
        .A(net_1735),
        .B(I),
        .X(net_1719)
    );

endmodule

module puzzle (
    input wire rst_n,
    input wire enable,
    output wire success,
    input wire I,
    input wire clk,
    output wire [7:0] O
);

    wire net_20;
    wire net_39;
    wire net_165;
    wire net_242;
    wire net_270;
    wire net_292;
    wire net_319;
    wire net_323;
    wire net_343;
    wire net_357;
    wire net_377;
    wire net_379;
    wire net_380;
    wire net_462;
    wire net_466;
    wire net_531;
    wire net_536;
    wire net_550;
    wire net_558;
    wire net_561;
    wire net_612;
    wire net_663;
    wire net_684;
    wire net_686;
    wire net_704;
    wire net_705;
    wire net_715;
    wire net_716;
    wire net_719;
    wire net_771;
    wire net_772;
    wire net_773;
    wire net_779;
    wire net_832;
    wire net_869;
    wire net_870;
    wire net_888;
    wire net_905;
    wire net_934;
    wire net_945;
    wire net_984;
    wire net_1029;
    wire net_1076;
    wire net_1170;
    wire net_1285;
    wire net_1351;
    wire net_1419;
    wire net_1441;
    wire net_1472;
    wire net_1508;
    wire net_1516;
    wire net_1526;
    wire net_1558;
    wire net_1559;
    wire net_1588;
    wire net_1629;
    wire net_1693;
    wire net_1694;
    wire net_1816;
    wire net_1822;
    wire net_1855;
    wire net_1906;
    wire net_1907;
    wire net_1927;
    wire net_1928;
    wire net_1936;
    wire net_1978;
    wire net_2008;
    wire net_2086;
    wire net_2088;
    wire net_2119;
    wire net_2120;
    wire net_2140;
    wire net_2141;
    wire net_2154;
    wire net_2189;
    wire net_2213;
    wire net_2231;
    wire net_2270;
    wire net_2275;
    wire net_2298;
    wire net_2313;
    wire net_2315;
    wire net_2388;
    wire net_2422;
    wire net_2460;
    wire net_2462;
    wire net_2467;
    wire net_2505;
    wire net_2515;
    wire net_2545;
    wire net_2606;
    wire net_2607;
    wire net_2637;
    wire net_2652;
    wire net_2674;
    wire net_2676;
    wire net_2684;
    wire net_2689;
    wire net_2700;
    wire net_2706;
    wire net_2722;
    wire net_2746;
    wire net_2752;
    wire net_2825;
    wire net_2887;
    wire net_2892;
    wire net_2905;
    wire net_2949;
    wire net_2985;
    wire net_3101;
    wire net_3136;
    wire net_3145;
    wire net_3190;
    wire net_3247;
    wire net_3249;
    wire net_3293;
    wire net_3502;
    wire net_3591;
    wire net_3771;
    wire net_3799;
    wire net_3842;
    wire net_3874;
    wire net_3922;
    wire net_4122;
    wire net_4229;
    wire net_4325;

    puzzle__inferred_block_0 inferred_block_0 (
        .I(I),
        .net_39(net_39),
        .net_165(net_165),
        .net_242(net_242),
        .net_292(net_292),
        .net_343(net_343),
        .net_379(net_379),
        .net_536(net_536),
        .net_550(net_550),
        .net_663(net_663),
        .net_704(net_704),
        .net_705(net_705),
        .net_715(net_715),
        .net_772(net_772),
        .net_773(net_773),
        .net_779(net_779),
        .net_869(net_869),
        .net_870(net_870),
        .net_905(net_905),
        .net_934(net_934),
        .net_945(net_945),
        .net_984(net_984),
        .net_1170(net_1170),
        .net_1441(net_1441),
        .net_1855(net_1855),
        .net_2086(net_2086),
        .net_2275(net_2275),
        .net_2515(net_2515),
        .net_2606(net_2606),
        .net_2700(net_2700),
        .net_2887(net_2887),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_1 inferred_block_1 (
        .net_1351(net_1351),
        .net_1419(net_1419),
        .net_1472(net_1472),
        .net_1516(net_1516),
        .net_1559(net_1559),
        .net_1629(net_1629),
        .net_1693(net_1693),
        .net_1694(net_1694),
        .net_1816(net_1816),
        .net_1822(net_1822),
        .net_1906(net_1906),
        .net_1907(net_1907),
        .net_1927(net_1927),
        .net_1928(net_1928),
        .net_1936(net_1936),
        .net_1978(net_1978),
        .net_2008(net_2008),
        .net_2088(net_2088),
        .net_2119(net_2119),
        .net_2120(net_2120),
        .net_2154(net_2154),
        .net_2189(net_2189),
        .net_2231(net_2231),
        .net_2298(net_2298),
        .net_2313(net_2313),
        .net_2315(net_2315),
        .net_2460(net_2460),
        .net_2462(net_2462),
        .net_2637(net_2637),
        .net_2652(net_2652),
        .net_2674(net_2674),
        .net_2676(net_2676),
        .net_2684(net_2684),
        .net_2689(net_2689),
        .net_2706(net_2706),
        .net_2752(net_2752),
        .net_2825(net_2825),
        .net_2892(net_2892),
        .net_2905(net_2905),
        .net_2949(net_2949),
        .net_3101(net_3101),
        .net_3190(net_3190),
        .net_3293(net_3293),
        .net_3591(net_3591),
        .net_3771(net_3771),
        .net_3874(net_3874),
        .net_3922(net_3922)
    );

    puzzle__inferred_block_2 inferred_block_2 (
        .net_20(net_20),
        .net_39(net_39),
        .net_165(net_165),
        .net_242(net_242),
        .net_270(net_270),
        .net_292(net_292),
        .net_319(net_319),
        .net_323(net_323),
        .net_357(net_357),
        .net_377(net_377),
        .net_380(net_380),
        .net_462(net_462),
        .net_466(net_466),
        .net_531(net_531),
        .net_536(net_536),
        .net_550(net_550),
        .net_558(net_558),
        .net_561(net_561),
        .net_663(net_663),
        .net_704(net_704),
        .net_705(net_705),
        .net_772(net_772),
        .net_773(net_773),
        .net_779(net_779),
        .net_869(net_869),
        .net_870(net_870),
        .net_905(net_905),
        .net_945(net_945)
    );

    puzzle__inferred_block_3 inferred_block_3 (
        .I(I),
        .O_0(O[0]),
        .O_1(O[1]),
        .O_2(O[2]),
        .O_3(O[3]),
        .O_4(O[4]),
        .O_5(O[5]),
        .O_6(O[6]),
        .O_7(O[7]),
        .net_343(net_343),
        .net_612(net_612),
        .net_684(net_684),
        .net_686(net_686),
        .net_716(net_716),
        .net_719(net_719),
        .net_888(net_888),
        .net_934(net_934),
        .net_1029(net_1029),
        .net_1076(net_1076),
        .net_1351(net_1351),
        .net_1419(net_1419),
        .net_1472(net_1472),
        .net_1508(net_1508),
        .net_1516(net_1516),
        .net_1526(net_1526),
        .net_1558(net_1558),
        .net_1559(net_1559),
        .net_1629(net_1629),
        .net_1693(net_1693),
        .net_1694(net_1694),
        .net_1816(net_1816),
        .net_1822(net_1822),
        .net_1906(net_1906),
        .net_1907(net_1907),
        .net_1927(net_1927),
        .net_1928(net_1928),
        .net_1936(net_1936),
        .net_1978(net_1978),
        .net_2008(net_2008),
        .net_2088(net_2088),
        .net_2119(net_2119),
        .net_2120(net_2120),
        .net_2154(net_2154),
        .net_2189(net_2189),
        .net_2231(net_2231),
        .net_2270(net_2270),
        .net_2275(net_2275),
        .net_2298(net_2298),
        .net_2313(net_2313),
        .net_2315(net_2315),
        .net_2388(net_2388),
        .net_2460(net_2460),
        .net_2462(net_2462),
        .net_2505(net_2505),
        .net_2607(net_2607),
        .net_2684(net_2684),
        .net_2706(net_2706),
        .net_2746(net_2746),
        .net_2892(net_2892),
        .net_2905(net_2905),
        .net_3136(net_3136),
        .net_3190(net_3190),
        .net_3293(net_3293),
        .net_3591(net_3591),
        .net_3771(net_3771),
        .net_3874(net_3874),
        .net_3922(net_3922),
        .rst_n(rst_n),
        .success(success)
    );

    puzzle__inferred_block_4 inferred_block_4 (
        .I(I),
        .enable(enable),
        .net_934(net_934),
        .net_1855(net_1855),
        .net_2086(net_2086),
        .net_2140(net_2140),
        .net_2141(net_2141),
        .net_2213(net_2213),
        .net_2270(net_2270),
        .net_2275(net_2275),
        .net_2422(net_2422),
        .net_2515(net_2515),
        .net_2606(net_2606),
        .net_2607(net_2607),
        .net_2637(net_2637),
        .net_2652(net_2652),
        .net_2674(net_2674),
        .net_2676(net_2676),
        .net_2689(net_2689),
        .net_2700(net_2700),
        .net_2722(net_2722),
        .net_2746(net_2746),
        .net_2752(net_2752),
        .net_2825(net_2825),
        .net_2887(net_2887),
        .net_2949(net_2949),
        .net_3101(net_3101),
        .net_3136(net_3136),
        .net_3771(net_3771),
        .net_3874(net_3874),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_5 inferred_block_5 (
        .I(I),
        .net_20(net_20),
        .net_319(net_319),
        .net_380(net_380),
        .net_832(net_832),
        .net_934(net_934),
        .net_1526(net_1526),
        .net_1855(net_1855),
        .net_2140(net_2140),
        .net_2141(net_2141),
        .net_2213(net_2213),
        .net_2270(net_2270),
        .net_2388(net_2388),
        .net_2422(net_2422),
        .net_2467(net_2467),
        .net_2985(net_2985),
        .net_3145(net_3145),
        .net_3247(net_3247),
        .net_3249(net_3249),
        .net_3502(net_3502),
        .net_3799(net_3799),
        .net_3842(net_3842),
        .net_4122(net_4122),
        .net_4229(net_4229),
        .net_4325(net_4325),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_6 inferred_block_6 (
        .net_270(net_270),
        .net_323(net_323),
        .net_357(net_357),
        .net_377(net_377),
        .net_379(net_379),
        .net_380(net_380),
        .net_462(net_462),
        .net_466(net_466),
        .net_531(net_531),
        .net_558(net_558),
        .net_561(net_561),
        .net_771(net_771),
        .net_772(net_772),
        .net_773(net_773),
        .net_832(net_832),
        .net_934(net_934),
        .net_1170(net_1170),
        .net_1508(net_1508),
        .net_1526(net_1526),
        .net_1588(net_1588),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_7 inferred_block_7 (
        .I(I),
        .net_612(net_612),
        .net_684(net_684),
        .net_686(net_686),
        .net_715(net_715),
        .net_716(net_716),
        .net_719(net_719),
        .net_771(net_771),
        .net_888(net_888),
        .net_934(net_934),
        .net_1029(net_1029),
        .net_1076(net_1076),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_8 inferred_block_8 (
        .I(I),
        .net_934(net_934),
        .net_2275(net_2275),
        .net_2545(net_2545),
        .net_2985(net_2985),
        .net_3101(net_3101),
        .net_3145(net_3145),
        .net_3247(net_3247),
        .net_3249(net_3249),
        .net_3502(net_3502),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_9 inferred_block_9 (
        .I(I),
        .net_934(net_934),
        .net_2467(net_2467),
        .net_2505(net_2505),
        .net_2545(net_2545),
        .net_3799(net_3799),
        .net_3842(net_3842),
        .net_4122(net_4122),
        .net_4229(net_4229),
        .net_4325(net_4325),
        .rst_n(rst_n)
    );

    puzzle__inferred_block_10 inferred_block_10 (
        .I(I),
        .net_934(net_934),
        .net_1526(net_1526),
        .net_1558(net_1558),
        .net_1588(net_1588),
        .rst_n(rst_n)
    );

    sky130_fd_sc_hd__clkbuf cell_39 (
        .A(net_1285),
        .X(net_3842)
    );

    sky130_fd_sc_hd__clkbuf cell_40 (
        .A(net_1285),
        .X(net_1855)
    );

    sky130_fd_sc_hd__clkbuf cell_41 (
        .A(net_1285),
        .X(net_2213)
    );

    sky130_fd_sc_hd__clkbuf cell_42 (
        .A(net_1285),
        .X(net_771)
    );

    sky130_fd_sc_hd__clkbuf cell_43 (
        .A(net_1285),
        .X(net_1588)
    );

    sky130_fd_sc_hd__clkbuf cell_44 (
        .A(net_1285),
        .X(net_3799)
    );

    sky130_fd_sc_hd__clkbuf cell_45 (
        .A(net_1285),
        .X(net_3247)
    );

    sky130_fd_sc_hd__clkbuf cell_46 (
        .A(net_1285),
        .X(net_2270)
    );

    sky130_fd_sc_hd__clkbuf cell_47 (
        .A(net_1285),
        .X(net_984)
    );

    sky130_fd_sc_hd__clkbuf cell_48 (
        .A(net_1285),
        .X(net_2275)
    );

    sky130_fd_sc_hd__clkbuf cell_49 (
        .A(net_1285),
        .X(net_3591)
    );

    sky130_fd_sc_hd__clkbuf cell_50 (
        .A(net_1285),
        .X(net_2086)
    );

    sky130_fd_sc_hd__clkbuf cell_51 (
        .A(net_1285),
        .X(net_1441)
    );

    sky130_fd_sc_hd__clkbuf cell_52 (
        .A(net_1285),
        .X(net_2722)
    );

    sky130_fd_sc_hd__clkbuf cell_54 (
        .A(net_1285),
        .X(net_3101)
    );

    sky130_fd_sc_hd__clkbuf cell_55 (
        .A(net_3591)
    );

    sky130_fd_sc_hd__clkbuf cell_56 (
        .A(net_3247)
    );

    sky130_fd_sc_hd__clkbuf cell_57 (
        .A(net_2270)
    );

    sky130_fd_sc_hd__clkbuf cell_58 (
        .A(net_1441)
    );

    sky130_fd_sc_hd__clkbuf cell_59 (
        .A(net_3799)
    );

    sky130_fd_sc_hd__clkbuf cell_60 (
        .A(net_984)
    );

    sky130_fd_sc_hd__clkbuf cell_61 (
        .A(net_1588)
    );

    sky130_fd_sc_hd__clkbuf cell_62 (
        .A(net_1855)
    );

    sky130_fd_sc_hd__clkbuf cell_63 (
        .A(net_2722)
    );

    sky130_fd_sc_hd__clkbuf cell_64 (
        .A(net_2275)
    );

    sky130_fd_sc_hd__clkbuf cell_65 (
        .A(net_2213)
    );

    sky130_fd_sc_hd__clkbuf cell_66 (
        .A(net_771)
    );

    sky130_fd_sc_hd__clkbuf cell_67 (
        .A(net_3842)
    );

    sky130_fd_sc_hd__clkbuf cell_68 (
        .A(net_2086)
    );

    sky130_fd_sc_hd__clkbuf cell_982 (
        .A(clk),
        .X(net_1285)
    );

    sky130_fd_sc_hd__clkbuf cell_1435 (
        .A(net_715)
    );

    sky130_fd_sc_hd__clkbuf cell_1436 (
        .A(net_1285),
        .X(net_715)
    );

endmodule
