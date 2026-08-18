from collections import deque

import z3

from z3_program import call_count, solver


input_length = 121
message_start = 122

for time in range(call_count):
    solver.add(
        z3.Bool(f"top_enable_{time}")
        == z3.BoolVal(True)
    )

for time in range(input_length, call_count):
    solver.add(
        z3.Bool(f"top_I_{time}")
        == z3.BoolVal(False)
    )


output_bytes = []

for time in range(call_count):
    output_bytes.append(
        z3.Sum(
            *(
                z3.If(
                    z3.Bool(f"top_O[{bit}]_{time}"),
                    z3.IntVal(1 << bit),
                    z3.IntVal(0),
                )
                for bit in range(8)
            )
        )
    )


queue = deque([()])

while queue:
    prefix = queue.popleft()
    position = message_start + len(prefix)

    if position >= call_count:
        raise RuntimeError(
            f"output did not reach EOS within the unroll: {prefix!r}"
        )

    solver.push()

    for index, byte in enumerate(prefix):
        solver.add(
            output_bytes[message_start + index]
            == byte
        )

    accepted_bytes = set()

    while True:
        result = solver.check()

        if result == z3.unsat:
            break

        if result == z3.unknown:
            reason = solver.reason_unknown()
            solver.pop()
            raise RuntimeError(
                f"solver returned unknown at prefix {prefix!r}: {reason}"
            )

        model = solver.model()

        # The model contains one complete board and internal trajectory.
        # Evaluating only this byte projects that full model onto the next
        # character currently being enumerated.
        byte = model.eval(
            output_bytes[position],
            model_completion=True,
        ).as_long()

        accepted_bytes.add(byte)

        # This is the prefix-local visited set. It excludes every board and
        # internal trajectory producing this same next byte, so the next check
        # must find a different byte or prove that none remain.
        solver.add(
            output_bytes[position] != byte
        )

    solver.pop()

    if not accepted_bytes:
        raise RuntimeError(
            f"reachable prefix has no continuation: {prefix!r}"
        )

    if 0 in accepted_bytes:
        print(
            "".join(
                chr(byte)
                if 32 <= byte <= 126
                else f"\\x{byte:02x}"
                for byte in prefix
            )
        )

    for byte in sorted(accepted_bytes - {0}):
        queue.append((*prefix, byte))
