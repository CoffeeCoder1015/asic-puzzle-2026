'use client';

import { useRef, useEffect, useLayoutEffect } from 'react';
import { beginAnimationWork, endAnimationWork } from '../animation-profile';

interface Rgb {
  r: number;
  g: number;
  b: number;
}

const FALLBACK_RGB: Rgb = { r: 255, g: 255, b: 255 };

export interface PaintRange {
  readonly start: number;
  readonly end: number;
}

const FULL_WIDTH_PAINT_RANGES: readonly PaintRange[] = [{ start: 0, end: 1 }];

const LetterGlitch = ({
  glitchColors = ['#2b4539', '#61dca3', '#61b3dc'],
  glitchSpeed = 50,
  centerVignette = false,
  outerVignette = true,
  smooth = true,
  lightMode = false,
  backgroundColor,
  className = '',
  getPaintRanges,
  characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$&*()-_+=/[]{};:<>.,0123456789'
}: {
  glitchColors: string[];
  glitchSpeed: number;
  centerVignette: boolean;
  outerVignette: boolean;
  smooth: boolean;
  lightMode?: boolean;
  backgroundColor?: string;
  className?: string;
  // Ordered, normalized horizontal ranges, read when the canvas is resized.
  getPaintRanges?: (container: HTMLElement) => readonly PaintRange[];
  characters: string;
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const paintRangeCallback = useRef(getPaintRanges);
  useLayoutEffect(() => {
    paintRangeCallback.current = getPaintRanges;
  }, [getPaintRanges]);
  const animationRef = useRef<number | null>(null);
  const letters = useRef<
    {
      char: string;
      rgb: Rgb;
      fromRgb: Rgb;
      targetRgb: Rgb;
      colorProgress: number;
    }[]
  >([]);
  const grid = useRef({ columns: 0, rows: 0 });
  const paint = useRef<{
    width: number;
    height: number;
    columnSpans: { start: number; end: number }[];
  }>({ width: 0, height: 0, columnSpans: [] });
  const context = useRef<CanvasRenderingContext2D | null>(null);
  const lastGlitchTime = useRef(Date.now());

  const lettersAndSymbols = Array.from(characters);

  const fontSize = 16;
  const charWidth = 10;
  const charHeight = 20;

  const getRandomChar = () => {
    return lettersAndSymbols[Math.floor(Math.random() * lettersAndSymbols.length)];
  };

  const getRandomColor = () => {
    return glitchColors[Math.floor(Math.random() * glitchColors.length)];
  };

  const hexToRgb = (hex: string) => {
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, (_m, r, g, b) => {
      return r + r + g + g + b + b;
    });

    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result
      ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        }
      : null;
  };

  // Interpolation happens in numbers, and the CSS string is only built at
  // paint time. Previously the formatted `rgb(...)` string was stored back
  // on the letter and fed to hexToRgb on the next frame, which returned null
  // and froze the transition after a single step.
  const mixRgb = (start: Rgb, end: Rgb, factor: number): Rgb => ({
    r: Math.round(start.r + (end.r - start.r) * factor),
    g: Math.round(start.g + (end.g - start.g) * factor),
    b: Math.round(start.b + (end.b - start.b) * factor)
  });

  const rgbToCss = ({ r, g, b }: Rgb) => `rgb(${r}, ${g}, ${b})`;

  // An unparseable entry in glitchColors must not stall the animation.
  const getRandomRgb = (): Rgb => hexToRgb(getRandomColor()) || FALLBACK_RGB;

  const calculateGrid = (width: number, height: number) => {
    const columns = Math.ceil(width / charWidth);
    const rows = Math.ceil(height / charHeight);
    return { columns, rows };
  };

  const initializeLetters = (columns: number, rows: number) => {
    grid.current = { columns, rows };
    const totalLetters = columns * rows;
    letters.current = Array.from({ length: totalLetters }, () => {
      const rgb = getRandomRgb();
      return {
        char: getRandomChar(),
        rgb,
        fromRgb: rgb,
        targetRgb: getRandomRgb(),
        colorProgress: 1
      };
    });
  };

  const resizeCanvas = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;
    if (!parent) return;

    const dpr = 1;
    const rect = parent.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;

    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${rect.height}px`;

    const { columns, rows } = calculateGrid(rect.width, rect.height);
    const columnSpans: { start: number; end: number }[] = [];
    const ctx = context.current;
    if (ctx) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.font = `${fontSize}px monospace`;
      ctx.textBaseline = 'top';

      let inkLeft = 0;
      let inkRight = 0;
      for (const char of lettersAndSymbols) {
        const metrics = ctx.measureText(char);
        inkLeft = Math.max(inkLeft, metrics.actualBoundingBoxLeft);
        inkRight = Math.max(inkRight, metrics.actualBoundingBoxRight);
      }
      // Keep glyphs whose overhang can reach a painted range, including a
      // pixel around measured ink for rasterization at fractional edges.
      inkLeft += 1;
      inkRight += 1;

      const getRanges = paintRangeCallback.current;
      const ranges = getRanges ? getRanges(parent) : FULL_WIDTH_PAINT_RANGES;
      for (const range of ranges) {
        const start = Math.max(0, Math.ceil((range.start * rect.width - inkRight) / charWidth));
        const end = Math.min(columns, Math.floor((range.end * rect.width + inkLeft) / charWidth) + 1);
        if (start >= end) continue;

        const previous = columnSpans[columnSpans.length - 1];
        if (previous && start <= previous.end) {
          previous.end = Math.max(previous.end, end);
        } else {
          columnSpans.push({ start, end });
        }
      }
    }
    paint.current = { width: rect.width, height: rect.height, columnSpans };
    initializeLetters(columns, rows);
    drawLetters();
  };

  const drawLetters = () => {
    if (!context.current || letters.current.length === 0) return;
    const workStart = beginAnimationWork();
    const ctx = context.current;
    const { width, height, columnSpans } = paint.current;
    const { columns, rows } = grid.current;
    ctx.clearRect(0, 0, width, height);

    let paintedLetters = 0;
    for (let row = 0; row < rows; row++) {
      for (const span of columnSpans) {
        for (let column = span.start; column < span.end; column++) {
          const letter = letters.current[row * columns + column];
          if (letter.char === ' ') continue;

          ctx.fillStyle = rgbToCss(letter.rgb);
          ctx.fillText(letter.char, column * charWidth, row * charHeight);
          paintedLetters++;
        }
      }
    }
    endAnimationWork('glyph', workStart, paintedLetters);
  };

  const updateLetters = () => {
    if (!letters.current || letters.current.length === 0) return;

    const updateCount = Math.max(1, Math.floor(letters.current.length * 0.05));

    for (let i = 0; i < updateCount; i++) {
      const index = Math.floor(Math.random() * letters.current.length);
      if (!letters.current[index]) continue;

      letters.current[index].char = getRandomChar();
      // A new transition starts from the colour currently on screen, so a
      // letter picked again mid-fade continues instead of jumping.
      letters.current[index].fromRgb = letters.current[index].rgb;
      letters.current[index].targetRgb = getRandomRgb();

      if (!smooth) {
        letters.current[index].rgb = letters.current[index].targetRgb;
        letters.current[index].colorProgress = 1;
      } else {
        letters.current[index].colorProgress = 0;
      }
    }
  };

  const handleSmoothTransitions = () => {
    let needsRedraw = false;
    letters.current.forEach(letter => {
      if (letter.colorProgress < 1) {
        letter.colorProgress += 0.05;
        if (letter.colorProgress > 1) letter.colorProgress = 1;

        letter.rgb = mixRgb(letter.fromRgb, letter.targetRgb, letter.colorProgress);
        needsRedraw = true;
      }
    });

    return needsRedraw;
  };

  const animate = () => {
    const updateStart = beginAnimationWork();
    const now = Date.now();
    let needsRedraw = false;
    if (now - lastGlitchTime.current >= glitchSpeed) {
      updateLetters();
      needsRedraw = true;
      lastGlitchTime.current = now;
    }

    if (smooth) {
      needsRedraw = handleSmoothTransitions() || needsRedraw;
    }

    endAnimationWork('glyph-update', updateStart, letters.current.length);
    if (needsRedraw) drawLetters();

    animationRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    context.current = canvas.getContext('2d');
    resizeCanvas();
    animate();

    let resizeTimeout: ReturnType<typeof setTimeout>;

    const handleResize = () => {
      clearTimeout(resizeTimeout);
      resizeTimeout = setTimeout(() => {
        cancelAnimationFrame(animationRef.current as number);
        resizeCanvas();
        animate();
      }, 100);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      clearTimeout(resizeTimeout);
      cancelAnimationFrame(animationRef.current!);
      window.removeEventListener('resize', handleResize);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [glitchSpeed, smooth]);

  return (
    <div
      className={`relative w-full h-full overflow-hidden ${className}`}
      style={{ backgroundColor: backgroundColor || (lightMode ? '#ffffff' : '#000000') }}
    >
      <canvas ref={canvasRef} className="block w-full h-full" />
      {outerVignette && (
        <div
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{
            background: lightMode
              ? 'radial-gradient(circle, rgba(255,255,255,0) 58%, rgba(255,255,255,0.96) 100%)'
              : 'radial-gradient(circle, rgba(0,0,0,0) 60%, rgba(0,0,0,1) 100%)'
          }}
        ></div>
      )}
      {centerVignette && (
        <div
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          style={{
            background: lightMode
              ? 'radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0) 60%)'
              : 'radial-gradient(circle, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 60%)'
          }}
        ></div>
      )}
    </div>
  );
};

export default LetterGlitch;
