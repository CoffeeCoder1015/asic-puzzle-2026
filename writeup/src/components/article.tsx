import { publicAsset } from "../lib/public-asset";
import { ExtractionFigure } from "./figures/extraction-figure";
import { CoverageFigure } from "./figures/coverage-figure";
import { Board } from "./board";
import { ClockFlow } from "./clock-flow";
import { CircuitOpening } from "./circuit-opening";
import { Disclosure } from "./disclosure";
import {
  WarmupExplorer,
  CandidateExplorer,
  PrefixEnumeration,
} from "./interactive-explanations";
import { MESSAGES, SUCCESS_PAIRS } from "../lib/circuit-data";

function BoardResults() {
  return (
    <section
      className="board-results"
      aria-label="Five exact circuit inputs and their outputs"
    >
      {MESSAGES.map((message) => (
        <figure
          className={`board-result${message.success ? " board-result--winner" : ""}`}
          key={message.message}
        >
          <div className="board-result__heading">
            <p className="board-result__message">{message.message}</p>
            {message.success && (
              <span className="board-result__status">success = 1</span>
            )}
          </div>
          <Board message={message} />
          {message.caption && <figcaption>{message.caption}</figcaption>}
          <Disclosure title="121-bit input stream" className="board-bits">
            <code aria-label={`${message.message} input stream`}>
              {message.bits}
            </code>
          </Disclosure>
        </figure>
      ))}
    </section>
  );
}

