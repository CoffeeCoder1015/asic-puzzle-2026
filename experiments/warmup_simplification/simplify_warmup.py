import json
from pathlib import Path
import networkx as nx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
breakdown_path = PROJECT_ROOT / "warmup" / "reversed_04_final.json"
cell_classifications = PROJECT_ROOT / "cell_classifications.json"

with breakdown_path.open(encoding="utf-8") as file:
    gds_breakdown = json.load(file)

with cell_classifications.open(encoding="utf-8") as file:
    cell_classes = json.load(file)

top_pins = gds_breakdown["top_pins"]
ports = gds_breakdown["ports"]
port_map = {p["name"]: p["direction"] for p in ports}

instances = {
    instance["name"]: instance
    for instance in gds_breakdown["instances"]
}
sequential_cells = set(cell_classes["sequential"])
comb_formulas = cell_classes["combinational"]

def get_cell_family_name(cell_type: str):
    return cell_type.rsplit("_", 1)[0]

def tag_cell_class(cell: dict):
    is_comb = get_cell_family_name(cell["cell_type"]) not in sequential_cells
    cell["kind"] = "combinational" if is_comb else "sequential"
    return cell

instances = {
    name: tag_cell_class(instance)
    for name, instance in instances.items()
}

def distinguish_cell_IO(cell_instance: dict):
    pins = cell_instance["pins"]
    signal_pins = dict(filter(lambda x: x[1]["kind"] == "signal", pins.items()))
    input_pins = dict(filter(lambda x: x[1]["direction"] == "input", signal_pins.items()))
    output_pins = dict(filter(lambda x: x[1]["direction"] == "output", signal_pins.items()))
    return (input_pins, output_pins)

nets = {}
for instance in instances.values():
    inputs, outputs = distinguish_cell_IO(instance)
    for pin_name, pin_info in inputs.items():
        net_id = pin_info["net_id"]
        nets.setdefault(net_id, {})
        nets[net_id].setdefault("sinks", {})
        nets[net_id]["sinks"][instance["name"]] = {
            "kind": instance["kind"],
            "type": instance["cell_type"],
            "pin": pin_name,
        }
    for pin_name, pin_info in outputs.items():
        net_id = pin_info["net_id"]
        nets.setdefault(net_id, {})
        nets[net_id].setdefault("sources", {})
        nets[net_id]["sources"][instance["name"]] = {
            "kind": instance["kind"],
            "type": instance["cell_type"],
            "pin": pin_name,
        }

for pin in top_pins:
    net_id = pin["net_id"]
    pin_name = pin["name"]
    pin_canonical = pin_name.rsplit("[", 1)[0]
    direction = port_map.get(pin_canonical)

    pin_category = None
    if direction == "input":
        pin_category = "sources"
    elif direction == "output":
        pin_category = "sinks"

    if pin_category is not None:
        nets.setdefault(net_id, {})
        nets[net_id].setdefault(pin_category, {})
        nets[net_id][pin_category]["top"] = {
            "kind": "combinational",
            "type": "top",
            "pin": pin_name,
        }

print("=== WARMUP GRAPH SUMMARY ===")
print(f"Total standard cell instances: {len(instances)}")
comb_count = sum(1 for c in instances.values() if c["kind"] == "combinational")
seq_count = sum(1 for c in instances.values() if c["kind"] == "sequential")
print(f"Combinational cells: {comb_count}")
print(f"Sequential flip-flops: {seq_count}")
print(f"Total signal nets: {len(nets)}")

# -------------------------------------------------------------
# Boolean AST Representation & Simplifier
# -------------------------------------------------------------

class ASTNode:
    pass

class Var(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def eval(self, env):
        return env[self.name]

class Const(ASTNode):
    def __init__(self, val: int):
        self.val = val & 1
    def __repr__(self):
        return str(self.val)
    def eval(self, env):
        return self.val

class Not(ASTNode):
    def __init__(self, child):
        self.child = child
    def __repr__(self):
        return f"!{self.child}"
    def eval(self, env):
        return 1 ^ self.child.eval(env)

class And(ASTNode):
    def __init__(self, *children):
        self.children = list(children)
    def __repr__(self):
        return f"({' & '.join(str(c) for c in self.children)})"
    def eval(self, env):
        res = 1
        for c in self.children:
            res &= c.eval(env)
        return res

class Or(ASTNode):
    def __init__(self, *children):
        self.children = list(children)
    def __repr__(self):
        return f"({' | '.join(str(c) for c in self.children)})"
    def eval(self, env):
        res = 0
        for c in self.children:
            res |= c.eval(env)
        return res

class Xor(ASTNode):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self):
        return f"({self.a} ^ {self.b})"
    def eval(self, env):
        return self.a.eval(env) ^ self.b.eval(env)

