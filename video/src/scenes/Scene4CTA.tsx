import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { VenturaLogo } from "../components/VenturaLogo";

// Scene 4: "Appel à l'Action" (25-30s / 150 frames within sequence)

export const Scene4CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene entrance - blue background slides in
  const bgReveal = spring({
    frame,
    fps,
    config: { damping: 20, stiffness: 60 },
  });
  const bgScale = interpolate(bgReveal, [0, 1], [1.1, 1]);

  // Logo
  const logoDelay = 10;

  // Tagline
  const taglineSpring = spring({
    frame: frame - 25,
    fps,
    config: { damping: 15, stiffness: 60 },
  });
  const taglineY = interpolate(taglineSpring, [0, 1], [40, 0]);
  const taglineOpacity = interpolate(taglineSpring, [0, 1], [0, 1]);

  // CTA Button
  const buttonSpring = spring({
    frame: frame - 50,
    fps,
    config: { damping: 12, stiffness: 80 },
  });
  const buttonScale = interpolate(buttonSpring, [0, 1], [0.8, 1]);
  const buttonOpacity = interpolate(buttonSpring, [0, 1], [0, 1]);

  // Button pulse
  const pulsePhase = Math.sin((frame - 70) * 0.08);
  const pulseScale = frame > 70 ? 1 + pulsePhase * 0.03 : 1;

  // Bottom badges
  const badgeSpring = spring({
    frame: frame - 70,
    fps,
    config: { damping: 15, stiffness: 60 },
  });

  // Particle sparkles
  const sparkles = Array.from({ length: 8 }, (_, i) => {
    const angle = (i / 8) * Math.PI * 2;
    const radius = 300 + Math.sin(frame * 0.04 + i) * 30;
    const x = 960 + Math.cos(angle + frame * 0.008) * radius;
    const y = 540 + Math.sin(angle + frame * 0.008) * radius;
    const sparkleOpacity = interpolate(
      frame - 20 - i * 3,
      [0, 15],
      [0, 0.4],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
    );
    const size = 4 + Math.sin(frame * 0.1 + i * 2) * 2;

    return { x, y, opacity: sparkleOpacity, size };
  });

  return (
    <AbsoluteFill>
      {/* Blue background */}
      <AbsoluteFill
        style={{
          transform: `scale(${bgScale})`,
          background:
            "linear-gradient(135deg, #1D4ED8 0%, #2563EB 40%, #3B82F6 100%)",
        }}
      />

      {/* Radial overlay */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(255,255,255,0.08) 0%, transparent 70%)",
        }}
      />

      {/* Grid pattern */}
      <AbsoluteFill style={{ opacity: 0.04 }}>
        <div
          className="w-full h-full"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)",
            backgroundSize: "80px 80px",
          }}
        />
      </AbsoluteFill>

      {/* Sparkles */}
      {sparkles.map((s, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: s.x,
            top: s.y,
            width: s.size,
            height: s.size,
            borderRadius: "50%",
            background: "white",
            opacity: s.opacity,
          }}
        />
      ))}

      {/* Content */}
      <AbsoluteFill className="flex flex-col items-center justify-center gap-10">
        {/* Logo (using real asset) */}
        <VenturaLogo size={120} delay={logoDelay} white showText={false} />

        {/* Tagline */}
        <div
          style={{
            transform: `translateY(${taglineY}px)`,
            opacity: taglineOpacity,
          }}
          className="text-center max-w-[1000px] px-8"
        >
          <h2 className="text-6xl font-extrabold text-white tracking-tight leading-tight">
            La gestion par les plombiers,<br />pour les plombiers.
          </h2>
        </div>

        {/* CTA Button */}
        <div
          style={{
            transform: `scale(${buttonScale * pulseScale})`,
            opacity: buttonOpacity,
          }}
          className="mt-4"
        >
          <div
            className="flex items-center gap-3 bg-white rounded-full px-10 py-5 shadow-2xl cursor-pointer hover:bg-ventura-slate-50 transition-colors"
            style={{
              boxShadow: "0 0 0 0 rgba(255,255,255,0.2), 0 20px 60px rgba(0,0,0,0.3)",
            }}
          >
            <span className="text-ventura-blue text-xl font-extrabold tracking-tight">
              Testez gratuitement pendant 3 mois
            </span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </div>
        </div>

        {/* Trust badges */}
        <div
          style={{
            opacity: interpolate(badgeSpring, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(badgeSpring, [0, 1], [20, 0])}px)`,
          }}
          className="flex items-center gap-8 mt-2"
        >
          {["Sans carte bancaire", "Setup en 2 minutes", "Support réactif"].map((text) => (
            <div key={text} className="flex items-center gap-2 text-white/70">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
              <span className="text-sm font-semibold">{text}</span>
            </div>
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
