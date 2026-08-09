import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export const PhoneFrame: React.FC<{
  children: React.ReactNode;
  delay?: number;
}> = ({ children, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scaleSpring = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, stiffness: 80 },
  });

  const scale = interpolate(scaleSpring, [0, 1], [0.7, 1]);
  const opacity = interpolate(scaleSpring, [0, 1], [0, 1]);

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        opacity,
      }}
      className="relative"
    >
      {/* Phone body */}
      <div
        className="relative bg-artisangestion-slate-900 rounded-[48px] p-3 shadow-2xl"
        style={{
          width: 380,
          height: 780,
          boxShadow:
            "0 0 0 2px #334155, 0 25px 80px rgba(15, 23, 42, 0.5)",
        }}
      >
        {/* Notch */}
        <div className="absolute top-3 left-1/2 -translate-x-1/2 w-[140px] h-[32px] bg-artisangestion-slate-900 rounded-b-2xl z-10 flex items-center justify-center">
          <div className="w-16 h-4 bg-artisangestion-slate-800 rounded-full" />
        </div>

        {/* Screen */}
        <div className="w-full h-full bg-white rounded-[38px] overflow-hidden relative">
          {children}
        </div>
      </div>

      {/* Reflection glow */}
      <div
        className="absolute -inset-4 rounded-[56px] -z-10"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(37, 99, 235, 0.15) 0%, transparent 70%)",
        }}
      />
    </div>
  );
};
