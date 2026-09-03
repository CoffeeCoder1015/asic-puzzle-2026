import z3

from z3_circuit_model import solver


I_seq = [1] * 121 + [0] * 11

for time, I in enumerate(I_seq):
    solver.add(
        z3.Bool(f"top_I_{time}")
        == z3.BoolVal(bool(I))
    )
    solver.add(
        z3.Bool(f"top_enable_{time}")
        == z3.BoolVal(True)
    )
    solver.add(
        z3.Bool(f"top_rst_n_{time}")
        == z3.BoolVal(True)
    )

result = solver.check()

if result != z3.sat:
    raise RuntimeError(f"unexpected solver result: {result}")

model = solver.model()

for time in range(len(I_seq)):
    output_bits = [
        model.eval(
            z3.Bool(f"top_O[{bit}]_{time}"),
            model_completion=True,
        )
        for bit in range(8)
    ]
    out_bus_raw = "".join(
        "1" if z3.is_true(bit) else "0"
        for bit in reversed(output_bits)
    )
    out_bus_dec = int(out_bus_raw, 2)
    print(chr(out_bus_dec), end="")
