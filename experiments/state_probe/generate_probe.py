"""Generate a disposable testbench for differential state probing."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECONSTRUCTION_PATH = ROOT / "puzzle" / "reversed_puzzle.json"
RESULTS_DIRECTORY = Path(__file__).parent / "results"

BASELINE_TEXT = "The night s"
POST_INPUT_CYCLES = 31
KEY_NETS = (3771, 3874)


def encode_text(text):
    # The supplied VCD reveals an 11-cycle character frame: eight ASCII data
    # bits least-significant-bit first, followed by three zero cycles.
    return "".join(f"{ord(character):08b}"[::-1] + "000" for character in text)


def cell_number(name):
    return int(name.rsplit("_", 1)[1])


reconstruction = json.loads(RECONSTRUCTION_PATH.read_text(encoding="utf-8"))
top_pins = {
    pin["net_id"]: pin["name"]
    for pin in reconstruction["top_pins"]
}


def verilog_signal(net_id):
    return f"dut.{top_pins.get(net_id, f'net_{net_id}')}"


flip_flops = []

for instance in sorted(
    reconstruction["instances"],
    key=lambda item: cell_number(item["name"]),
):
    pins = instance["pins"]

    # For the SKY130 cells in this circuit, the functional D/Q/CLK interface
    # directly identifies a D-type storage element. Physical drive-strength
    # suffixes and reset/set variants do not change that interface.
    if not (
        pins.get("D", {}).get("direction") == "input"
        and pins.get("Q", {}).get("direction") == "output"
        and pins.get("CLK", {}).get("direction") == "input"
    ):
        continue

    flip_flops.append(
        {
            "name": instance["name"],
            "cell_type": instance["cell_type"],
            "d_net": pins["D"]["net_id"],
            "q_net": pins["Q"]["net_id"],
            "d_column": f"{instance['name']}_D",
            "q_column": f"{instance['name']}_Q",
        }
    )

variants = [{"id": 0, "position": None, "text": BASELINE_TEXT}]

for position, character in enumerate(BASELINE_TEXT):
    mutated = list(BASELINE_TEXT)
    mutated[position] = chr(ord(character) ^ 1)
    variants.append(
        {
            "id": position + 1,
            "position": position,
            "text": "".join(mutated),
        }
    )

for variant in variants:
    variant["bits"] = encode_text(variant["text"])

if encode_text(BASELINE_TEXT) != (
    "00101010000000101100001010011000000000100000011101100001001011000"
    "01110011000000010110000001011100000000010000011001110000"
):
    raise RuntimeError("the discovered character encoding no longer matches the VCD")

trace_columns = []
trace_expressions = []

for net_id in KEY_NETS:
    trace_columns.append(f"net_{net_id}")
    trace_expressions.append(verilog_signal(net_id))

for flip_flop in flip_flops:
    trace_columns.extend((flip_flop["d_column"], flip_flop["q_column"]))
    trace_expressions.extend(
        (
            verilog_signal(flip_flop["d_net"]),
            verilog_signal(flip_flop["q_net"]),
        )
    )

header = ",".join(
    ("run", "cycle", "input_phase", "I", "enable", "O", "success")
    + tuple(trace_columns)
)
value_format = ",".join(
    ("%0d", "%0d", "%0d", "%b", "%b", "%b", "%b")
    + ("%b",) * len(trace_expressions)
)
value_arguments = ",\n            ".join(
    ("run_id", "cycle", "input_phase", "I", "enable", "O", "success")
    + tuple(trace_expressions)
)
attempt_assignments = "\n".join(
    f"        attempts[{variant['id']}] = 121'b{variant['bits']};"
    for variant in variants
)

testbench = f"""`timescale 1ps / 1ps

module state_probe_testbench;
    reg clk;
    reg rst_n;
    reg enable;
    reg I;
    reg [120:0] attempts [0:{len(variants) - 1}];

    wire [7:0] O;
    wire success;

    integer trace_file;
    integer run_index;

    puzzle dut (
        .clk(clk),
        .rst_n(rst_n),
        .enable(enable),
        .I(I),
        .O(O),
        .success(success)
    );

    always #5000 clk = ~clk;

    task record_cycle;
        input integer run_id;
        input integer cycle;
        input integer input_phase;
        begin
            $fwrite(
                trace_file,
                "{value_format}\\n",
                {value_arguments}
            );
        end
    endtask

    task run_attempt;
        input [120:0] bits;
        input integer run_id;
        integer bit_index;
        integer cycle;
        integer post_cycle;

        begin
            rst_n = 0;
            enable = 0;
            I = 0;
            repeat (3) @(negedge clk);
            rst_n = 1;
            @(negedge clk);

            enable = 1;
            cycle = 0;

            for (bit_index = 120; bit_index >= 0; bit_index = bit_index - 1) begin
                I = bits[bit_index];
                @(posedge clk);
                @(negedge clk);
                record_cycle(run_id, cycle, 1);
                cycle = cycle + 1;
            end

            enable = 0;
            I = 0;

            for (post_cycle = 0; post_cycle < {POST_INPUT_CYCLES}; post_cycle = post_cycle + 1) begin
                @(posedge clk);
                @(negedge clk);
                record_cycle(run_id, cycle, 0);
                cycle = cycle + 1;
            end
        end
    endtask

    initial begin
{attempt_assignments}

        trace_file = $fopen("experiments/state_probe/results/probe_trace.csv", "w");
        $fwrite(trace_file, "{header}\\n");

        $dumpfile("experiments/state_probe/results/probe.vcd");
        $dumpvars(0, clk, rst_n, enable, I, O, success);
        $dumpvars(1, dut);

        clk = 0;
        rst_n = 0;
        enable = 0;
        I = 0;

        for (run_index = 0; run_index < {len(variants)}; run_index = run_index + 1) begin
            run_attempt(attempts[run_index], run_index);
        end

        $fclose(trace_file);
        $finish;
    end
endmodule
"""

manifest = {
    "baseline": BASELINE_TEXT,
    "post_input_cycles": POST_INPUT_CYCLES,
    "variants": variants,
    "key_nets": list(KEY_NETS),
    "flip_flops": flip_flops,
}

RESULTS_DIRECTORY.mkdir(parents=True, exist_ok=True)
(RESULTS_DIRECTORY / "probe_testbench.v").write_text(testbench, encoding="utf-8")
(RESULTS_DIRECTORY / "probe_manifest.json").write_text(
    json.dumps(manifest, indent=2) + "\n",
    encoding="utf-8",
)

print(f"ATTEMPTS {len(variants)}")
print(f"FLIP_FLOPS {len(flip_flops)}")
print(f"WROTE {RESULTS_DIRECTORY / 'probe_testbench.v'}")
print(f"WROTE {RESULTS_DIRECTORY / 'probe_manifest.json'}")
