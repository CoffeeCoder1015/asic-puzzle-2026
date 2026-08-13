`timescale 1ps / 1ps

// Exercises the recovered alternate-result path through the real puzzle
// output pins.  Each board has exactly two stars in every row and column and
// deliberately contains a different kind of touching pair.  The still-
// unknown terminal qualifier is forced only for the handoff clock; the touch
// detector, alternate-result flip-flop, response controller, and O[7:0] logic
// all run normally.
module trigger_two_not_touch_testbench;
    reg clk;
    reg rst_n;
    reg enable;
    reg I;

    wire [7:0] O;
    wire success;

    integer failures;

    puzzle dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .I(I),
        .O(O),
        .success(success)
    );

    always #5000 clk = ~clk;

    function integer selected;
        input integer board;
        input integer row;
        input integer column;
        integer first_column;
        integer second_column;
        begin
            first_column = (2 * row) % 11;

            case (board)
                // Horizontal neighbours occur within each row.
                0: second_column = (2 * row + 1) % 11;

                // The second star in row r is directly above the first star
                // in row r+1.
                1: second_column = (2 * row + 2) % 11;

                // The second star in row r is diagonally adjacent to the
                // first star in row r+1.
                2: second_column = (2 * row + 3) % 11;

                default: second_column = -1;
            endcase

            selected =
                column == first_column || column == second_column;
        end
    endfunction

    function [7:0] expected_byte;
        input integer index;
        begin
            case (index)
                 0: expected_byte = "T";
                 1: expected_byte = "W";
                 2: expected_byte = "O";
                 3: expected_byte = " ";
                 4: expected_byte = "N";
                 5: expected_byte = "O";
                 6: expected_byte = "T";
                 7: expected_byte = " ";
                 8: expected_byte = "T";
                 9: expected_byte = "O";
                10: expected_byte = "U";
                11: expected_byte = "C";
                12: expected_byte = "H";
                default: expected_byte = 8'h00;
            endcase
        end
    endfunction

    task show_board;
        input integer board;
        integer row;
        integer column;
        begin
            for (row = 0; row < 11; row = row + 1) begin
                $write("    ");
                for (column = 0; column < 11; column = column + 1)
                    $write("%c", selected(board, row, column) ? "*" : ".");
                $write("\n");
            end
        end
    endtask

    task reset_dut;
        begin
            rst_n = 0;
            enable = 0;
            I = 0;
            repeat (3) @(negedge clk);
            rst_n = 1;
            @(negedge clk);
        end
    endtask

    task drive_board;
        input integer board;
        integer row;
        integer column;
        begin
            enable = 1;

            for (row = 0; row < 11; row = row + 1) begin
                for (column = 0; column < 11; column = column + 1) begin
                    I = selected(board, row, column);
                    @(posedge clk);
                    @(negedge clk);
                end
            end

            enable = 0;
            I = 0;
        end
    endtask

    task run_board;
        input integer board;
        input [8*24-1:0] description;
        integer output_index;
        begin
            $display("BOARD %0d: %0s", board + 1, description);
            show_board(board);

            reset_dut;
            drive_board(board);

            if (dut.net_2255 !== 1'b1) begin
                $display("  FAIL: natural touch flag was not set");
                failures = failures + 1;
            end else begin
                $display("  natural touch flag: set");
            end

            // net_4166 & net_4201 is the shared terminal qualifier used by
            // both success and the alternate-result latch.  Force only that
            // unknown prerequisite for one handoff edge.
            force dut.net_4166 = 1'b1;
            force dut.net_4201 = 1'b1;
            @(posedge clk);
            @(negedge clk);
            release dut.net_4166;
            release dut.net_4201;

            if (dut.net_3920 !== 1'b1) begin
                $display("  FAIL: alternate-result flip-flop was not set");
                failures = failures + 1;
            end else begin
                $display("  alternate-result flip-flop: set");
            end

            $write("  top-level output: \"");
            for (output_index = 0; output_index < 13;
                 output_index = output_index + 1) begin
                $write("%c", O);
                if (O !== expected_byte(output_index)) begin
                    $write("[expected %c]", expected_byte(output_index));
                    failures = failures + 1;
                end
                @(negedge clk);
            end
            $write("\"\n\n");
        end
    endtask

    initial begin
        clk = 0;
        rst_n = 0;
        enable = 0;
        I = 0;
        failures = 0;

        run_board(0, "horizontal touching");
        run_board(1, "vertical touching");
        run_board(2, "diagonal touching");

        if (failures == 0)
            $display("PASS: all three boards emitted TWO NOT TOUCH");
        else
            $display("FAIL: %0d checks failed", failures);

        $finish;
    end
endmodule
