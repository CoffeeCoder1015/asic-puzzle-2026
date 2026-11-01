"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import AnimatedContent from "@/components/react-bits/AnimatedContent";
import { MESSAGES, SUCCESS_PAIRS } from "@/lib/circuit-data";
import { Board } from "./board";

function useMounted() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  return mounted;
}

const INITIAL_REGISTERS = { a: 255, b: 241 };
const BIT_POSITIONS = Array.from({ length: 8 }, (_, bit) => bit);

export function WarmupExplorer() {
  const mounted = useMounted();
  const [registers, setRegisters] = useState(INITIAL_REGISTERS);
  const [drafts, setDrafts] = useState({ a: "255", b: "241" });
  const invalid = (name: "a" | "b") =>
    !/^\d+$/.test(drafts[name]) || Number(drafts[name]) > 255;
  const hasError = invalid("a") || invalid("b");
  const sum = registers.a + registers.b;

  function editRegister(name: "a" | "b", text: string) {
    setDrafts((previous) => ({ ...previous, [name]: text }));
    if (/^\d+$/.test(text) && Number(text) <= 255) {
      setRegisters((previous) => ({ ...previous, [name]: Number(text) }));
    }
  }

  function setExample([a, b]: readonly [number, number]) {
    setRegisters({ a, b });
    setDrafts({ a: String(a), b: String(b) });
  }

  function nextValidAnswer() {
    const current = hasError
      ? -1
      : SUCCESS_PAIRS.findIndex(
          ([a, b]) => a === registers.a && b === registers.b,
        );
    setExample(SUCCESS_PAIRS[(current + 1) % SUCCESS_PAIRS.length]);
  }

  function flipBit(name: "a" | "b", bit: number) {
    const value = registers[name] ^ (1 << bit);
    setRegisters((previous) => ({ ...previous, [name]: value }));
    setDrafts((previous) => ({ ...previous, [name]: String(value) }));
  }

  return (
    <div className="explanation warmup-panel">
      <h3 className="figure-title" id="warmup-title">
        A + B = 496
      </h3>
      <p className="figure-hint">Change a register or flip a bit.</p>
      <div className="warmup-registers">
        {(["a", "b"] as const).map((name) => (
          <section
            className="warmup-register"
            aria-label={`Register ${name.toUpperCase()}`}
            key={name}
          >
            <label className="warmup-register-label" htmlFor={`warmup-${name}`}>
              Register {name.toUpperCase()}
              <Input
                id={`warmup-${name}`}
                type="text"
                inputMode="numeric"
                value={drafts[name]}
                disabled={!mounted}
                aria-invalid={invalid(name)}
                aria-describedby="warmup-error"
                required
                onChange={(event) => editRegister(name, event.target.value)}
              />
            </label>
            <div className="warmup-bits">
              {BIT_POSITIONS.map((bit) => (
                <Button
                  key={bit}
                  type="button"
                  className="warmup-bit"
                  variant="outline"
                  disabled={!mounted}
                  aria-label={`${name.toUpperCase()}${bit}, weight ${1 << bit}`}
                  aria-pressed={Boolean(registers[name] & (1 << bit))}
                  onClick={() => flipBit(name, bit)}
                >
                  <span>
                    {name.toUpperCase()}
                    {bit}
                  </span>
                  <strong key={(registers[name] >> bit) & 1}>
                    {(registers[name] >> bit) & 1}
                  </strong>
                </Button>
              ))}
            </div>
          </section>
        ))}
      </div>
      <p
        className="warmup-error"
        id="warmup-error"
        role="alert"
        hidden={!hasError}
      >
        {hasError
          ? "Enter a whole number from 0 to 255. The figure still shows the last valid registers."
          : ""}
      </p>
      <div className="warmup-result" data-success={sum === 496}>
        <p className="warmup-sum">
          <output>
            {registers.a} + {registers.b} = {sum}
          </output>
        </p>
        <p
          className="warmup-status"
          role="status"
          aria-live="polite"
          aria-atomic="true"
        >
          success = {sum === 496 ? 1 : 0}
        </p>
      </div>
      <div className="warmup-literals">
        {(["a", "b"] as const).map((name) => (
          <code key={name}>
            {BIT_POSITIONS.map(
              (bit) =>
                `${registers[name] & (1 << bit) ? "" : "¬"}${name.toUpperCase()}${bit}`,
            ).join(" ∧ ")}
          </code>
        ))}
      </div>
      <div className="warmup-examples" hidden={!mounted}>
        <Button
          type="button"
          variant="outline"
          onClick={() => setExample(SUCCESS_PAIRS[0])}
        >
          Reset
        </Button>
        <Button type="button" variant="outline" onClick={nextValidAnswer}>
          Next valid answer
        </Button>
      </div>
    </div>
  );
}

const CANDIDATES = [
  { byte: "R", messageIndex: 2 },
  { byte: "W", messageIndex: 3 },
  { byte: "A", messageIndex: null },
] as const;

