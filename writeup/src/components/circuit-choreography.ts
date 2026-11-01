export const CIRCUIT_STORY = {
  expandStart: 0,
  collapseStart: 0.5,
  manualStart: 1,
} as const;

function easeBetween(start: number, end: number, progress: number) {
  const fraction = Math.max(0, Math.min(1, (progress - start) / (end - start)));
  return fraction * fraction * (3 - 2 * fraction);
}

/** One opening revolution and one closing revolution, ending at the manual view. */
export function circuitPose(progress: number) {
  const expansion = easeBetween(0, 0.5, progress);
  const collapse = easeBetween(0.5, 1, progress);
  const spread = expansion * (1 - collapse);
  const angle = Math.atan2(7, 9) + (expansion + collapse) * Math.PI * 2;
  const radius = Math.hypot(7, 9) + spread * 2.7;
  return {
    angle,
    camera: [
      Math.sin(angle) * radius,
      6.5 + spread * 3.3 - (1 - expansion),
      Math.cos(angle) * radius,
    ],
    target: [0, 0.35 + spread + (1 - expansion) * 0.3, 0],
    spacing: (0.48 + expansion * 0.77) * (1 - collapse),
    light: Math.sin(progress * Math.PI) * 60,
  };
}
