import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export const KpiCard: React.FC<{
  label: string;
  value: string;
  icon: React.ReactNode;
  iconBg: string;
  subText: string;
  subColor?: string;
  delay: number;
  animateValue?: boolean;
  targetNumber?: number;
}> = ({
  label,
  value,
  icon,
  iconBg,
  subText,
  subColor = "text-artisangestion-slate-500",
  delay,
  animateValue = false,
  targetNumber,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideUp = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  const translateY = interpolate(slideUp, [0, 1], [60, 0]);
  const opacity = interpolate(slideUp, [0, 1], [0, 1]);

  // Animated number counting
  let displayValue = value;
  if (animateValue && targetNumber !== undefined) {
    const countProgress = spring({
      frame: frame - delay - 8,
      fps,
      config: { damping: 30, stiffness: 40, mass: 1.5 },
    });
    const currentNumber = Math.round(
      interpolate(countProgress, [0, 1], [0, targetNumber])
    );
    displayValue =
      currentNumber.toLocaleString("fr-FR") + " €";
  }

  return (
    <div
      style={{
        transform: `translateY(${translateY}px)`,
        opacity,
      }}
      className="bg-white rounded-2xl border border-artisangestion-slate-200 p-6 flex items-start gap-5 shadow-sm"
    >
      <div
        className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${iconBg}`}
      >
        {icon}
      </div>
      <div className="flex flex-col gap-1 min-w-0">
        <span className="text-xs font-semibold text-artisangestion-slate-500 uppercase tracking-widest">
          {label}
        </span>
        <span className="text-3xl font-extrabold text-artisangestion-slate-900 tracking-tight leading-tight">
          {displayValue}
        </span>
        <span className={`text-xs font-medium flex items-center gap-1 ${subColor}`}>
          {subText}
        </span>
      </div>
    </div>
  );
};
