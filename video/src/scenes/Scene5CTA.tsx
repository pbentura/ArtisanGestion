import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { ArtisanGestionLogo } from "../components/ArtisanGestionLogo";

// Scene 5 — Appel à l'action (33–40s / 210 frames within sequence)

export const Scene5CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Background reveal
  const bgReveal = spring({ frame, fps, config: { damping: 20, stiffness: 60 } });
  const bgScale = interpolate(bgReveal, [0, 1], [1.1, 1]);

  // Logo
  const logoDelay = 8;

  // Tagline
  const taglineSpring = spring({ frame: frame - 22, fps, config: { damping: 15, stiffness: 60 } });
  const taglineY = interpolate(taglineSpring, [0, 1], [40, 0]);
  const taglineOpacity = interpolate(taglineSpring, [0, 1], [0, 1]);

  // Sub-tagline
  const subDelay = 38;
  const subOpacity = interpolate(frame - subDelay, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const subY = interpolate(frame - subDelay, [0, 15], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // CTA Button
  const buttonSpring = spring({ frame: frame - 52, fps, config: { damping: 12, stiffness: 80 } });
  const buttonScale = interpolate(buttonSpring, [0, 1], [0.8, 1]);
  const buttonOpacity = interpolate(buttonSpring, [0, 1], [0, 1]);

  // Button pulse
  const pulsePhase = Math.sin((frame - 72) * 0.08);
  const pulseScale = frame > 72 ? 1 + pulsePhase * 0.025 : 1;

  // Trust badges
  const badgeSpring = spring({ frame: frame - 75, fps, config: { damping: 15, stiffness: 60 } });

  // Sparkles orbiting
  const sparkles = Array.from({ length: 12 }, (_, i) => {
    const angle = (i / 12) * Math.PI * 2;
    const baseRadius = 380 + (i % 3) * 60;
    const radius = baseRadius + Math.sin(frame * 0.04 + i) * 25;
    const x = 960 + Math.cos(angle + frame * 0.006) * radius;
    const y = 540 + Math.sin(angle + frame * 0.006) * radius * 0.55;
    const sparkleOpacity = interpolate(frame - 15 - i * 3, [0, 20], [0, 0.5], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const size = 3 + Math.sin(frame * 0.1 + i * 2) * 2;
    return { x, y, opacity: sparkleOpacity, size };
  });

  return (
    <AbsoluteFill>
      {/* Blue gradient background */}
      <AbsoluteFill
        style={{
          transform: `scale(${bgScale})`,
          background: "linear-gradient(135deg, #1D4ED8 0%, #2563EB 45%, #3B82F6 100%)",
        }}
      />

      {/* Radial overlay */}
      <div
        className="absolute inset-0"
        style={{ background: "radial-gradient(ellipse at center, rgba(255,255,255,0.10) 0%, transparent 70%)" }}
      />

      {/* Grid pattern */}
      <AbsoluteFill style={{ opacity: 0.05 }}>
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
            boxShadow: "0 0 8px rgba(255,255,255,0.8)",
          }}
        />
      ))}

      {/* Content */}
      <AbsoluteFill className="flex flex-col items-center justify-center gap-8">
        {/* Logo */}
        <ArtisanGestionLogo size={120} delay={logoDelay} white showText />

        {/* Tagline */}
        <div
          style={{ transform: `translateY(${taglineY}px)`, opacity: taglineOpacity }}
          className="text-center max-w-[1100px] px-8"
        >
          <h2 className="text-6xl font-extrabold text-white tracking-tight leading-tight">
            Prêt à transformer votre gestion ?
          </h2>
        </div>

        {/* Sub-tagline */}
        <div
          style={{ opacity: subOpacity, transform: `translateY(${subY}px)` }}
          className="text-center max-w-[800px] px-8"
        >
          <p className="text-xl text-white/80 font-medium">
            Rejoignez plus de 500 artisans et PME qui gagnent du temps chaque jour.
          </p>
        </div>

        {/* CTA Button */}
        <div
          style={{ transform: `scale(${buttonScale * pulseScale})`, opacity: buttonOpacity }}
          className="mt-2"
        >
          <div
            className="flex items-center gap-3 bg-white rounded-full px-10 py-5 shadow-2xl"
            style={{ boxShadow: "0 0 0 0 rgba(255,255,255,0.2), 0 20px 60px rgba(0,0,0,0.3)" }}
          >
            <span className="text-artisangestion-blue text-xl font-extrabold tracking-tight">
              Commencer gratuitement
            </span>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </div>
        </div>

        {/* Trial pill */}
        <div
          style={{
            opacity: interpolate(frame - 65, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
          className="bg-white/15 backdrop-blur-sm border border-white/20 px-5 py-2 rounded-full"
        >
          <span className="text-white text-sm font-semibold">14 jours d'essai • Sans carte bancaire</span>
        </div>

        {/* Trust badges */}
        <div
          style={{
            opacity: interpolate(badgeSpring, [0, 1], [0, 1]),
            transform: `translateY(${interpolate(badgeSpring, [0, 1], [20, 0])}px)`,
          }}
          className="flex items-center gap-8 mt-4"
        >
          {[
            { text: "Sans engagement", icon: "M22 11.08V12a10 10 0 1 1-5.93-9.14M22 4L12 14.01l-3-3" },
            { text: "Setup en 2 minutes", icon: "M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" },
            { text: "Support réactif", icon: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" },
          ].map((b) => (
            <div key={b.text} className="flex items-center gap-2 text-white/75">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d={b.icon} />
              </svg>
              <span className="text-sm font-semibold">{b.text}</span>
            </div>
          ))}
        </div>

        {/* URL */}
        <div
          style={{
            opacity: interpolate(frame - 95, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
          className="mt-6 text-white/60 font-medium text-lg tracking-wide"
        >
          artisangestion.com
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