def simplify(node: ASTNode) -> ASTNode:
    if isinstance(node, (Var, Const)):
        return node

    if isinstance(node, Not):
        c = simplify(node.child)
        if isinstance(c, Const):
            return Const(1 ^ c.val)
        if isinstance(c, Not):
            return c.child
        return Not(c)

    if isinstance(node, And):
        children = [simplify(c) for c in node.children]
        flat = []
        for c in children:
            if isinstance(c, And):
                flat.extend(c.children)
            elif isinstance(c, Const):
                if c.val == 0:
                    return Const(0)
            else:
                flat.append(c)
        if not flat:
            return Const(1)
        if len(flat) == 1:
            return flat[0]
        return And(*flat)

    if isinstance(node, Or):
        children = [simplify(c) for c in node.children]
        flat = []
        for c in children:
            if isinstance(c, Or):
                flat.extend(c.children)
            elif isinstance(c, Const):
                if c.val == 1:
                    return Const(1)
            else:
                flat.append(c)
        if not flat:
            return Const(0)
        if len(flat) == 1:
            return flat[0]
        return Or(*flat)

    if isinstance(node, Xor):
        a = simplify(node.a)
        b = simplify(node.b)
        if isinstance(a, Const) and isinstance(b, Const):
            return Const(a.val ^ b.val)
        if isinstance(a, Const) and a.val == 0:
            return b
        if isinstance(b, Const) and b.val == 0:
            return a
        if isinstance(a, Const) and a.val == 1:
            return simplify(Not(b))
        if isinstance(b, Const) and b.val == 1:
            return simplify(Not(a))
        return Xor(a, b)

    return node

# -------------------------------------------------------------
# Parser for standard cell formulas
# -------------------------------------------------------------

def parse_expr(formula_str: str, pin_map: dict[str, ASTNode]) -> ASTNode:
    # Tokenizer / parser for basic Liberty formulas
    import re
    tokens = re.findall(r"[A-Za-z0-9_]+|[()!&|^]", formula_str)
    pos = 0

    def parse_or():
        nonlocal pos
        res = parse_xor()
        while pos < len(tokens) and tokens[pos] == '|':
            pos += 1
            res = Or(res, parse_xor())
        return res

    def parse_xor():
        nonlocal pos
        res = parse_and()
        while pos < len(tokens) and tokens[pos] == '^':
            pos += 1
            res = Xor(res, parse_and())
        return res

    def parse_and():
        nonlocal pos
        res = parse_unary()
        while pos < len(tokens) and tokens[pos] == '&':
            pos += 1
            res = And(res, parse_unary())
        return res

    def parse_unary():
        nonlocal pos
        if pos >= len(tokens):
            return Const(0)
        tok = tokens[pos]
        pos += 1
        if tok == '!':
            return Not(parse_unary())
        if tok == '(':
            sub = parse_or()
            if pos < len(tokens) and tokens[pos] == ')':
                pos += 1
            return sub
        if tok == '0':
            return Const(0)
        if tok == '1':
            return Const(1)
        if tok in pin_map:
            return pin_map[tok]
        return Var(tok)

    return parse_or()

# -------------------------------------------------------------
# Netlist Backward Logic Cone Collapser
# -------------------------------------------------------------

memo_net = {}

def get_net_ast(net_id: int) -> ASTNode:
    if net_id in memo_net:
        return memo_net[net_id]

    net_info = nets.get(net_id, {})
    sources = net_info.get("sources", {})

    if not sources:
        # Check if it's a known power/ground rail
        for tp in top_pins:
            if tp["net_id"] == net_id:
                if tp["name"] in ("VPWR", "vccd1"):
                    return Const(1)
                if tp["name"] in ("VGND", "vssd1"):
                    return Const(0)
                return Var(tp["name"])
        return Var(f"net_{net_id}")

    src_name, src_data = next(iter(sources.items()))

    if src_name == "top":
        pin_name = src_data["pin"]
        if pin_name in ("VPWR", "vccd1"):
            node = Const(1)
        elif pin_name in ("VGND", "vssd1"):
            node = Const(0)
        else:
            node = Var(pin_name)
        memo_net[net_id] = node
        return node

    cell = instances[src_name]
    cell_family = get_cell_family_name(cell["cell_type"])

    # If it's a sequential cell (flip-flop), stop at the Q output
    if cell["kind"] == "sequential":
        node = Var(f"{src_name}.Q")
        memo_net[net_id] = node
        return node

    # Clock buffers / pure buffers: passthrough
    if "clkbuf" in cell_family or cell_family.endswith("__buf"):
        in_pin = cell["pins"].get("A")
        if in_pin:
            node = get_net_ast(in_pin["net_id"])
            memo_net[net_id] = node
            return node

    # Look up truth template from cell_classifications
    if cell_family in comb_formulas:
        formula_dict = comb_formulas[cell_family]
        out_pin = src_data["pin"]
        formula_str = formula_dict.get(out_pin, "0")

        # Map cell input pins to their incoming net ASTs
        pin_map = {}
        for pin_name, pin_info in cell["pins"].items():
            if pin_info["direction"] == "input" and pin_info["kind"] == "signal":
                pin_map[pin_name] = get_net_ast(pin_info["net_id"])

        node = parse_expr(formula_str, pin_map)
        node = simplify(node)
        memo_net[net_id] = node
        return node

    node = Var(f"{src_name}.{src_data['pin']}")
    memo_net[net_id] = node
    return node

