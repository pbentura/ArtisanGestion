import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { KpiCard } from "../components/KpiCard";
import { BrowserFrame } from "../components/BrowserFrame";
import { ArtisanGestionLogo } from "../components/ArtisanGestionLogo";

// Scene 2 — Tableau de bord web (5–15.5s / 315 frames within sequence)
// Fidèle au vrai Dashboard.vue : header + shortcuts, 4 KPIs, évolution CA,
// Top 5 clients, factures impayées, donut taux de conversion.

const Sidebar: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const slideX = interpolate(frame - delay, [0, 20], [-30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const navItems = [
    { label: "Tableau de bord", active: true, icon: "M3 3h7v7H3zM14 3h7v7h-7zM14 14h7v7h-7zM3 14h7v7H3z" },
    { label: "Rapports", active: false, icon: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6" },
    { label: "Devis", active: false, icon: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M9 18l2 2 4-4" },
    { label: "Factures", active: false, icon: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z M14 2v6h6 M16 13H8 M16 17H8 M10 9H8" },
    { label: "Clients", active: false, icon: "M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" },
  ];

  return (
    <div
      style={{ opacity, transform: `translateX(${slideX}px)` }}
      className="w-[240px] bg-white border-r border-artisangestion-slate-200 flex flex-col"
    >
      <div className="px-5 pt-6 pb-5 flex items-center gap-2.5 border-b border-artisangestion-slate-100">
        <ArtisanGestionLogo size={32} delay={delay + 5} showText={false} />
        <span className="font-extrabold text-artisangestion-slate-900 tracking-tight text-[17px]">
          Artisan<span className="text-artisangestion-blue">Gestion</span>
        </span>
      </div>

      <div className="p-4 pt-5 flex-1">
        <span className="text-[10px] font-bold text-artisangestion-slate-400 uppercase tracking-widest px-3">
          Menu Principal
        </span>
        <div className="mt-3 flex flex-col gap-1">
          {navItems.map((item) => (
            <div
              key={item.label}
              className={`px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-3 ${
                item.active ? "bg-artisangestion-blue text-white shadow-md shadow-artisangestion-blue/30" : "text-artisangestion-slate-500"
              }`}
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d={item.icon} />
              </svg>
              {item.label}
            </div>
          ))}
        </div>

        <span className="text-[10px] font-bold text-artisangestion-slate-400 uppercase tracking-widest px-3 mt-6 block">
          Configuration
        </span>
        <div className="mt-3 flex flex-col gap-1">
          <div className="px-3 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-3 text-artisangestion-slate-500">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 21h18 M5 21V7l8-4v18 M19 21V11l-6-4" />
            </svg>
            Mon entreprise
          </div>
        </div>
      </div>

      <div className="mt-auto p-4 border-t border-artisangestion-slate-200 bg-artisangestion-slate-50">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-artisangestion-blue text-white flex items-center justify-center text-xs font-bold shadow-sm">
            PM
          </div>
          <div className="min-w-0">
            <div className="text-xs font-bold text-artisangestion-slate-900 truncate">Pierre Martin</div>
            <div className="text-[10px] text-artisangestion-slate-500 truncate">Martin Plomberie</div>
          </div>
        </div>
      </div>
    </div>
  );
};

const TopHeader: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame - delay, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{ opacity }}
      className="h-[56px] px-7 border-b border-artisangestion-slate-200 flex items-center justify-between bg-white"
    >
      <div className="flex items-center gap-3">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="18" x2="21" y2="18" />
        </svg>
        <span className="text-base font-bold text-artisangestion-slate-900">Tableau de bord</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          <div className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-artisangestion-danger border-2 border-white" />
        </div>
        <div className="w-9 h-9 rounded-full bg-artisangestion-slate-100 flex items-center justify-center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0F172A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5" /><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
          </svg>
        </div>
        <div className="bg-artisangestion-blue text-white px-4 py-2 rounded-lg text-xs font-bold shadow-sm">
          Mon compte
        </div>
      </div>
    </div>
  );
};

// Header with welcome + shortcuts (matches real dashboard-header)
const WelcomeHeader: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = spring({ frame: frame - delay, fps, config: { damping: 15, stiffness: 80 } });

  const shortcuts = [
    { label: "Nouveau Devis", icon: "M12 5v14M5 12h14" },
    { label: "Nouvelle Facture", icon: "M12 5v14M5 12h14" },
    { label: "Ajouter Client", icon: "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" },
  ];

  return (
    <div
      style={{
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(appear, [0, 1], [15, 0])}px)`,
      }}
      className="flex items-start justify-between gap-4 mb-5"
    >
      <div>
        <h2 className="text-[28px] font-extrabold text-artisangestion-slate-900 tracking-tight leading-tight">
          Bienvenue, Pierre
        </h2>
        <p className="text-sm text-artisangestion-slate-500 mt-1">
          Vue d'ensemble de <strong className="text-artisangestion-slate-900">Martin Plomberie</strong>
        </p>
      </div>
      <div className="flex gap-2">
        {shortcuts.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5 bg-artisangestion-blue text-white px-3.5 py-2 rounded-lg text-xs font-bold shadow-sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d={s.icon} />
            </svg>
            {s.label}
          </div>
        ))}
      </div>
    </div>
  );
};

// Bar chart matching the real SVG style (viewBox 420×200, grid lines, gradient bars)
const EvolutionChart: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const months = [
    { label: "Nov", value: 6200 },
    { label: "Déc", value: 8400 },
    { label: "Jan", value: 7100 },
    { label: "Fév", value: 9800 },
    { label: "Mar", value: 10576 },
    { label: "Avr", value: 12480 },
  ];
  const maxVal = Math.max(...months.map((m) => m.value));

  const cardAppear = interpolate(frame - delay, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const cardY = interpolate(frame - delay, [0, 15], [25, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{ opacity: cardAppear, transform: `translateY(${cardY}px)` }}
      className="bg-white border border-artisangestion-slate-200 rounded-2xl p-6 shadow-sm"
    >
      <div className="flex items-center gap-2 mb-4">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="20" x2="12" y2="10" /><line x1="18" y1="20" x2="18" y2="4" /><line x1="6" y1="20" x2="6" y2="16" />
        </svg>
        <span className="text-sm font-bold text-artisangestion-slate-900">Évolution du CA (6 mois)</span>
      </div>

      <svg viewBox="0 0 420 200" preserveAspectRatio="xMidYMid meet" className="w-full">
        <defs>
          <linearGradient id="barGradDash" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#2563EB" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#2563EB" stopOpacity="0.4" />
          </linearGradient>
        </defs>

        {/* Grid lines */}
        {[0, 1, 2, 3].map((i) => (
          <line key={i} x1="40" x2="410" y1={10 + i * 50} y2={10 + i * 50} stroke="#E2E8F0" strokeWidth="0.5" strokeDasharray="4,4" />
        ))}

        {/* Bars */}
        {months.map((m, idx) => {
          const barSpring = spring({
            frame: frame - delay - 20 - idx * 6,
            fps,
            config: { damping: 14, stiffness: 70 },
          });
          const h = interpolate(barSpring, [0, 1], [0, (m.value / maxVal) * 155]);
          const y = 170 - h;
          const valOpacity = interpolate(barSpring, [0.6, 1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

          return (
            <g key={m.label}>
              <rect x={55 + idx * 62} y={y} width={36} height={h} rx="4" fill="url(#barGradDash)" />
              <text
                x={55 + idx * 62 + 18}
                y={y - 5}
                textAnchor="middle"
                fill="#64748B"
                fontSize="9"
                fontWeight="600"
                style={{ opacity: valOpacity }}
              >
                {m.value.toLocaleString("fr-FR")} €
              </text>
              <text x={55 + idx * 62 + 18} y="188" textAnchor="middle" fill="#64748B" fontSize="11" fontWeight="600">
                {m.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// Top 5 clients (matches real top-clients-list)
const TopClients: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const clients = [
    { name: "Martin Durand", ca: 8200 },
    { name: "Sophie Lefevre", ca: 5400 },
    { name: "Marc Moreau", ca: 3100 },
    { name: "Julie Petit", ca: 1800 },
    { name: "Laurent Roy", ca: 1200 },
  ];
  const maxCa = Math.max(...clients.map((c) => c.ca));

  const cardAppear = interpolate(frame - delay, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{ opacity: cardAppear }}
      className="bg-white border border-artisangestion-slate-200 rounded-2xl p-6 shadow-sm"
    >
      <div className="flex items-center gap-2 mb-4">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2 M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
        </svg>
        <span className="text-sm font-bold text-artisangestion-slate-900">Top 5 Clients</span>
      </div>

      <div className="flex flex-col gap-3.5">
        {clients.map((c, idx) => {
          const barSpring = spring({
            frame: frame - delay - 15 - idx * 8,
            fps,
            config: { damping: 16, stiffness: 80 },
          });
          const fillWidth = interpolate(barSpring, [0, 1], [0, (c.ca / maxCa) * 100]);
          const rowOpacity = interpolate(frame - delay - 10 - idx * 8, [0, 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          return (
            <div key={c.name} style={{ opacity: rowOpacity }} className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-lg bg-artisangestion-slate-100 text-artisangestion-slate-900 flex items-center justify-center text-xs font-extrabold flex-shrink-0">
                {idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold text-artisangestion-slate-900 mb-1 truncate">{c.name}</div>
                <div className="w-full h-1.5 bg-artisangestion-slate-100 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${fillWidth}%`,
                      background: "linear-gradient(90deg, #2563EB, #8B5CF6)",
                    }}
                  />
                </div>
              </div>
              <span className="text-xs font-bold text-artisangestion-slate-900 whitespace-nowrap">
                {c.ca.toLocaleString("fr-FR")} €
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Factures impayées list
const FacturesImpayees: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const factures = [
    { num: "F-2026-0038", client: "Martin Durand", amount: 480, retard: 12 },
    { num: "F-2026-0035", client: "Sophie Lefevre", amount: 1000, retard: 5 },
  ];

  const cardAppear = interpolate(frame - delay, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{ opacity: cardAppear }}
      className="bg-white border border-artisangestion-slate-200 rounded-2xl p-6 shadow-sm"
    >
      <div className="flex items-center gap-2 mb-4">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 2v20l4-2 4 2 4-2 4 2V2l-4 2-4-2-4 2z" /><line x1="8" y1="10" x2="16" y2="10" /><line x1="8" y1="14" x2="14" y2="14" />
        </svg>
        <span className="text-sm font-bold text-artisangestion-slate-900">Factures impayées</span>
      </div>

      <div className="flex flex-col gap-1">
        {factures.map((f, idx) => {
          const rowSpring = spring({
            frame: frame - delay - 15 - idx * 10,
            fps,
            config: { damping: 16, stiffness: 90 },
          });
          return (
            <div
              key={f.num}
              style={{
                opacity: interpolate(rowSpring, [0, 1], [0, 1]),
                transform: `translateX(${interpolate(rowSpring, [0, 1], [-15, 0])}px)`,
              }}
              className="flex items-center justify-between py-3 px-3.5 rounded-xl"
            >
              <div className="flex flex-col gap-0.5 min-w-0">
                <span className="text-sm font-bold text-artisangestion-slate-900">{f.num}</span>
                <span className="text-xs text-artisangestion-slate-500">{f.client}</span>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span className="text-sm font-bold text-artisangestion-slate-900">
                  {f.amount.toLocaleString("fr-FR")},00 €
                </span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-50 text-artisangestion-danger">
                  {f.retard}j de retard
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Donut chart for taux de conversion + rapport stats
const ConversionDonut: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const cardAppear = interpolate(frame - delay, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const targetPct = 68;
  const donutSpring = spring({
    frame: frame - delay - 15,
    fps,
    config: { damping: 18, stiffness: 60 },
  });
  const currentPct = interpolate(donutSpring, [0, 1], [0, targetPct]);
  const dashLength = (currentPct / 100) * 301.6;

  const rapports = [
    { label: "30 derniers jours", value: 14, color: "#2563EB" },
    { label: "En cours", value: 3, color: "#F59E0B" },
    { label: "Terminés", value: 11, color: "#16A34A" },
  ];

  return (
    <div
      style={{ opacity: cardAppear }}
      className="bg-white border border-artisangestion-slate-200 rounded-2xl p-6 shadow-sm flex flex-col"
    >
      <div className="flex items-center gap-2 mb-3">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
        </svg>
        <span className="text-sm font-bold text-artisangestion-slate-900">Taux de conversion</span>
      </div>

      <div className="flex justify-center mb-3">
        <svg viewBox="0 0 120 120" width="110" height="110">
          <circle cx="60" cy="60" r="48" fill="none" stroke="#E2E8F0" strokeWidth="12" />
          <circle
            cx="60" cy="60" r="48" fill="none" stroke="#2563EB" strokeWidth="12" strokeLinecap="round"
            strokeDasharray={`${dashLength} 301.6`}
            transform="rotate(-90 60 60)"
          />
          <text x="60" y="56" textAnchor="middle" fill="#0F172A" fontSize="22" fontWeight="800">
            {Math.round(currentPct)}%
          </text>
          <text x="60" y="73" textAnchor="middle" fill="#64748B" fontSize="9">
            13/19 devis
          </text>
        </svg>
      </div>

      <div className="flex flex-col gap-2.5 border-t border-artisangestion-slate-200 pt-3">
        {rapports.map((r) => {
          const rowOpacity = interpolate(frame - delay - 30, [0, 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <div key={r.label} style={{ opacity: rowOpacity }} className="flex items-center gap-2 text-xs">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={r.color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
              </svg>
              <span className="flex-1 text-artisangestion-slate-500 font-medium">{r.label}</span>
              <span className="font-extrabold text-artisangestion-slate-900">{r.value}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const OverlayText: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 60 } });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 50,
        left: 0,
        right: 0,
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(appear, [0, 1], [30, 0])}px)`,
      }}
      className="flex justify-center"
    >
      <div className="bg-artisangestion-blue/95 backdrop-blur-sm px-10 py-5 rounded-2xl shadow-2xl">
        <span className="text-white text-3xl font-extrabold tracking-tight">
          Votre entreprise, sous contrôle.
        </span>
      </div>
    </div>
  );
};

export const Scene2Dashboard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sceneEntry = spring({ frame, fps, config: { damping: 16, stiffness: 45 } });
  const sceneScale = interpolate(sceneEntry, [0, 1], [0.9, 1]);
  const sceneOpacity = interpolate(sceneEntry, [0, 1], [0, 1]);

  const exitOpacity = interpolate(frame, [295, 315], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ opacity: sceneOpacity * exitOpacity }} className="bg-artisangestion-slate-100 flex items-center justify-center">
      <div
        className="absolute inset-0"
        style={{ background: "radial-gradient(ellipse at top left, rgba(37, 99, 235, 0.07) 0%, transparent 60%)" }}
      />

      <div style={{ transform: `scale(${sceneScale})` }}>
        <BrowserFrame delay={4} url="app.artisangestion.com/dashboard" width={1640} height={920}>
          <div className="flex h-full">
            <Sidebar delay={12} />
            <div className="flex-1 flex flex-col min-w-0">
              <TopHeader delay={10} />
              <div className="flex-1 p-7 overflow-hidden">
                <WelcomeHeader delay={18} />

                {/* KPI Grid */}
                <div className="grid grid-cols-4 gap-4 mb-5">
                  <KpiCard
                    label="CA du mois (TTC)"
                    value="12 480 €"
                    targetNumber={12480}
                    animateValue={true}
                    icon={
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4" /><path d="M4 6v12c0 1.1.9 2 2 2h14v-4" /><path d="M18 12a2 2 0 0 0 0 4h4v-4z" />
                      </svg>
                    }
                    iconBg="bg-blue-50"
                    subText="↗ 18% vs mois précédent"
                    subColor="text-artisangestion-success"
                    delay={30}
                  />
                  <KpiCard
                    label="Encours client"
                    value="3 250 €"
                    icon={
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M4 2v20l4-2 4 2 4-2 4 2V2l-4 2-4-2-4 2z" /><line x1="8" y1="10" x2="16" y2="10" /><line x1="8" y1="14" x2="14" y2="14" />
                      </svg>
                    }
                    iconBg="bg-blue-50"
                    subText="Factures non encaissées"
                    delay={42}
                  />
                  <KpiCard
                    label="Factures en retard"
                    value="2"
                    icon={
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
                      </svg>
                    }
                    iconBg="bg-red-50"
                    subText="1 480 € à recouvrer"
                    subColor="text-artisangestion-danger"
                    delay={54}
                  />
                  <KpiCard
                    label="Pipeline devis"
                    value="8 400 €"
                    icon={
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
                      </svg>
                    }
                    iconBg="bg-blue-50"
                    subText="En attente de conversion"
                    delay={66}
                  />
                </div>

                {/* Charts row 1: Evolution CA (60%) + Top 5 Clients (40%) */}
                <div className="grid grid-cols-[1.5fr_1fr] gap-4 mb-5">
                  <EvolutionChart delay={75} />
                  <TopClients delay={90} />
                </div>

                {/* Charts row 2: Factures impayées (60%) + Taux de conversion (40%) */}
                <div className="grid grid-cols-[1.5fr_1fr] gap-4">
                  <FacturesImpayees delay={110} />
                  <ConversionDonut delay={125} />
                </div>
              </div>
            </div>
          </div>
        </BrowserFrame>
      </div>

      <OverlayText delay={220} />
    </AbsoluteFill>
  );
};
