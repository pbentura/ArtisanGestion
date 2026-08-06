import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

export const BrowserFrame: React.FC<{
  children: React.ReactNode;
  delay?: number;
  url?: string;
  width?: number;
  height?: number;
}> = ({ children, delay = 0, url = "artisangestion.com", width = 1640, height = 920 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entrance = spring({
    frame: frame - delay,
    fps,
    config: { damping: 18, stiffness: 70 },
  });

  const scale = interpolate(entrance, [0, 1], [0.94, 1]);
  const opacity = interpolate(entrance, [0, 1], [0, 1]);

  return (
    <div
      style={{
        transform: `scale(${scale})`,
        opacity,
        width,
        height,
      }}
      className="bg-white rounded-2xl shadow-2xl overflow-hidden border border-ventura-slate-200 flex flex-col"
    >
      {/* Browser top bar */}
      <div className="bg-ventura-slate-100 px-5 py-3 flex items-center gap-3 border-b border-ventura-slate-200">
        {/* Traffic lights */}
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-[#FF5F57]" />
          <div className="w-3 h-3 rounded-full bg-[#FEBC2E]" />
          <div className="w-3 h-3 rounded-full bg-[#28C840]" />
        </div>
        {/* URL bar */}
        <div className="flex-1 mx-4 bg-white rounded-md px-4 py-1.5 flex items-center gap-2 border border-ventura-slate-200 shadow-sm">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#16A34A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <span className="text-xs font-medium text-ventura-slate-500">{url}</span>
        </div>
      </div>

      {/* Page content */}
      <div className="flex-1 overflow-hidden bg-white">{children}</div>
    </div>
  );
};
