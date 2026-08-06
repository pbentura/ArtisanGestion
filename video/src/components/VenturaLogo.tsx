import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

// VenturaLogo - High-fidelity implementation of the real logo from video/public/logo.svg
// Allows for individual part animation and perfect rendering

export const VenturaLogo: React.FC<{
  size?: number;
  delay?: number;
  showText?: boolean;
  white?: boolean;
}> = ({ size = 64, delay = 0, showText = true, white = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 100, mass: 0.8 },
  });

  const textOpacity = interpolate(
    frame - delay - 10,
    [0, 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const textSlide = interpolate(
    frame - delay - 10,
    [0, 15],
    [20, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Individual part animations
  const docPop = spring({
    frame: frame - delay - 5,
    fps,
    config: { damping: 10, stiffness: 120 },
  });

  const checkPop = spring({
    frame: frame - delay - 15,
    fps,
    config: { damping: 8, stiffness: 150 },
  });

  return (
    <div className="flex items-center gap-6">
      {/* Icon Container */}
      <div
        style={{
          width: size,
          height: size,
          transform: `scale(${entrance})`,
          filter: white ? "brightness(0) invert(1)" : "none",
        }}
        className="relative"
      >
        <svg viewBox="0 0 512 512" className="w-full h-full drop-shadow-xl">
          <defs>
            <linearGradient id="logoMainGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#3B82F6" />
              <stop offset="100%" stopColor="#2563EB" />
            </linearGradient>
            <linearGradient id="logoAccentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="100%" stopColor="#059669" />
            </linearGradient>
          </defs>
          
          {/* Hexagon Background */}
          <g transform="translate(256, 256)">
            <path 
              d="M0,-180 L155.88,-90 L155.88,90 L0,180 L-155.88,90 L-155.88,-90 Z" 
              fill="url(#logoMainGradient)"
            />
            {/* Brillance */}
            <path 
              d="M0,-180 L155.88,-90 L155.88,90 L0,180 L-155.88,90 L-155.88,-90 Z" 
              fill="white" 
              fillOpacity="0.1"
            />
          </g>
          
          {/* Document Icon */}
          <g transform={`translate(256, 256) scale(${docPop})`}>
            <g transform="translate(-60, -80)">
              <rect x="0" y="0" width="120" height="150" rx="12" fill="white"/>
              <path d="M85,0 L120,0 L120,35 Z" fill="#E5E7EB"/>
              <path d="M85,0 L120,35 L85,35 Z" fill="white"/>
              
              {/* Lines */}
              <rect x="15" y="25" width="60" height="8" rx="4" fill="#E5E7EB"/>
              <rect x="15" y="45" width="90" height="6" rx="3" fill="#F3F4F6"/>
              <rect x="15" y="58" width="80" height="6" rx="3" fill="#F3F4F6"/>
              <rect x="15" y="71" width="85" height="6" rx="3" fill="#F3F4F6"/>
              <rect x="15" y="84" width="50" height="6" rx="3" fill="#F3F4F6"/>
            </g>
          </g>

          {/* Badge Check */}
          <g transform={`translate(256, 256) scale(${checkPop})`}>
            <circle cx="35" cy="40" r="28" fill="url(#logoAccentGradient)" />
            <path 
              d="M23,40 L31,48 L47,32" 
              stroke="white" 
              strokeWidth="5" 
              strokeLinecap="round" 
              strokeLinejoin="round"
              fill="none"
            />
          </g>
        </svg>
      </div>

      {/* Text */}
      {showText && (
        <span
          style={{
            opacity: textOpacity,
            transform: `translateX(${textSlide}px)`,
            fontSize: size * 0.52,
            color: white ? "white" : "#0F172A",
            letterSpacing: "-0.02em",
          }}
          className="font-sans font-extrabold tracking-tight whitespace-nowrap"
        >
          Artisan<span style={{ color: white ? "rgba(255,255,255,0.85)" : "#2563EB" }}>Gestion</span>
        </span>
      )}
    </div>
  );
};
