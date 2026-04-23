import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export const BarChart: React.FC<{
  delay: number;
}> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const months = [
    { label: "Nov", value: 1200 },
    { label: "Déc", value: 1850 },
    { label: "Jan", value: 1400 },
    { label: "Fév", value: 2100 },
    { label: "Mar", value: 1780 },
    { label: "Avr", value: 2640 },
  ];

  const maxValue = Math.max(...months.map((m) => m.value));

  return (
    <div
      className="bg-white rounded-2xl border border-ventura-slate-200 p-7 shadow-sm"
      style={{
        opacity: interpolate(
          frame - delay,
          [0, 15],
          [0, 1],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        ),
        transform: `translateY(${interpolate(
          frame - delay,
          [0, 15],
          [40, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        )}px)`,
      }}
    >
      <div className="flex items-center gap-3 mb-6">
        <svg
          width="22"
          height="22"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#2563EB"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="12" y1="20" x2="12" y2="10" />
          <line x1="18" y1="20" x2="18" y2="4" />
          <line x1="6" y1="20" x2="6" y2="16" />
        </svg>
        <span className="text-base font-bold text-ventura-slate-900">
          Évolution du CA (6 mois)
        </span>
      </div>

      <div className="flex items-end gap-4 h-[160px]">
        {months.map((month, idx) => {
          const barGrow = spring({
            frame: frame - delay - 20 - idx * 5,
            fps,
            config: { damping: 12, stiffness: 60 },
          });

          const barHeight = interpolate(
            barGrow,
            [0, 1],
            [0, (month.value / maxValue) * 140]
          );

          return (
            <div
              key={month.label}
              className="flex-1 flex flex-col items-center justify-end gap-2"
            >
              {/* Value label */}
              <span
                className="text-xs font-bold text-ventura-slate-500"
                style={{
                  opacity: interpolate(
                    barGrow,
                    [0.5, 1],
                    [0, 1],
                    {
                      extrapolateLeft: "clamp",
                      extrapolateRight: "clamp",
                    }
                  ),
                }}
              >
                {month.value.toLocaleString("fr-FR")} €
              </span>

              {/* Bar */}
              <div
                className="w-full rounded-t-lg"
                style={{
                  height: barHeight,
                  background: `linear-gradient(180deg, #2563EB 0%, rgba(37, 99, 235, 0.4) 100%)`,
                }}
              />

              {/* Month label */}
              <span className="text-xs font-semibold text-ventura-slate-500 mt-1">
                {month.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
