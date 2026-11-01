"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";

export function ExtractionFigure() {
  const figure = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = figure.current!;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    let visible = false;
    let timeline: gsap.core.Timeline;
    const context = gsap.context(() => {
      timeline = gsap
        .timeline({ paused: true })
        .from(".component-outline", {
          opacity: 0,
          duration: 0.65,
          stagger: 0.16,
        })
        .from(
          ".physical-layer",
          { y: 9, opacity: 0.2, duration: 0.8, stagger: 0.15 },
          0.3,
        )
        .from(
          ".extraction-stage--net .contact-shape",
          {
            scaleY: 0,
            transformOrigin: "center top",
            duration: 0.6,
            stagger: 0.3,
          },
          1.3,
        )
        .from(
          ".extraction-stage--net .net-line",
          { strokeDashoffset: 1, duration: 1.1, ease: "power1.inOut" },
          2.1,
        )
        .from(
          ".cell-pin--net",
          { opacity: 0.3, duration: 0.45, stagger: 0.12 },
          3.1,
        )
        .from(
          ".extraction-stage:last-child .net-line",
          { opacity: 0.1, duration: 0.5 },
          3.6,
        );
    }, element);
    function updatePlayback() {
      if (reducedMotion.matches) timeline.progress(1).pause();
      else if (visible && !document.hidden) timeline.play();
      else timeline.pause();
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        visible = entry.isIntersecting;
        updatePlayback();
      },
      { threshold: 0.15 },
    );
    observer.observe(element);
    document.addEventListener("visibilitychange", updatePlayback);
    reducedMotion.addEventListener("change", updatePlayback);
    updatePlayback();
    return () => {
      observer.disconnect();
      document.removeEventListener("visibilitychange", updatePlayback);
      reducedMotion.removeEventListener("change", updatePlayback);
      context.revert();
    };
  }, []);

  return (
    <figure className="figure--wide extraction-figure" ref={figure}>
      <div
        className="extraction-stages"
        role="img"
        aria-label="Three-stage GDS extraction. First, touching shapes are joined within each conductive layer. Second, via1 joins met2 to met1 and mcon joins met1 to li1. One continuous highlighted component reaches cell_1.X and cell_0.A2 and is labeled net 1. Third, KLayout records net ID 1 on both reached pins."
      >
        <section className="extraction-stage">
          <header>
            <span className="stage-number">1</span>
            <h3>Join shapes within each layer</h3>
          </header>
          <svg viewBox="0 0 240 185" aria-hidden="true">
            <text className="diagram-label diagram-label--strong" x="4" y="31">
              met2
            </text>
            <line
              className="layer-guide"
              x1="42"
              y1="27"
              x2="232"
              y2="27"
            ></line>
            <path
              className="layer-shape layer-shape--met2"
              d="M51 18h48v18h43V18h38v18h-47v15H95V36H51z"
            ></path>
            <rect
              className="layer-shape layer-shape--met2"
              x="198"
              y="18"
              width="25"
              height="18"
              rx="2"
            ></rect>
            <path
              className="component-outline"
              d="M47 14h56v18h35V14h46v26h-45v15H91V40H47z"
            ></path>
            <text className="diagram-label diagram-label--strong" x="4" y="92">
              met1
            </text>
            <line
              className="layer-guide"
              x1="42"
              y1="88"
              x2="232"
              y2="88"
            ></line>
            <path
              className="layer-shape layer-shape--met1"
              d="M51 79h38v18h38V79h33v18h-29v15H84V97H51z"
            ></path>
            <rect
              className="layer-shape layer-shape--met1"
              x="181"
              y="79"
              width="42"
              height="18"
              rx="2"
            ></rect>
            <path
              className="component-outline"
              d="M47 75h46v18h30V75h41v26h-29v15H80v-15H47z"
            ></path>
            <text className="diagram-label diagram-label--strong" x="4" y="153">
              li1
            </text>
            <line
              className="layer-guide"
              x1="42"
              y1="149"
              x2="232"
              y2="149"
            ></line>
            <rect
              className="layer-shape layer-shape--li1"
              x="51"
              y="140"
              width="70"
              height="18"
              rx="2"
            ></rect>
            <rect
              className="layer-shape layer-shape--li1"
              x="121"
              y="140"
              width="48"
              height="18"
              rx="2"
            ></rect>
            <rect
              className="layer-shape layer-shape--li1"
              x="190"
              y="140"
              width="33"
              height="18"
              rx="2"
            ></rect>
            <rect
              className="component-outline"
              x="47"
              y="136"
              width="126"
              height="26"
              rx="4"
            ></rect>
          </svg>
        </section>
        <section className="extraction-stage extraction-stage--net">
          <header>
            <span className="stage-number">2</span>
            <h3>Connect the complete physical net</h3>
          </header>
          <svg
            className="physical-stack"
            viewBox="0 0 320 240"
            aria-hidden="true"
          >
            <g className="physical-layer">
              <path
                className="layer-side layer-side--met2"
                d="M55 28L108 54H280V61H108L55 35Z"
              />
              <path
                className="layer-shape layer-shape--met2"
                d="M55 28H227L280 54H108Z"
              />
              <text
                className="diagram-label diagram-label--strong"
                x="4"
                y="38"
              >
                met2
              </text>
            </g>
            <g className="physical-layer">
              <path
                className="layer-side layer-side--met1"
                d="M55 76L108 102H280V109H108L55 83Z"
              />
              <path
                className="layer-shape layer-shape--met1"
                d="M55 76H227L280 102H108Z"
              />
              <text
                className="diagram-label diagram-label--strong"
                x="4"
                y="86"
              >
                met1
              </text>
            </g>
            <g className="physical-layer">
              <path
                className="layer-side layer-side--li1"
                d="M55 124L108 150H280V157H108L55 131Z"
              />
              <path
                className="layer-shape layer-shape--li1"
                d="M55 124H227L280 150H108Z"
              />
              <text
                className="diagram-label diagram-label--strong"
                x="4"
                y="134"
              >
                li1
              </text>
            </g>
            <path className="contact-shape" d="M128 42H140V90H128Z" />
            <text className="diagram-label" x="145" y="68">
              via1
            </text>
            <path className="contact-shape" d="M218 90H230V138H218Z" />
            <text className="diagram-label" x="235" y="116">
              mcon
            </text>
            <rect
              className="cell-body"
              x="43"
              y="185"
              width="105"
              height="47"
              rx="7"
            />
            <rect
              className="cell-pin cell-pin--net"
              x="88"
              y="180"
              width="18"
              height="10"
              rx="2"
            />
            <text
              className="diagram-label diagram-label--strong"
              x="111"
              y="197"
            >
              X
            </text>
            <text
              className="diagram-label diagram-label--strong"
              x="54"
              y="209"
            >
              cell_1
            </text>
            <text className="diagram-label" x="54" y="223">
              and2_2
            </text>
            <rect
              className="cell-body"
              x="172"
              y="185"
              width="105"
              height="47"
              rx="7"
            />
            <rect
              className="cell-pin cell-pin--net"
              x="216"
              y="180"
              width="18"
              height="10"
              rx="2"
            />
            <text
              className="diagram-label diagram-label--strong"
              x="239"
              y="197"
            >
              A2
            </text>
            <text
              className="diagram-label diagram-label--strong"
              x="183"
              y="209"
            >
              cell_0
            </text>
            <text className="diagram-label" x="183" y="223">
              o21a_2
            </text>
            <path
              className="net-line"
              pathLength="1"
              d="M95 42H134V90H224V138H97V185V138H225V185"
            />
          </svg>
        </section>
        <section className="extraction-stage">
          <header>
            <span className="stage-number">3</span>
            <h3>Assign net IDs to reached pins</h3>
          </header>
          <svg viewBox="0 0 240 185" aria-hidden="true">
            <rect
              className="cell-body"
              x="9"
              y="45"
              width="91"
              height="95"
              rx="7"
            ></rect>
            <text className="diagram-label diagram-label--strong" x="20" y="65">
              cell_1
            </text>
            <text className="diagram-label" x="20" y="80">
              and2_2
            </text>
            <rect
              className="cell-pin"
              x="4"
              y="91"
              width="10"
              height="10"
              rx="2"
            ></rect>
            <text className="diagram-label" x="19" y="100">
              A · 103
            </text>
            <rect
              className="cell-pin"
              x="4"
              y="113"
              width="10"
              height="10"
              rx="2"
            ></rect>
            <text className="diagram-label" x="19" y="122">
              B · 21
            </text>
            <rect
              className="cell-pin cell-pin--net"
              x="95"
              y="91"
              width="10"
              height="10"
              rx="2"
            ></rect>
            <text className="diagram-label diagram-label--strong" x="64" y="87">
              X · 1
            </text>
            <rect
              className="cell-body"
              x="140"
              y="45"
              width="91"
              height="95"
              rx="7"
            ></rect>
            <text
              className="diagram-label diagram-label--strong"
              x="151"
              y="65"
            >
              cell_0
            </text>
            <text className="diagram-label" x="151" y="80">
              o21a_2
            </text>
            <rect
              className="cell-pin cell-pin--net"
              x="135"
              y="91"
              width="10"
              height="10"
              rx="2"
            ></rect>
            <text
              className="diagram-label diagram-label--strong"
              x="151"
              y="100"
            >
              A2 · 1
            </text>
            <rect
              className="cell-pin"
              x="135"
              y="113"
              width="10"
              height="10"
              rx="2"
            ></rect>
            <text className="diagram-label" x="151" y="122">
              A1 · 23
            </text>
            <path className="net-line" d="M105 96C118 80 123 112 135 96"></path>
            <text
              className="diagram-label diagram-label--strong"
              x="105"
              y="76"
            >
              net 1
            </text>
          </svg>
        </section>
      </div>
      <figcaption>
        Schematic extraction. The highlighted pins share net 1.
      </figcaption>
    </figure>
  );
}
