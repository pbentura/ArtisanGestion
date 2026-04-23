import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { VenturaLogo } from "../components/VenturaLogo";

// Scene 1: "La Problématique" (0-5s / 150 frames)
// Displays chaotic floating paper icons, then reveals the Ventura logo

const FloatingIcon: React.FC<{
  x: number;
  y: number;
  size: number;
  delay: number;
  rotation: number;
  icon: "folder" | "receipt" | "clock" | "alert";
}> = ({ x, y, size, delay, rotation, icon }) => {
  const frame = useCurrentFrame();

  // Chaotic floating animation
  const floatY = Math.sin((frame + delay * 10) * 0.06) * 18;
  const floatX = Math.cos((frame + delay * 7) * 0.04) * 12;
  const rot = rotation + Math.sin((frame + delay * 5) * 0.03) * 8;

  // Fade in
  const opacity = interpolate(
    frame - delay,
    [0, 20],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Transition out (when blue sweep happens)
  const sweepStart = 110;
  const exitOpacity = interpolate(
    frame - sweepStart,
    [0, 15],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const getIcon = () => {
    switch (icon) {
      case "folder":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
        );
      case "receipt":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1z"/><path d="M16 8H8"/><path d="M16 12H8"/><path d="M13 16H8"/></svg>
        );
      case "clock":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        );
      case "alert":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        );
    }
  };

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(${floatX}px, ${floatY}px) rotate(${rot}deg)`,
        opacity: opacity * exitOpacity,
        color: "#64748B",
      }}
      className="bg-white/60 backdrop-blur-sm p-4 rounded-2xl shadow-lg border border-white/50"
    >
      {getIcon()}
    </div>
  );
};

export const Scene1Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animations for text
  const text1Opacity = interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const text1Y = interpolate(frame, [10, 25], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const text2Opacity = interpolate(frame, [35, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const text2Y = interpolate(frame, [35, 50], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Blue sweep transition
  const sweepStart = 110;
  const sweep = spring({
    frame: frame - sweepStart,
    fps,
    config: { damping: 20, stiffness: 60, mass: 1.2 },
  });

  const sweepX = interpolate(sweep, [0, 1], [-2000, 2000]);
  const logoOpacity = interpolate(sweep, [0.3, 0.6], [0, 1]);
  const logoScale = interpolate(sweep, [0.3, 0.6], [0.8, 1]);

  return (
    <AbsoluteFill className="bg-ventura-slate-50 overflow-hidden">
      {/* Background Grid */}
      <AbsoluteFill style={{ opacity: 0.03 }}>
        <div className="w-full h-full" style={{ backgroundImage: "radial-gradient(circle, #0F172A 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
      </AbsoluteFill>

      {/* Chaotic Icons */}
      <FloatingIcon x={300} y={200} size={40} delay={0} rotation={-15} icon="receipt" />
      <FloatingIcon x={1400} y={150} size={45} delay={10} rotation={20} icon="folder" />
      <FloatingIcon x={500} y={700} size={35} delay={20} rotation={10} icon="clock" />
      <FloatingIcon x={1600} y={800} size={40} delay={5} rotation={-10} icon="receipt" />
      <FloatingIcon x={200} y={850} size={50} delay={15} rotation={30} icon="alert" />
      <FloatingIcon x={1300} y={650} size={35} delay={25} rotation={-5} icon="folder" />
      <FloatingIcon x={1500} y={400} size={45} delay={30} rotation={12} icon="receipt" />
      <FloatingIcon x={400} y={450} size={30} delay={12} rotation={-20} icon="clock" />

      {/* Main Text */}
      <AbsoluteFill className="flex flex-col items-center justify-center gap-4">
        <h1
          style={{
            opacity: text1Opacity * (1 - sweep),
            transform: `translateY(${text1Y}px)`,
          }}
          className="text-6xl font-extrabold text-ventura-slate-900 tracking-tight"
        >
          Encore sur vos factures
        </h1>
        <h1
          style={{
            opacity: text2Opacity * (1 - sweep),
            transform: `translateY(${text2Y}px)`,
          }}
          className="text-6xl font-extrabold text-ventura-blue tracking-tight"
        >
          à cette heure-ci ?
        </h1>
      </AbsoluteFill>

      {/* Blue Sweep Reveal */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: sweepX,
          width: 2000,
          height: "100%",
          background: "linear-gradient(90deg, transparent 0%, #2563EB 40%, #2563EB 60%, transparent 100%)",
          transform: "skewX(-15deg)",
          zIndex: 50,
        }}
      />

      {/* Final Reveal (Logo) */}
      <AbsoluteFill
        style={{
          opacity: logoOpacity,
          zIndex: 60,
        }}
        className="flex flex-col items-center justify-center"
      >
        <div style={{ transform: `scale(${logoScale})` }}>
          <VenturaLogo size={120} delay={sweepStart + 10} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
