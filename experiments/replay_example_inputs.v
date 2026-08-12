`timescale 1ps / 1ps

// Temporary replay harness for the two attempts recorded in
// example_inputs.vcd. This is for validating the recovered circuit, not the
// eventual interface for searching candidate inputs.
module puzzle_testbench;
    reg clk;
    reg rst_n;
    reg enable;
    reg I;

    wire [7:0] O;
    wire success;

    localparam [120:0] ATTEMPT_1 =
        121'b0010101000000010110000101001100000000010000001110110000100101100001110011000000010110000001011100000000010000011001110000;

    localparam [120:0] ATTEMPT_2 =
        121'b1101011000010011110000000001000001000011000011101110000100001100001001011000000101110000110011100000000010000000000100000;

    puzzle dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .I(I),
        .O(O),
        .success(success)
    );

    always #5000 clk = ~clk;

    task replay_attempt;
        input [120:0] bits;
        integer bit_index;

        begin
            enable = 1;

            // The leftmost literal bit is bits[120] and is presented first.
            for (bit_index = 120; bit_index >= 0; bit_index = bit_index - 1) begin
                I = bits[bit_index];
                @(posedge clk);
                @(negedge clk);
            end

            enable = 0;
            I = 0;
        end
    endtask

    initial begin
        $dumpfile("replayed_inputs.vcd");
        $dumpvars(1, puzzle_testbench);

        clk = 0;
        rst_n = 0;
        enable = 0;
        I = 0;

        // First attempt starts at 40,000 ps, matching the supplied VCD.
        repeat (3) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        replay_attempt(ATTEMPT_1);

        // Allow the output generator to emit its response.
        repeat (31) @(negedge clk);

        // Reset before the second attempt, as required by the puzzle.
        rst_n = 0;
        repeat (3) @(negedge clk);
        rst_n = 1;
        @(negedge clk);
        replay_attempt(ATTEMPT_2);

        repeat (31) @(negedge clk);
        $finish;
    end
endmodule
