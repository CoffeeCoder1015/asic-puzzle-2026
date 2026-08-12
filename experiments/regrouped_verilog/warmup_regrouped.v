// Experimental hierarchy inferred from graph communities.
// Standard-cell logic is unchanged; module boundaries are hypotheses.

module adder_demo__inferred_block_0 (
    input wire A,
    input wire B,
    output wire S,
    input wire en,
    output wire net_57,
    input wire net_66,
    input wire net_91,
    output wire net_123,
    input wire net_329,
    input wire net_332,
    input wire net_371,
    output wire net_471,
    input wire rst_n
);
    wire net_11;
    wire net_18;
    wire net_21;
    wire net_98;
    wire net_115;
    wire net_122;
    wire net_145;
    wire net_153;
    wire net_188;
    wire net_247;
    wire net_306;
    wire net_383;
    wire net_422;

    sky130_fd_sc_hd__mux2 cell_4 (
        .A1(A),
        .A0(net_11),
        .X(net_422),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_5 (
        .A1(net_18),
        .A0(net_123),
        .X(net_247),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_6 (
        .A1(B),
        .A0(net_18),
        .X(net_115),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_7 (
        .A1(net_122),
        .A0(net_91),
        .X(net_471),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_8 (
        .A1(net_11),
        .A0(net_122),
        .X(net_383),
        .S(en)
    );

    sky130_fd_sc_hd__dfrtp cell_30 (
        .RESET_B(rst_n),
        .Q(net_11),
        .CLK(net_371),
        .D(net_422)
    );

    sky130_fd_sc_hd__dfrtp cell_31 (
        .RESET_B(rst_n),
        .Q(net_122),
        .CLK(net_371),
        .D(net_383)
    );

    sky130_fd_sc_hd__dfrtp cell_32 (
        .RESET_B(rst_n),
        .Q(net_123),
        .CLK(net_66),
        .D(net_247)
    );

    sky130_fd_sc_hd__dfrtp cell_33 (
        .RESET_B(rst_n),
        .Q(net_18),
        .CLK(net_66),
        .D(net_115)
    );

    sky130_fd_sc_hd__nand2 cell_37 (
        .A(net_18),
        .B(net_11),
        .Y(net_188)
    );

    sky130_fd_sc_hd__xor2 cell_40 (
        .B(net_122),
        .A(net_123),
        .X(net_98)
    );

    sky130_fd_sc_hd__a31o cell_44 (
        .B1(net_145),
        .A1(net_18),
        .A2(net_11),
        .A3(net_98),
        .X(net_57)
    );

    sky130_fd_sc_hd__xnor2 cell_47 (
        .B(net_98),
        .A(net_188),
        .Y(net_153)
    );

    sky130_fd_sc_hd__or2 cell_51 (
        .A(net_18),
        .B(net_11),
        .X(net_21)
    );

    sky130_fd_sc_hd__and2 cell_70 (
        .A(net_188),
        .B(net_21),
        .X(net_306)
    );

    sky130_fd_sc_hd__and2 cell_75 (
        .A(net_123),
        .B(net_122),
        .X(net_145)
    );

    sky130_fd_sc_hd__and4bb cell_147 (
        .A_N(net_153),
        .B_N(net_306),
        .C(net_329),
        .D(net_332),
        .X(S)
    );

endmodule

module adder_demo__inferred_block_1 (
    input wire en,
    output wire net_34,
    output wire net_35,
    output wire net_52,
    input wire net_55,
    input wire net_57,
    input wire net_66,
    output wire net_91,
    input wire net_123,
    input wire net_281,
    output wire net_332,
    input wire net_371,
    input wire net_471,
    input wire rst_n
);
    wire net_30;
    wire net_36;
    wire net_38;
    wire net_42;
    wire net_46;
    wire net_61;
    wire net_62;
    wire net_64;
    wire net_126;
    wire net_128;
    wire net_164;
    wire net_177;
    wire net_192;
    wire net_268;
    wire net_335;
    wire net_400;

    sky130_fd_sc_hd__and4bb cell_0 (
        .A_N(net_335),
        .B_N(net_177),
        .C(net_62),
        .D(net_281),
        .X(net_332)
    );

    sky130_fd_sc_hd__mux2 cell_12 (
        .A1(net_46),
        .A0(net_35),
        .X(net_30),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_13 (
        .A1(net_123),
        .A0(net_46),
        .X(net_164),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_16 (
        .A1(net_91),
        .A0(net_34),
        .X(net_400),
        .S(en)
    );

    sky130_fd_sc_hd__dfrtp cell_21 (
        .RESET_B(rst_n),
        .Q(net_46),
        .CLK(net_66),
        .D(net_164)
    );

    sky130_fd_sc_hd__dfrtp cell_23 (
        .RESET_B(rst_n),
        .Q(net_34),
        .CLK(net_371),
        .D(net_400)
    );

    sky130_fd_sc_hd__dfrtp cell_24 (
        .RESET_B(rst_n),
        .Q(net_35),
        .CLK(net_66),
        .D(net_30)
    );

    sky130_fd_sc_hd__dfrtp cell_26 (
        .RESET_B(rst_n),
        .Q(net_91),
        .CLK(net_371),
        .D(net_471)
    );

    sky130_fd_sc_hd__nand2 cell_35 (
        .A(net_46),
        .B(net_91),
        .Y(net_61)
    );

    sky130_fd_sc_hd__xor2 cell_38 (
        .B(net_42),
        .A(net_57),
        .X(net_177)
    );

    sky130_fd_sc_hd__xor2 cell_39 (
        .B(net_128),
        .A(net_36),
        .X(net_335)
    );

    sky130_fd_sc_hd__a31o cell_45 (
        .B1(net_192),
        .A1(net_46),
        .A2(net_91),
        .A3(net_64),
        .X(net_38)
    );

    sky130_fd_sc_hd__or2 cell_50 (
        .A(net_46),
        .B(net_91),
        .X(net_268)
    );

    sky130_fd_sc_hd__or2 cell_52 (
        .A(net_35),
        .B(net_34),
        .X(net_64)
    );

    sky130_fd_sc_hd__a31o cell_53 (
        .B1(net_38),
        .A1(net_57),
        .A2(net_42),
        .A3(net_36),
        .X(net_52)
    );

    sky130_fd_sc_hd__xor2 cell_54 (
        .B(net_52),
        .A(net_55),
        .X(net_62)
    );

    sky130_fd_sc_hd__nor2 cell_58 (
        .A(net_126),
        .B(net_192),
        .Y(net_36)
    );

    sky130_fd_sc_hd__nor2 cell_62 (
        .A(net_35),
        .B(net_34),
        .Y(net_126)
    );

    sky130_fd_sc_hd__and2 cell_66 (
        .A(net_35),
        .B(net_34),
        .X(net_192)
    );

    sky130_fd_sc_hd__a21bo cell_71 (
        .B1_N(net_61),
        .A1(net_57),
        .A2(net_42),
        .X(net_128)
    );

    sky130_fd_sc_hd__and2 cell_73 (
        .A(net_268),
        .B(net_61),
        .X(net_42)
    );

endmodule

module adder_demo__inferred_block_2 (
    input wire en,
    input wire net_33,
    input wire net_37,
    input wire net_52,
    input wire net_55,
    input wire net_66,
    input wire net_206,
    input wire net_209,
    output wire net_329,
    input wire net_371,
    input wire rst_n
);
    wire net_22;
    wire net_29;
    wire net_41;
    wire net_45;
    wire net_53;
    wire net_65;
    wire net_87;
    wire net_100;
    wire net_109;
    wire net_113;
    wire net_125;
    wire net_132;
    wire net_173;
    wire net_233;
    wire net_292;
    wire net_333;
    wire net_351;
    wire net_385;
    wire net_419;

    sky130_fd_sc_hd__and3 cell_1 (
        .A(net_351),
        .B(net_333),
        .C(net_173),
        .X(net_329)
    );

    sky130_fd_sc_hd__mux2 cell_9 (
        .A1(net_33),
        .A0(net_65),
        .X(net_100),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_11 (
        .A1(net_37),
        .A0(net_233),
        .X(net_419),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_14 (
        .A1(net_233),
        .A0(net_22),
        .X(net_385),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_15 (
        .A1(net_65),
        .A0(net_113),
        .X(net_292),
        .S(en)
    );

    sky130_fd_sc_hd__dfrtp cell_22 (
        .RESET_B(rst_n),
        .Q(net_113),
        .CLK(net_66),
        .D(net_292)
    );

    sky130_fd_sc_hd__dfrtp cell_25 (
        .RESET_B(rst_n),
        .Q(net_233),
        .CLK(net_371),
        .D(net_419)
    );

    sky130_fd_sc_hd__dfrtp cell_29 (
        .RESET_B(rst_n),
        .Q(net_22),
        .CLK(net_371),
        .D(net_385)
    );

    sky130_fd_sc_hd__nand2 cell_36 (
        .A(net_53),
        .B(net_87),
        .Y(net_109)
    );

    sky130_fd_sc_hd__a21boi cell_43 (
        .B1_N(net_53),
        .A2(net_125),
        .A1(net_87),
        .Y(net_45)
    );

    sky130_fd_sc_hd__a31o cell_46 (
        .B1(net_206),
        .A1(net_55),
        .A2(net_52),
        .A3(net_209),
        .X(net_125)
    );

    sky130_fd_sc_hd__xnor2 cell_48 (
        .B(net_125),
        .A(net_109),
        .Y(net_351)
    );

    sky130_fd_sc_hd__o21bai cell_49 (
        .A1(net_132),
        .A2(net_45),
        .B1_N(net_29),
        .Y(net_173)
    );

    sky130_fd_sc_hd__or2 cell_55 (
        .A(net_65),
        .B(net_233),
        .X(net_87)
    );

    sky130_fd_sc_hd__nor2 cell_61 (
        .A(net_113),
        .B(net_22),
        .Y(net_132)
    );

    sky130_fd_sc_hd__nor2 cell_64 (
        .A(net_29),
        .B(net_132),
        .Y(net_41)
    );

    sky130_fd_sc_hd__and2 cell_67 (
        .A(net_113),
        .B(net_22),
        .X(net_29)
    );

    sky130_fd_sc_hd__xnor2 cell_69 (
        .B(net_45),
        .A(net_41),
        .Y(net_333)
    );

    sky130_fd_sc_hd__nand2 cell_74 (
        .A(net_65),
        .B(net_233),
        .Y(net_53)
    );

    sky130_fd_sc_hd__dfrtp cell_171 (
        .RESET_B(rst_n),
        .Q(net_65),
        .CLK(net_66),
        .D(net_100)
    );

endmodule

module adder_demo__inferred_block_3 (
    input wire en,
    output wire net_33,
    input wire net_34,
    input wire net_35,
    output wire net_37,
    input wire net_52,
    output wire net_55,
    input wire net_66,
    output wire net_206,
    output wire net_209,
    output wire net_281,
    input wire net_371,
    input wire rst_n
);
    wire net_14;
    wire net_15;
    wire net_24;
    wire net_31;
    wire net_67;
    wire net_106;
    wire net_107;
    wire net_151;
    wire net_227;
    wire net_311;
    wire net_415;
    wire net_465;

    sky130_fd_sc_hd__mux2 cell_10 (
        .A1(net_35),
        .A0(net_14),
        .X(net_67),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_17 (
        .A1(net_34),
        .A0(net_15),
        .X(net_465),
        .S(en)
    );

    sky130_fd_sc_hd__mux2 cell_18 (
        .A1(net_15),
        .A0(net_37),
        .X(net_415),
        .S(en)
    );

    sky130_fd_sc_hd__dfrtp cell_19 (
        .RESET_B(rst_n),
        .Q(net_15),
        .CLK(net_371),
        .D(net_465)
    );

    sky130_fd_sc_hd__dfrtp cell_20 (
        .RESET_B(rst_n),
        .Q(net_37),
        .CLK(net_371),
        .D(net_415)
    );

    sky130_fd_sc_hd__dfrtp cell_27 (
        .RESET_B(rst_n),
        .Q(net_14),
        .CLK(net_66),
        .D(net_67)
    );

    sky130_fd_sc_hd__mux2 cell_28 (
        .A1(net_14),
        .A0(net_33),
        .X(net_151),
        .S(en)
    );

    sky130_fd_sc_hd__dfrtp cell_34 (
        .RESET_B(rst_n),
        .Q(net_33),
        .CLK(net_66),
        .D(net_151)
    );

    sky130_fd_sc_hd__xor2 cell_41 (
        .B(net_227),
        .A(net_209),
        .X(net_281)
    );

    sky130_fd_sc_hd__a31o cell_42 (
        .B1(net_106),
        .A1(net_14),
        .A2(net_15),
        .A3(net_107),
        .X(net_206)
    );

    sky130_fd_sc_hd__and2 cell_56 (
        .A(net_14),
        .B(net_15),
        .X(net_24)
    );

    sky130_fd_sc_hd__nor2 cell_57 (
        .A(net_24),
        .B(net_31),
        .Y(net_55)
    );

    sky130_fd_sc_hd__a21o cell_59 (
        .B1(net_24),
        .A1(net_55),
        .A2(net_52),
        .X(net_227)
    );

    sky130_fd_sc_hd__nor2 cell_60 (
        .A(net_33),
        .B(net_37),
        .Y(net_311)
    );

    sky130_fd_sc_hd__nor2 cell_63 (
        .A(net_311),
        .B(net_106),
        .Y(net_209)
    );

    sky130_fd_sc_hd__nor2 cell_65 (
        .A(net_14),
        .B(net_15),
        .Y(net_31)
    );

    sky130_fd_sc_hd__or2 cell_68 (
        .A(net_33),
        .B(net_37),
        .X(net_107)
    );

    sky130_fd_sc_hd__and2 cell_72 (
        .A(net_33),
        .B(net_37),
        .X(net_106)
    );

endmodule

module adder_demo (
    input wire clk,
    input wire A,
    input wire en,
    input wire B,
    input wire rst_n,
    output wire S
);

    wire net_33;
    wire net_34;
    wire net_35;
    wire net_37;
    wire net_52;
    wire net_55;
    wire net_57;
    wire net_66;
    wire net_91;
    wire net_123;
    wire net_206;
    wire net_209;
    wire net_281;
    wire net_315;
    wire net_329;
    wire net_332;
    wire net_371;
    wire net_471;

    adder_demo__inferred_block_0 inferred_block_0 (
        .A(A),
        .B(B),
        .S(S),
        .en(en),
        .net_57(net_57),
        .net_66(net_66),
        .net_91(net_91),
        .net_123(net_123),
        .net_329(net_329),
        .net_332(net_332),
        .net_371(net_371),
        .net_471(net_471),
        .rst_n(rst_n)
    );

    adder_demo__inferred_block_1 inferred_block_1 (
        .en(en),
        .net_34(net_34),
        .net_35(net_35),
        .net_52(net_52),
        .net_55(net_55),
        .net_57(net_57),
        .net_66(net_66),
        .net_91(net_91),
        .net_123(net_123),
        .net_281(net_281),
        .net_332(net_332),
        .net_371(net_371),
        .net_471(net_471),
        .rst_n(rst_n)
    );

    adder_demo__inferred_block_2 inferred_block_2 (
        .en(en),
        .net_33(net_33),
        .net_37(net_37),
        .net_52(net_52),
        .net_55(net_55),
        .net_66(net_66),
        .net_206(net_206),
        .net_209(net_209),
        .net_329(net_329),
        .net_371(net_371),
        .rst_n(rst_n)
    );

    adder_demo__inferred_block_3 inferred_block_3 (
        .en(en),
        .net_33(net_33),
        .net_34(net_34),
        .net_35(net_35),
        .net_37(net_37),
        .net_52(net_52),
        .net_55(net_55),
        .net_66(net_66),
        .net_206(net_206),
        .net_209(net_209),
        .net_281(net_281),
        .net_371(net_371),
        .rst_n(rst_n)
    );

    sky130_fd_sc_hd__clkbuf cell_2 (
        .A(net_315),
        .X(net_371)
    );

    sky130_fd_sc_hd__clkbuf cell_3 (
        .A(clk),
        .X(net_315)
    );

    sky130_fd_sc_hd__clkbuf cell_83 (
        .A(net_315),
        .X(net_66)
    );

endmodule