export function CandidateExplorer() {
  const mounted = useMounted();
  const [chosen, setChosen] =
    useState<(typeof CANDIDATES)[number]["byte"]>("R");

  return (
    <div className="explanation candidate-explorer" id="candidate-explorer">
      <div className="figure-heading">
        <p className="figure-title">Test a next byte after T</p>
        <span className="example-label">Recorded Z3 results</span>
      </div>
      <div className="solver-model" key={`constraints-${chosen}`}>
        <div>
          <strong>Require an output</strong>
          <code className="requested-prefix">T{chosen}</code>
        </div>
        <span aria-hidden="true">→</span>
        <div>
          <strong>Constrain every clock</strong>
          <span>121 input + 30 readout clocks</span>
        </div>
        <span aria-hidden="true">→</span>
        <div>
          <strong>Find an input</strong>
          <small>121 bits for Z3 to choose</small>
        </div>
      </div>
      <div className="candidate-controls" hidden={!mounted}>
        {CANDIDATES.map(({ byte }) => (
          <Button
            type="button"
            variant="outline"
            key={byte}
            aria-pressed={chosen === byte}
            onClick={() => setChosen(byte)}
          >
            {byte}
          </Button>
        ))}
      </div>
      <AnimatedContent
        key={mounted ? chosen : "static"}
        className="explanation-reveal"
        trigger="mount"
        distance={8}
        duration={0.35}
        initialOpacity={0.6}
        style={{ visibility: "visible" }}
      >
        <div className="candidate-panels">
          {CANDIDATES.map(({ byte, messageIndex }) => {
            const message =
              messageIndex === null ? null : MESSAGES[messageIndex];
            return (
              <section
                key={byte}
                className={`candidate-panel${message ? "" : " candidate-panel--impossible"}`}
                hidden={mounted && chosen !== byte}
                aria-label={`T${byte}: ${message ? "SAT" : "UNSAT"}`}
              >
                <div className="candidate-answer">
                  <div>
                    <code>
                      {message ? (
                        <>
                          <mark>{message.message.slice(0, 2)}</mark>
                          {message.message.slice(2)}
                        </>
                      ) : (
                        "TA"
                      )}
                    </code>
                    <span
                      className={`status status--${message ? "yes" : "no"}`}
                    >
                      {message ? "SAT" : "UNSAT"}
                    </span>
                  </div>
                  {!message && <p>No matching input exists.</p>}
                </div>
                {message && (
                  <>
                    <svg
                      className="query-signal"
                      viewBox="0 0 260 80"
                      aria-hidden="true"
                    >
                      <path pathLength="1" d="M0 40H90L125 15H200L235 40H260" />
                      <path d="M250 33L260 40L250 47" />
                    </svg>
                    <div className="query-witness">
                      <Board message={message} />
                      <p>One matching input</p>
                    </div>
                  </>
                )}
              </section>
            );
          })}
        </div>
      </AnimatedContent>
      <p
        className="candidate-status visually-hidden"
        role="status"
        aria-live="polite"
      >
        {mounted
          ? `T${chosen}, ${chosen === "A" ? "UNSAT. No matching input exists." : "SAT. One matching input shown."}`
          : ""}
      </p>
    </div>
  );
}

const ENUMERATION_STEPS = [
  { excluded: "none", next: "R", action: "Exclude R →" },
  { excluded: "R", next: "W", action: "Exclude W →" },
  { excluded: "R, W", next: null, action: "Complete" },
] as const;

export function PrefixEnumeration() {
  const mounted = useMounted();
  const [index, setIndex] = useState(0);
  const nextButton = useRef<HTMLButtonElement>(null);
  const replayRequested = useRef(false);

  useEffect(() => {
    if (index === 0 && replayRequested.current) {
      nextButton.current?.focus();
      replayRequested.current = false;
    }
  }, [index]);

  return (
    <div
      className={`explanation enumeration${mounted ? " is-interactive" : ""}`}
      id="prefix-enumeration"
    >
      <div className="figure-heading">
        <p className="figure-title">Exclude each byte you find</p>
      </div>
      <div
        className="enumeration-history"
        aria-label="Already found and excluded from this query"
        hidden={!mounted || index === 0}
      >
        <span>Already found · excluded from this query</span>
        {ENUMERATION_STEPS.slice(0, index).map((step) => (
          <code key={step.next}>{step.next}</code>
        ))}
      </div>
      <AnimatedContent
        key={mounted ? index : "static"}
        className="explanation-reveal"
        trigger="mount"
        distance={8}
        duration={0.35}
        initialOpacity={0.6}
        style={{ visibility: "visible" }}
      >
        <ol className="enumeration-steps">
          {ENUMERATION_STEPS.map((step, stepIndex) => (
            <li key={step.excluded} hidden={mounted && index !== stepIndex}>
              <div className="query enumeration-excluded">
                <span>Excluded after T</span>
                <code>{step.excluded}</code>
              </div>
              <div className="query-result">
                <code>T → {step.next ?? "?"}</code>
                <span className={`status status--${step.next ? "yes" : "no"}`}>
                  {step.next ? "SAT" : "UNSAT"}
                </span>
              </div>
              {!step.next && (
                <p>
                  <code>R</code> and <code>W</code> are the only next bytes
                  after <code>T</code>.
                </p>
              )}
            </li>
          ))}
        </ol>
      </AnimatedContent>
      {mounted && (
        <>
          <div className="enumeration-controls">
            <Button
              type="button"
              variant="outline"
              disabled={index === 0}
              onClick={() => setIndex(index - 1)}
            >
              ← Previous
            </Button>
            <p className="enumeration-status" role="status" aria-live="polite">
              Query {index + 1} of {ENUMERATION_STEPS.length}
            </p>
            <Button
              ref={nextButton}
              type="button"
              data-action="next"
              disabled={index === ENUMERATION_STEPS.length - 1}
              onClick={() => setIndex(index + 1)}
            >
              {ENUMERATION_STEPS[index].action}
            </Button>
            {index === ENUMERATION_STEPS.length - 1 && (
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  replayRequested.current = true;
                  setIndex(0);
                }}
              >
                Replay
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
