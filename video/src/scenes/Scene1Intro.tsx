import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { ArtisanGestionLogo } from "../components/ArtisanGestionLogo";

// Scene 1 — Intro / Problématique (0–5.5s / 165 frames)
// Chaotic floating admin icons → blue sweep reveal → ArtisanGestion logo

const FloatingIcon: React.FC<{
  x: number;
  y: number;
  size: number;
  delay: number;
  rotation: number;
  icon: "folder" | "receipt" | "clock" | "alert" | "excel" | "mail";
  sweepStart: number;
}> = ({ x, y, size, delay, rotation, icon, sweepStart }) => {
  const frame = useCurrentFrame();

  const floatY = Math.sin((frame + delay * 10) * 0.06) * 18;
  const floatX = Math.cos((frame + delay * 7) * 0.04) * 12;
  const rot = rotation + Math.sin((frame + delay * 5) * 0.03) * 8;

  const opacity = interpolate(frame - delay, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const exitOpacity = interpolate(frame - sweepStart, [0, 18], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const getIcon = () => {
    switch (icon) {
      case "folder":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /></svg>
        );
      case "receipt":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1z" /><path d="M16 8H8" /><path d="M16 12H8" /><path d="M13 16H8" /></svg>
        );
      case "clock":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
        );
      case "alert":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
        );
      case "excel":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="8" y1="13" x2="16" y2="13" /><line x1="8" y1="17" x2="16" y2="17" /></svg>
        );
      case "mail":
        return (
          <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="4" width="20" height="16" rx="2" /><path d="m22 7-10 6L2 7" /></svg>
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
      className="bg-white/70 backdrop-blur-sm p-4 rounded-2xl shadow-lg border border-white/60"
    >
      {getIcon()}
    </div>
  );
};

export const Scene1Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const text1Opacity = interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const text1Y = interpolate(frame, [10, 25], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const text2Opacity = interpolate(frame, [35, 50], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const text2Y = interpolate(frame, [35, 50], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const sweepStart = 110;
  const sweep = spring({
    frame: frame - sweepStart,
    fps,
    config: { damping: 20, stiffness: 60, mass: 1.2 },
  });

  const sweepX = interpolate(sweep, [0, 1], [-2200, 2200]);
  const logoOpacity = interpolate(sweep, [0.35, 0.7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const logoScale = interpolate(sweep, [0.35, 0.7], [0.85, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const taglineOpacity = interpolate(frame - sweepStart - 25, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const taglineY = interpolate(frame - sweepStart - 25, [0, 15], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const exitOpacity = interpolate(frame, [148, 165], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill className="bg-artisangestion-slate-50 overflow-hidden" style={{ opacity: exitOpacity }}>
      {/* Background dotted grid */}
      <AbsoluteFill style={{ opacity: 0.03 }}>
        <div
          className="w-full h-full"
          style={{
            backgroundImage: "radial-gradient(circle, #0F172A 1px, transparent 1px)",
            backgroundSize: "60px 60px",
          }}
        />
      </AbsoluteFill>

      {/* Chaotic icons */}
      <FloatingIcon x={260} y={210} size={40} delay={0} rotation={-15} icon="receipt" sweepStart={sweepStart} />
      <FloatingIcon x={1400} y={160} size={45} delay={10} rotation={20} icon="excel" sweepStart={sweepStart} />
      <FloatingIcon x={480} y={700} size={35} delay={20} rotation={10} icon="clock" sweepStart={sweepStart} />
      <FloatingIcon x={1600} y={780} size={42} delay={5} rotation={-10} icon="mail" sweepStart={sweepStart} />
      <FloatingIcon x={180} y={840} size={50} delay={15} rotation={30} icon="alert" sweepStart={sweepStart} />
      <FloatingIcon x={1320} y={630} size={36} delay={25} rotation={-5} icon="folder" sweepStart={sweepStart} />
      <FloatingIcon x={1500} y={390} size={44} delay={30} rotation={12} icon="receipt" sweepStart={sweepStart} />
      <FloatingIcon x={380} y={430} size={32} delay={12} rotation={-20} icon="excel" sweepStart={sweepStart} />

      {/* Problem text */}
      <AbsoluteFill className="flex flex-col items-center justify-center gap-4 px-8">
        <h1
          style={{ opacity: text1Opacity * (1 - sweep), transform: `translateY(${text1Y}px)` }}
          className="text-6xl font-extrabold text-artisangestion-slate-900 tracking-tight text-center"
        >
          Encore sur vos factures
        </h1>
        <h1
          style={{ opacity: text2Opacity * (1 - sweep), transform: `translateY(${text2Y}px)` }}
          className="text-6xl font-extrabold text-artisangestion-blue tracking-tight text-center"
        >
          à cette heure-ci ?
        </h1>
      </AbsoluteFill>

      {/* Blue sweep reveal */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: sweepX,
          width: 2200,
          height: "100%",
          background: "linear-gradient(90deg, transparent 0%, #2563EB 40%, #2563EB 60%, transparent 100%)",
          transform: "skewX(-15deg)",
          zIndex: 50,
        }}
      />

      {/* Logo + tagline reveal */}
      <AbsoluteFill style={{ opacity: logoOpacity, zIndex: 60 }} className="flex flex-col items-center justify-center gap-10">
        <div style={{ transform: `scale(${logoScale})` }}>
          <ArtisanGestionLogo size={130} delay={sweepStart + 12} showText />
        </div>
        <div
          style={{ opacity: taglineOpacity, transform: `translateY(${taglineY}px)` }}
          className="text-3xl font-bold text-artisangestion-slate-500 tracking-tight"
        >
          La gestion simplifiée pour artisans & PME.
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
