import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { KpiCard } from "../components/KpiCard";
import { BarChart } from "../components/BarChart";
import { VenturaLogo } from "../components/VenturaLogo";

// Scene 2: "Le Tableau de Bord" (5-15s / 300 frames within sequence)
// Shows a simplified Ventura Dashboard with animated KPIs

const DashboardHeader: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const slideDown = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  return (
    <div
      style={{
        opacity: interpolate(slideDown, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(slideDown, [0, 1], [-30, 0])}px)`,
      }}
      className="bg-ventura-slate-900 px-12 py-5 flex items-center justify-between"
    >
      <div className="flex items-center gap-4">
        {/* Real Logo icon using VenturaLogo component */}
        <VenturaLogo size={40} delay={delay + 10} white showText={false} />
        <span className="text-white font-bold text-lg tracking-tight">
          Ventura Dashboard
        </span>
      </div>
      <div className="flex gap-2">
        <div className="w-3.5 h-3.5 rounded-full bg-red-400" />
        <div className="w-3.5 h-3.5 rounded-full bg-yellow-400" />
        <div className="w-3.5 h-3.5 rounded-full bg-green-400" />
      </div>
    </div>
  );
};

const OverlayText: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({
    frame: frame - delay,
    fps,
    config: { damping: 12, stiffness: 60 },
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 60,
        left: 0,
        right: 0,
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(appear, [0, 1], [30, 0])}px)`,
      }}
      className="flex justify-center"
    >
      <div className="bg-ventura-blue/95 backdrop-blur-sm px-10 py-5 rounded-2xl shadow-2xl">
        <span className="text-white text-3xl font-extrabold tracking-tight">
          Votre entreprise, sous contrôle.
        </span>
      </div>
    </div>
  );
};

const SidebarMock: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame - delay,
    [0, 20],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const navItems = [
    { label: "Tableau de bord", active: true },
    { label: "Rapports", active: false },
    { label: "Devis", active: false },
    { label: "Factures", active: false },
    { label: "Mon entreprise", active: false },
    { label: "Mes clients", active: false },
  ];

  return (
    <div
      style={{ opacity }}
      className="w-[220px] bg-white border-r border-ventura-slate-200 flex flex-col"
    >
      {/* Nav section */}
      <div className="p-4 pt-6">
        <span className="text-[10px] font-bold text-ventura-slate-500 uppercase tracking-widest px-3">
          Menu Principal
        </span>
        <div className="mt-3 flex flex-col gap-1">
          {navItems.map((item) => (
            <div
              key={item.label}
              className={`px-3 py-2.5 rounded-xl text-sm font-semibold ${
                item.active
                  ? "bg-ventura-blue text-white"
                  : "text-ventura-slate-500"
              }`}
            >
              {item.label}
            </div>
          ))}
        </div>
      </div>

      {/* User footer */}
      <div className="mt-auto p-4 border-t border-ventura-slate-200 bg-ventura-slate-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-ventura-blue text-white flex items-center justify-center text-xs font-bold">
            P
          </div>
          <div>
            <div className="text-xs font-bold text-ventura-slate-900">
              Pierre Martin
            </div>
            <div className="text-[10px] text-ventura-slate-500">
              Martin Plomberie
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export const Scene2Dashboard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene entrance
  const sceneEntry = spring({
    frame,
    fps,
    config: { damping: 15, stiffness: 40 },
  });
  const sceneScale = interpolate(sceneEntry, [0, 1], [0.92, 1]);
  const sceneOpacity = interpolate(sceneEntry, [0, 1], [0, 1]);

  // Scene exit
  const exitOpacity = interpolate(
    frame,
    [290, 315],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Welcome header
  const welcomeDelay = 15;

  return (
    <AbsoluteFill
      style={{
        opacity: sceneOpacity * exitOpacity,
      }}
      className="bg-ventura-slate-100 flex items-center justify-center"
    >
      {/* Background subtle radial gradient */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at top left, rgba(37, 99, 235, 0.06) 0%, transparent 60%)",
        }}
      />

      {/* Dashboard window */}
      <div
        style={{
          width: 1600,
          height: 900,
          transform: `scale(${sceneScale})`,
        }}
        className="bg-white rounded-3xl shadow-2xl overflow-hidden border border-ventura-slate-200 flex flex-col"
      >
        {/* Top bar */}
        <DashboardHeader delay={8} />

        {/* Content area with sidebar */}
        <div className="flex-1 flex min-h-0">
          {/* Sidebar */}
          <SidebarMock delay={12} />

          {/* Main content */}
          <div className="flex-1 p-8 overflow-hidden">
            {/* Welcome */}
            <div
              style={{
                opacity: interpolate(
                  frame - welcomeDelay,
                  [0, 15],
                  [0, 1],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                ),
                transform: `translateY(${interpolate(
                  frame - welcomeDelay,
                  [0, 15],
                  [20, 0],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
                )}px)`,
              }}
              className="mb-6"
            >
              <h2 className="text-2xl font-extrabold text-ventura-slate-900 tracking-tight">
                Bienvenue, Pierre 👋
              </h2>
              <p className="text-sm text-ventura-slate-500 mt-1">
                Vue d'ensemble de{" "}
                <strong className="text-ventura-slate-900">
                  Martin Plomberie
                </strong>
              </p>
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-4 gap-4 mb-6">
              <KpiCard
                label="CA du mois (TTC)"
                value="2 640 €"
                targetNumber={2640}
                animateValue={true}
                icon={
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 12V8H6a2 2 0 01-2-2c0-1.1.9-2 2-2h12v4" />
                    <path d="M4 6v12c0 1.1.9 2 2 2h14v-4" />
                    <path d="M18 12a2 2 0 000 4h4v-4z" />
                  </svg>
                }
                iconBg="bg-blue-50"
                subText="↗ 18% vs mois précédent"
                subColor="text-ventura-success"
                delay={30}
              />
              <KpiCard
                label="Encours client"
                value="1 250 €"
                icon={
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 2v20l4-2 4 2 4-2 4 2V2l-4 2-4-2-4 2z" />
                    <line x1="8" y1="10" x2="16" y2="10" />
                    <line x1="8" y1="14" x2="14" y2="14" />
                  </svg>
                }
                iconBg="bg-amber-50"
                subText="Factures non encaissées"
                delay={40}
              />
              <KpiCard
                label="Factures en retard"
                value="1"
                icon={
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                }
                iconBg="bg-red-50"
                subText="480 € à recouvrer"
                subColor="text-ventura-danger"
                delay={50}
              />
              <KpiCard
                label="Pipeline devis"
                value="4 800 €"
                icon={
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <path d="M12 6v6l4 2" />
                  </svg>
                }
                iconBg="bg-purple-50"
                subText="En attente de conversion"
                delay={60}
              />
            </div>

            {/* Chart */}
            <div className="grid grid-cols-1">
              <BarChart delay={55} />
            </div>
          </div>
        </div>
      </div>

      {/* Overlay text */}
      <OverlayText delay={200} />
    </AbsoluteFill>
  );
};
