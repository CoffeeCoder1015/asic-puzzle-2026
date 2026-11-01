/** Recorded circuit witnesses, in the original serial bit order. */
export type CircuitMessage = {
  message: string;
  bits: string;
  label: string;
  caption?: string;
  success: boolean;
};

export const MESSAGES: CircuitMessage[] = [
  {
    message: "EMPTY SKY",
    bits: "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    label: "Empty 11 by 11 board",
    success: false,
  },
  {
    message: "BIG BANG",
    bits: "1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
    label: "Completely filled 11 by 11 board",
    success: false,
  },
  {
    message: "TRY AGAIN",
    bits: "1111110101101000110011011010111010110110001111110001110000001100011111111010000001111101011100111011111100001000001011110",
    label: "Irregular 11 by 11 rejection board",
    success: false,
  },
  {
    message: "TWO NOT TOUCH",
    bits: "0100000001001000010000000000010100000011000010000001000100000001000001100000000000000101000001000010010100000000110000000",
    label:
      "11 by 11 board with two filled positions per row and column and touching pairs",
    caption: "Two filled positions in every row and column, but some touch.",
    success: false,
  },
  {
    message: "(* TWO STARS *)",
    bits: "0000000101010000100000000000010101010000000000001010000001000001000000100000101000010000000100000010000010010001010000000",
    label: "Successful 11 by 11 two-star board",
    caption:
      "Two filled positions in every row and column, with none touching.",
    success: true,
  },
];

/** The fifteen accepted warm-up register pairs, in Boolean-term order. */
export const SUCCESS_PAIRS: readonly (readonly [number, number])[] = [
  [255, 241],
  [247, 249],
  [251, 245],
  [243, 253],
  [253, 243],
  [245, 251],
  [249, 247],
  [241, 255],
  [254, 242],
  [246, 250],
  [250, 246],
  [242, 254],
  [252, 244],
  [244, 252],
  [248, 248],
];