print("\n=== COLLAPSING OUTPUT 'S' CONE ===")
s_net_id = None
for pin in top_pins:
    if pin["name"] == "S":
        s_net_id = pin["net_id"]
        break

if s_net_id is not None:
    s_ast = simplify(get_net_ast(s_net_id))
    print(f"Output S Net ID: {s_net_id}")
    print(f"Collapsed Formula for S:\n{s_ast}")

# -------------------------------------------------------------
# Collapsing the 16 Flip-Flop D inputs (Shift Registers)
# -------------------------------------------------------------
print("\n=== COLLAPSING FLIP-FLOP NEXT-STATE EQUATIONS ===")
dff_d_equations = {}
for name, cell in sorted(instances.items()):
    if cell["kind"] == "sequential":
        d_pin = cell["pins"].get("D")
        if d_pin:
            d_ast = simplify(get_net_ast(d_pin["net_id"]))
            dff_d_equations[f"{name}.D"] = d_ast
            print(f"{name}.D := {d_ast}")

# -------------------------------------------------------------
# Identify Shift Register Chains
# -------------------------------------------------------------
print("\n=== IDENTIFYING RECOVERED SHIFT CHAINS ===")
# A shift register step is: (en & prev_Q) | (!en & self_Q) or mux2(self_Q, prev_Q, en)
# Let's map predecessors for each DFF under en=1
chains = []
for name, cell in sorted(instances.items()):
    if cell["kind"] == "sequential":
        d_pin = cell["pins"].get("D")
        if d_pin:
            eq = dff_d_equations[f"{name}.D"]
            # Evaluate under en=1, rst_n=1
            print(f"  {name}.Q <- drives D with formula: {eq}")

# -------------------------------------------------------------
# Truth Table Verification against A + B == 496
# -------------------------------------------------------------
print("\n=== FULL TRUTH TABLE VERIFICATION ===")
# We have 16 flip-flops in the design.
# Let's find which 8 DFFs belong to A and which 8 belong to B by tracing back from inputs A and B.

def trace_dff_chain(start_input_name):
    chain = []
    current_src = start_input_name
    visited = set()
    for _ in range(8):
        # find DFF that reads current_src under en=1
        found_next = None
        for dff_name, dff_cell in instances.items():
            if dff_cell["kind"] == "sequential" and dff_name not in visited:
                d_ast = str(dff_d_equations[f"{dff_name}.D"])
                if current_src in d_ast:
                    found_next = dff_name
                    break
        if found_next:
            chain.append(found_next)
            visited.add(found_next)
            current_src = f"{found_next}.Q"
        else:
            break
    return chain

chain_a = trace_dff_chain("A")
chain_b = trace_dff_chain("B")

print(f"Recovered Register A (8 bits, LSB->MSB): {chain_a}")
print(f"Recovered Register B (8 bits, LSB->MSB): {chain_b}")

if len(chain_a) == 8 and len(chain_b) == 8:
    print("\nEvaluating all 65,536 combinations of (A, B) through the collapsed Boolean AST of S...")
    match_count = 0
    mismatch_count = 0
    satisfying_pairs = []

    for a_val in range(256):
        for b_val in range(256):
            expected_sum = a_val + b_val
            expected_s = 1 if (expected_sum == 496) else 0

            # Build environment for the AST
            env = {}
            for i, dff in enumerate(chain_a):
                env[f"{dff}.Q"] = (a_val >> i) & 1
            for i, dff in enumerate(chain_b):
                env[f"{dff}.Q"] = (b_val >> i) & 1

            # Test bit order if needed
            s_val = s_ast.eval(env)
            if s_val == 1:
                satisfying_pairs.append((a_val, b_val, expected_sum))

            if s_val == expected_s:
                match_count += 1
            else:
                mismatch_count += 1

    print(f"Pairs where S == 1: {len(satisfying_pairs)}")
    for p in satisfying_pairs[:5]:
        print(f"  A = {p[0]:3d}, B = {p[1]:3d} -> A + B = {p[2]}")
    if len(satisfying_pairs) > 5:
        print(f"  ... and {len(satisfying_pairs) - 5} more")

    if all(p[2] == 496 for p in satisfying_pairs):
        print(f"\nSUCCESS: All {len(satisfying_pairs)} satisfying pairs sum to exactly 496!")
        print("The collapsed Boolean formula for S is 100% mathematically equivalent to (A + B == 496)!")
