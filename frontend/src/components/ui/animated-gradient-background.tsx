import { motion } from "framer-motion";
import { useEffect, useRef } from "react";

const DEFAULT_COLORS = [
  "#050816",
  "#0B1B4A",
  "#1E3A8A",
  "#4F46E5",
  "#2563EB",
  "#7C5CFC",
  "#050816",
];
const DEFAULT_STOPS = [28, 42, 54, 66, 78, 90, 100];

interface AnimatedGradientBackgroundProps {
  startingGap?: number;
  breathing?: boolean;
  gradientColors?: string[];
  gradientStops?: number[];
  animationSpeed?: number;
  breathingRange?: number;
  topOffset?: number;
  className?: string;
}

/**
 * Breathing radial gradient — adapted from 21st.dev Animated Gradient Background
 * for BookMe indigo / cobalt palette.
 */
export function AnimatedGradientBackground({
  startingGap = 125,
  breathing = true,
  gradientColors = DEFAULT_COLORS,
  gradientStops = DEFAULT_STOPS,
  animationSpeed = 0.035,
  breathingRange = 6,
  topOffset = 0,
  className = "",
}: AnimatedGradientBackgroundProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (gradientColors.length !== gradientStops.length) return;

    let animationFrame = 0;
    let width = startingGap;
    let direction = 1;

    const tick = () => {
      if (breathing) {
        if (width >= startingGap + breathingRange) direction = -1;
        if (width <= startingGap - breathingRange) direction = 1;
        width += direction * animationSpeed;
      }

      const stops = gradientStops
        .map((stop, i) => `${gradientColors[i]} ${stop}%`)
        .join(", ");
      const gradient = `radial-gradient(${width}% ${width + topOffset}% at 50% 18%, ${stops})`;

      if (containerRef.current) {
        containerRef.current.style.background = gradient;
      }
      animationFrame = requestAnimationFrame(tick);
    };

    animationFrame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animationFrame);
  }, [
    startingGap,
    breathing,
    gradientColors,
    gradientStops,
    animationSpeed,
    breathingRange,
    topOffset,
  ]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 1.35 }}
      animate={{
        opacity: 1,
        scale: 1,
        transition: { duration: 1.8, ease: [0.25, 0.1, 0.25, 1] },
      }}
      className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`}
      aria-hidden
    >
      <div ref={containerRef} className="absolute inset-0" />
    </motion.div>
  );
}