function BooleanTerms({ mapped = false }: { mapped?: boolean }) {
  return (
    <table className={`formula-table${mapped ? "" : " formula-table--raw"}`}>
      <thead>
        <tr>
          <th aria-label="term" />
          {Array.from({ length: 8 }, (_, bit) => (
            <th scope="col" key={`A${bit}`}>
              A{bit}
            </th>
          ))}
          <th aria-label="and" />
          {Array.from({ length: 8 }, (_, bit) => (
            <th scope="col" key={`B${bit}`}>
              B{bit}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {SUCCESS_PAIRS.map(([a, b]) => (
          <tr key={a}>
            <th scope="row" />
            {Array.from({ length: 8 }, (_, bit) => {
              const value = (a >> bit) & 1;
              return (
                <td key={`A${bit}`}>
                  {mapped ? value : `${value ? "" : "~"}A${bit}`}
                </td>
              );
            })}
            <td className="formula-separator">&amp;</td>
            {Array.from({ length: 8 }, (_, bit) => {
              const value = (b >> bit) & 1;
              return (
                <td key={`B${bit}`}>
                  {mapped ? value : `${value ? "" : "~"}B${bit}`}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function Article() {
  return (
    <article id="top" aria-labelledby="article-title">
      <CircuitOpening>
        <div data-entry-step>
          <p
            id="writeup-start"
            className="article-lead reading-start"
            tabIndex={-1}
          >
            <a href="https://blog.janestreet.com/can-you-reverse-engineer-an-asic/">
              Jane Street
            </a>
            {" "}gave us a chip’s finished layout and asked us to recover the
            circuit, then find the answer string. This is what I had to start with.
          </p>
        </div>
        <div data-entry-step>
          <p>
            I’m a computer science student, and most of my hardware experience
            was with Verilog. But how do you get back to runnable code from a
            finished layout?
          </p>
        </div>
        <div data-entry-step>
          <p>
            Fortunately, there was a warm-up. It came with the original Verilog
            source as well as the finished layout. I could start there and check
            whether my reconstruction matched a known design.
          </p>
        </div>
        <div data-entry-step>
          <p>
            To see what was inside, I opened the warm-up’s layout in the{" "}
            <a href="https://gds-viewer.tinytapeout.com/">TinyTapeout GDS Viewer</a>
            .
          </p>
        </div>
      </CircuitOpening>
      <p>
        <em>
          And hey, what do you know? It was the same viewer used for the image
          at the top of the puzzle’s blog post.
        </em>
      </p>
      <p>
        More usefully, the viewer showed that the GDS preserved both the
        physical layers and the standard-cell instances, the individual building
        blocks of the circuit. Their names identified them as members of
        SkyWater’s SKY130 standard-cell library.
      </p>
      <p>
        That gave me a starting point. I could identify the cells from their
        library definitions, then reconstruct their connections from the layout.
      </p>
      <p>
        The repository included the puzzle files and each stage of the warm-up’s
        design flow, from Verilog to GDS, the final physical layout:
      </p>
      <pre>
        <code>
          {
            "asic-puzzle-2026/\n├── puzzle.gds                         ← reverse this\n├── example_inputs.vcd                 ← sample inputs and outputs\n└── warmup/\n    ├── 00_source.v                    ← original Verilog\n    ├── 01_netlist.v                   ← target representation\n    ├── 02_netlist_with_power_rails.v\n    ├── 03_post_place_and_route.def\n    └── 04_final.gds                   ← final layout"
          }
        </code>
      </pre>
      <h2 id="extracting-the-circuit">Extracting the circuit</h2>
      <p>
        I could see the cells. To recover their wiring in code, I used
        KLayout’s Python API to extract the standard cells and their connections.
      </p>
      <p>
        The extraction followed the physical wiring. KLayout merged touching
        conductor shapes within each layer, connected layers through contacts
        and vias, and assigned each connected component a net ID. Pins reached
        by the same connected component belonged to the same net.
      </p>
      <p>
        I then matched the extracted cells against the SKY130 definitions to
        identify their pins, input and output directions, and logical behavior.
      </p>
      <ExtractionFigure />
      <p>
        For each extracted instance, I recorded its cell type and the direction
        and net ID of every connected pin. The physical layout had become a
        netlist: a description of the circuit’s components and how they were
        wired together.
      </p>
      <h3>Simulating the recovered circuit</h3>
      <p>I had the connections. To run the circuit, I needed to turn them back into Verilog.</p>
      <p>The extracted data now described the logical circuit:</p>
      <ul>
        <li>
          <strong>Cell types</strong>, which identified the logic performed by
          each standard cell.
        </li>
        <li>
          <strong>Pins and directions</strong>, which identified the inputs and
          outputs of each cell.
        </li>
        <li>
          <strong>Net IDs</strong>, which connected output pins to the input
          pins they supplied.
        </li>
      </ul>
      <p>
        The SKY130 library also provided the Verilog models needed to simulate
        those cells.
      </p>
      <p>
        For this logical simulation, I filtered out the power rails and cells
        used only for power connections.
      </p>
      <p>The remaining data mapped almost directly to structural Verilog:</p>
      <ul>
        <li>
          Each signal net became a <code>wire</code>.
        </li>
        <li>Each cell type selected the corresponding SKY130 module.</li>
        <li>Each cell instance became a module instance.</li>
        <li>
          Each pin became a named module argument connected to the wire with the
          same net ID.
        </li>
      </ul>
      <p>
        I wrote a generator that applied this mapping and recovered the module's
        top-level ports from the named nets at the edge of the layout.
      </p>
      <p>
        I compiled the generated Verilog with Icarus Verilog and ran the
        warm-up. Its behavior was consistent with the known circuit, a promising
        first check that the extraction worked.
      </p>
      <h3>Checking the connections</h3>
      <p>
        The warm-up worked on sample inputs. I still wanted to check the
        connections themselves, and a long Verilog file was awkward to inspect.
      </p>
      <p>
        I converted the netlist into a NetworkX graph and plotted it with
        Matplotlib, showing the logical cells, nets, top-level ports, and
        connections.
      </p>
      <p>
        The warm-up gave me a direct comparison: I could build one graph from
        the supplied netlist and another from my reconstruction.
      </p>
      <figure className="figure--wide">
        <img
          src={publicAsset("/figures/warmup-netlist-comparison.png")}
          alt="Side-by-side NetworkX graphs showing that the supplied warm-up netlist and the reconstructed warm-up netlist have the same logical structure."
          width="3180"
          height="1594"
        />
        <figcaption>
          Arranged by connectivity, not physical placement.
        </figcaption>
      </figure>
      <p>
        NetworkX found that the two graphs were isomorphic: they had the same
        connection structure. The reconstruction had recovered the warm-up’s
        wiring.
      </p>
      <h3>Inspecting the puzzle</h3>
      <p>
        With that check in place, I applied the same graph-building code to the
        puzzle. Its reconstructed graph contained 738 logical cells and 717
        electrical nets.
      </p>
      <figure className="figure--wide">
        <img
          src={publicAsset("/figures/puzzle-netlist.png")}
          alt="NetworkX graph of the reconstructed puzzle netlist, showing standard-cell nodes, internal-net nodes, and top-level ports including I, O[7:0], clk, enable, rst_n, and success."
          width="2618"
          height="2184"
        />
        <figcaption>
          The recovered puzzle netlist, arranged by connectivity rather than
          physical placement.
        </figcaption>
      </figure>
      <p>
        The circuit was executable, and I could see all its connections. What I
        still could not see was its purpose.
      </p>
      <hr />
      <p>
        I first tried dividing the graph into communities of closely connected
        cells, hoping they would correspond to recognizable parts of the design.
        They did not. Even on the warm-up, the communities mixed logic from
        different source blocks. A later experiment with DANA grouped related
        flip-flops, but still did not explain the puzzle.
      </p>
      <p>
        If I couldn’t spot the design by looking at the graph, I needed a
        representation I could manipulate in code as well as run. I generated a
        Python version of the circuit.
      </p>
      <p>
        Because Python runs one line at a time while hardware updates all at
        once, that required making the execution order explicit:
      </p>
      <ul>
        <li>
          The combinational logic had to be topologically sorted so that no
          instruction ran before the values it needed had been calculated.
        </li>
        <li>
          The flip-flops became state variables and were updated separately from
          the combinational logic.
        </li>
      </ul>
      <ClockFlow />
      <h2 id="boolean-collapse">Boolean collapse</h2>
      <p>
        With the circuit in Python, my first approach was to combine the
        individual gates into larger Boolean expressions and let algebra
        simplify them.
      </p>
      <p>
        For each cell, I recursively substituted its expression wherever another
        cell used its output. I then passed the expanded expressions to SymPy’s{" "}
        <code>simplify_logic</code>, hoping that simplification would reveal a
        recognizable rule.
      </p>
      <p>
        On the warm-up, it did. The simplified success expression had fifteen
        terms involving two 8-bit input registers, <code>A</code> and{" "}
        <code>B</code>. Each term specified one accepted pair.
      </p>
      <p>
        A bit written directly had to be <code>1</code>; a negated bit had to be{" "}
        <code>0</code>. Reading those requirements as numbers revealed the same
        rule in every term, <code>A + B = 496</code>.
      </p>
      <figure
        className="warmup figure--wide"
        id="warmup"
        aria-labelledby="warmup-title"
      >
        <WarmupExplorer />
      </figure>
      <Disclosure
        title="Inspect the full collapse, all 15 terms and accepted pairs"
        className="collapse-evidence"
      >
        <p>
          The terms are joined by OR. Within each row, all bit requirements are
          joined by AND. Register bits are shown from 0 to 7, least significant
          first.
        </p>
        <figure className="collapse-source" data-asset-kind="programmatic">
          <div className="explanation formula-panel">
            <p className="figure-title">Boolean terms, one per row</p>
            <p className="figure-hint">
              Scroll horizontally on smaller screens.
            </p>
            <div
              className="formula-scroll"
              tabIndex={0}
              role="region"
              aria-label="Boolean terms, one per row"
            >
              <BooleanTerms />
            </div>
          </div>
        </figure>
        <p>Replace each literal with its required bit value.</p>
        <figure className="collapse-mapped" data-asset-kind="programmatic">
          <div className="explanation formula-panel">
            <p className="figure-title">
              Required bit values, in the same order
            </p>
            <div
              className="formula-scroll"
              tabIndex={0}
              role="region"
              aria-label="Required bit values, in the same order"
            >
              <BooleanTerms mapped />
            </div>
          </div>
        </figure>
        <p>Converting each register to decimal gives these fifteen pairs.</p>
        <figure className="figure--collapse-decimal">
          <div
            className="boolean-collapse-decimal"
            role="img"
            aria-label="The fifteen decimal pairs recovered from the collapsed Boolean formula. Every pair adds to 496."
          >
            {SUCCESS_PAIRS.map(([a, b]) => (
              <code key={a}>
                {a} + {b} = 496
              </code>
            ))}
          </div>
        </figure>
      </Disclosure>
      <p>
        The warm-up source raised <code>success</code> when{" "}
        <code>A + B = 496</code>. The collapsed expression had recovered that
        original condition.
      </p>
      <p>
        I tried the same approach on the puzzle. Because the puzzle streamed 121
        bits across dozens of flip-flops instead of checking two static
        registers, the expressions grew enormously without revealing a
        comparable rule. Combining the gates had made the formulas larger, but
        had not made the circuit easier to understand.
      </p>
      <h2 id="z3-output-search">Asking the circuit precise questions</h2>
      <p>
        <em>
          Wait: did I even need to understand what every gate was doing?
        </em>
      </p>
      <p>
        All I really needed was the string the chip was looking for. Instead of
        trying to explain the entire circuit, I asked a smaller question:
      </p>
      <p className="central-question">
        Given the bytes it had already emitted,{" "}
        <strong>what byte could come next?</strong>
      </p>
      <p>
        There were 2<sup>121</sup> possible inputs, but only 256 possible values
        for the next output byte. I could search the outputs and ask Z3, a
        constraint solver, to find inputs that produced them.
      </p>
      <p>
        I modeled the testbench in Z3, with each cycle’s resulting state feeding
        the next. The input bits stayed symbolic, so Z3 could choose their
        values to satisfy the output I requested.
      </p>
      <p>
        I could then constrain the output and ask whether any input satisfied
        the complete model. Z3 returned <code>SAT</code> if such an input
        existed and <code>UNSAT</code> if none did.
      </p>
      <figure
        className="figure--wide figure--z3"
        data-asset-kind="programmatic"
      >
        <CandidateExplorer />
      </figure>
      <p>
        I needed every possible continuation. Starting with an empty output prefix, I
        excluded each byte Z3 returned and asked again. Only an{" "}
        <code>UNSAT</code> result established that no continuation remained.
      </p>
      <figure
        className="figure--wide figure--z3"
        data-asset-kind="programmatic"
      >
        <PrefixEnumeration />
      </figure>
      <p>
        I repeated this process for each continuation, extending the prefix one
        byte at a time. A zero byte ended a message. The result was a tree of
        every possible output message, built without first identifying the
        computation behind it.
      </p>
      <hr />
      <p>
        Eventually, the tree stopped growing. Under the modeled input and
        readout sequence, the circuit could emit exactly five messages across
        all possible 121-bit inputs.
      </p>
      <p>
        For each message, Z3 also supplied a concrete input that produced it.
      </p>
      <p>
        I later learned that this was a Star Battle board. To show the inputs in
        that form, I’ve arranged each 121-bit sequence into eleven rows of
        eleven, with the original serial sequence beneath it.
      </p>
      <h2 id="five-messages">Five messages, one successful input</h2>
      <BoardResults />
      <p>
        Only the last of these inputs raised <code>success</code>.
      </p>
      <p>
        <em>
          Before celebrating, I wanted to make sure it wasn’t a quirk of my Z3
          setup.
        </em>{" "}
        To check it outside Z3, I reset the ordinary Python circuit evaluator
        and replayed the 121 bits in their original serial order. It emitted{" "}
        <code>(* TWO STARS *)</code> and raised <code>success</code> again.
      </p>
      <p>
        That was the answer. I had recovered enough of the circuit to reproduce
        its behavior, then searched that behavior to find the successful input.
        Understanding the purpose of every group of gates had never become
        necessary.
      </p>
      <h2 id="ml-postscript">Postscript: searching by circuit activation</h2>
      <p>
        After solving the puzzle, one question kept nagging at me:{" "}
        <em>
          could a learned search discover interesting boards on its own, just by
          trying to light up parts of the circuit that earlier boards had not
          reached?
        </em>
      </p>
      <p>
        The idea was to supply a board, record which internal values became{" "}
        <code>true</code>, and search for edits that activated something new.
      </p>
      <p>
        I traced backward from the output bus to identify internal values that
        could affect the output. For each board, the Python evaluator recorded
        which of those values became <code>true</code> during the input and
        readout cycles. The same value at two different clocks counted as two
        separate coverage items.
      </p>
      <p>
        Combining those records across boards showed how much of this activation
        coverage the search had reached.
      </p>
      <CoverageFigure />
      <p>
        The learned editor received the current 121-bit board, its recorded
        circuit states, and the coverage already reached along that search path.
        It assigned probabilities to flipping each board position under two
        possible edit sizes.
      </p>
      <p>
        The surrounding search evaluated both proposals and selected the more
        useful edit size. It also evaluated every possible one-bit alternative
        to assign credit. Circuit evaluation and coverage recording remained
        exact; the learned component guided the choice of edits.
      </p>
      <h3>What a simple baseline could reach</h3>
      <p>
        <em>
          The ML run reached roughly 65% coverage, but was that actually good,
          or would random boards get almost as far?
        </em>
      </p>
      <p>To judge the result, I measured coverage without training a model.</p>
      <p>
        I evaluated 45 random boards, five at each fill level from 10% to 90%,
        plus the all-zero and all-one boards. Coverage for individual boards
        rose steadily with the number of one bits, from 32.98% for the empty
        board to 51.76% for the full board. Together, the 47 boards reached
        64.45%, already close to the roughly 65% activation coverage reported
        for the ML run.
      </p>
      <figure className="figure--wide">
        <img
          src={publicAsset("/figures/activation-coverage-baseline.png")}
          alt="Two plots from a non-ML baseline. Per-board coverage rises with the number of one bits, while the cumulative union across 47 boards reaches 64.45 percent."
          width="2240"
          height="960"
        />
      </figure>
      <p>
        <em>
          What about the remaining 35%? Was that locked behind the winning
          board?
        </em>
      </p>
      <p>
        The known result boards reached some values that this baseline missed.
        The <code>TWO NOT TOUCH</code> board activated 469 previously unseen
        values at particular clocks, and the <code>(* TWO STARS *)</code> board
        activated 443.
      </p>
      <p>
        Adding representative boards for all five messages increased the
        combined coverage from 64.45% to 65.22%. Finding the successful board
        therefore did not unlock most of the remaining coverage.
      </p>
      <figure
        className="coverage-comparison"
        aria-label="Measured activation coverage on a zero to one hundred percent scale"
      >
        <div className="coverage-row">
          <div className="coverage-label">
            47-board non-ML baseline <strong>64.45%</strong>
          </div>
          <div className="coverage-track">
            <span style={{ width: "64.45%" }}></span>
          </div>
        </div>
        <div className="coverage-row">
          <div className="coverage-label">
            Baseline + five result boards <strong>65.22%</strong>
          </div>
          <div className="coverage-track">
            <span style={{ width: "65.22%" }}></span>
          </div>
        </div>
        <div className="coverage-scale">
          <span>0%</span>
          <span>100%</span>
        </div>
        <figcaption>
          Combined activation coverage. This comparison does not isolate the
          learned editor’s contribution.
        </figcaption>
      </figure>
      <h3>What the learned search found</h3>
      <p>
        <em>
          If the winning board wasn’t hiding at high coverage, where did the
          learned search actually end up?
        </em>
      </p>
      <p>
        When I started the search from random boards, it found only{" "}
        <code>BIG BANG</code>. It did not find <code>TWO NOT TOUCH</code> or{" "}
        <code>(* TWO STARS *)</code>.
      </p>
      <p>
        Earlier runs had received <code>EMPTY SKY</code> as a starting example.{" "}
        <code>TRY AGAIN</code> was the circuit’s common fallback output, so
        encountering it did not show that the model had discovered a special
        input.
      </p>
      <p>
        The baseline helps explain that result: the all-one board produces{" "}
        <code>BIG BANG</code>, and denser boards already tended to produce higher
        coverage.
      </p>
      <p>
        The search also performed substantial selection and evaluation of
        alternative edits, so this result alone doesn’t tell me how much the
        neural model contributed.
      </p>
      <p>
        It also exposed a limitation of the objective: activating more internal
        values did not necessarily move the search toward the successful board.
        The learned search explored circuit behavior, but the puzzle had already
        been solved by asking Z3 exactly which outputs were possible.
      </p>
      <footer className="article-footer">
        <span>Circuit notes / Jane Street ASIC puzzle</span>
        <a href="#top">Back to the beginning ↑</a>
      </footer>
    </article>
  );
}
