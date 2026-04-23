import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { PhoneFrame } from "../components/PhoneFrame";

// Scene 3: "Efficacité sur le Terrain" (15-25s / 300 frames within sequence)
// Updated to match the real Ventura mobile app "Nouveau Rapport" view

const FormSection: React.FC<{
  children: React.ReactNode;
  delay: number;
  title?: string;
}> = ({ children, delay, title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({
    frame: frame - delay,
    fps,
    config: { damping: 15, stiffness: 100 },
  });

  return (
    <div
      style={{
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(appear, [0, 1], [15, 0])}px)`,
      }}
      className="bg-white border border-ventura-slate-200 rounded-xl p-4 mb-4 shadow-sm"
    >
      {title && (
        <h3 className="text-sm font-bold text-ventura-slate-900 mb-3">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

const FormField: React.FC<{
  label: string;
  value: string;
  delay: number;
  isDate?: boolean;
}> = ({ label, value, delay, isDate = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const typing = spring({
    frame: frame - delay,
    fps,
    config: { damping: 20, stiffness: 80 },
  });

  const displayValue = value.slice(0, Math.floor(interpolate(typing, [0, 1], [0, value.length])));

  return (
    <div className="mb-3 last:mb-0">
      <label className="block text-[10px] font-bold text-ventura-slate-500 mb-1.5 uppercase tracking-wide">
        {label}
      </label>
      <div className="w-full bg-ventura-slate-50 border border-ventura-slate-200 rounded-lg px-3 py-2 text-xs text-ventura-slate-900 min-h-[34px] flex items-center justify-between">
        <span>{displayValue}</span>
        {isDate && (
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-ventura-slate-400">
            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
            <line x1="16" y1="2" x2="16" y2="6" />
            <line x1="8" y1="2" x2="8" y2="6" />
            <line x1="3" y1="10" x2="21" y2="10" />
          </svg>
        )}
      </div>
    </div>
  );
};

export const Scene3Mobile: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene entrance
  const entryOpacity = interpolate(frame, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const exitOpacity = interpolate(frame, [280, 300], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Animations timings
  const phoneDelay = 10;
  const headerDelay = 40;
  const titleDelay = 60;
  const section1Delay = 80;
  const section2Delay = 130;
  const section3Delay = 180;

  return (
    <AbsoluteFill style={{ opacity: entryOpacity * exitOpacity }} className="bg-ventura-slate-50">
      {/* Background decoration */}
      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at bottom right, rgba(37, 99, 235, 0.08) 0%, transparent 60%)" }} />

      <div className="absolute inset-0 flex items-center justify-center gap-24">
        {/* Left side text */}
        <div style={{ maxWidth: 600 }}>
          <h2 className="text-5xl font-extrabold text-ventura-slate-900 tracking-tight leading-tight mb-8">
            Générez vos rapports<br />
            <span className="text-ventura-blue">en direct</span> du chantier
          </h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4 bg-white p-4 rounded-2xl shadow-sm border border-ventura-slate-100">
              <div className="w-12 h-12 rounded-xl bg-ventura-blue/10 flex items-center justify-center text-ventura-blue">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </div>
              <p className="font-bold text-ventura-slate-700">Rapports conformes et sécurisés</p>
            </div>
            <div className="flex items-center gap-4 bg-white p-4 rounded-2xl shadow-sm border border-ventura-slate-100">
              <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center text-green-600">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
              </div>
              <p className="font-bold text-ventura-slate-700">Photos intégrées automatiquement</p>
            </div>
          </div>
        </div>

        {/* Phone side */}
        <PhoneFrame delay={phoneDelay}>
          <div className="h-full bg-ventura-slate-50 flex flex-col overflow-hidden">
            {/* Status bar mock */}
            <div className="h-6 flex justify-between items-center px-6 pt-2">
              <span className="text-[10px] font-bold text-ventura-slate-900">14:32</span>
              <div className="flex gap-1 items-center">
                <div className="w-3 h-3 rounded-full border border-ventura-slate-900/20" />
                <div className="w-4 h-2 rounded-sm bg-ventura-slate-900" />
              </div>
            </div>

            {/* App Header (matching NouveauRapport.vue) */}
            <div 
              style={{ opacity: interpolate(spring({ frame: frame - headerDelay, fps }), [0, 1], [0, 1]) }}
              className="px-4 py-4 flex items-center justify-between bg-white border-b border-ventura-slate-200"
            >
              <div className="flex items-center gap-2 text-ventura-slate-500 font-medium text-sm">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
                Retour
              </div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg border border-ventura-slate-200 flex items-center justify-center text-ventura-slate-500">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </div>
                <div className="w-8 h-8 rounded-lg border border-ventura-slate-200 flex items-center justify-center text-ventura-slate-500">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
                </div>
                <div className="bg-ventura-blue text-white px-3 py-1.5 rounded-lg flex items-center gap-1.5 text-xs font-bold shadow-sm">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                  PDF
                </div>
              </div>
            </div>

            {/* Content area */}
            <div className="flex-1 overflow-y-auto p-4 pt-6">
              <h1 
                style={{ opacity: interpolate(spring({ frame: frame - titleDelay, fps }), [0, 1], [0, 1]) }}
                className="text-xl font-extrabold text-ventura-slate-900 mb-6 leading-tight"
              >
                Nouveau Rapport<br />d'Intervention
              </h1>

              {/* Section 1: Date */}
              <FormSection delay={section1Delay}>
                <FormField label="Date d'intervention *" value="23/04/2026" delay={section1Delay + 10} isDate />
              </FormSection>

              {/* Section 2: Titre + Statut */}
              <FormSection delay={section2Delay}>
                <div className="flex justify-between items-center mb-3">
                  <label className="text-[10px] font-bold text-ventura-slate-500 uppercase tracking-wide">Titre du document PDF *</label>
                  <div className="bg-ventura-slate-100 rounded-lg p-0.5 flex gap-0.5">
                    <div className="bg-ventura-blue text-white text-[9px] font-bold px-2 py-1 rounded shadow-sm">En cours</div>
                    <div className="text-ventura-slate-500 text-[9px] font-bold px-2 py-1 rounded">Terminée</div>
                  </div>
                </div>
                <div className="w-full bg-ventura-slate-50 border border-ventura-slate-200 rounded-lg px-3 py-2 text-xs text-ventura-slate-900 font-bold uppercase">
                  RAPPORT D'INTERVENTION
                </div>
                <p className="text-[9px] text-ventura-slate-400 mt-1.5">Ce titre apparaîtra en haut du document PDF généré</p>
              </FormSection>

              {/* Section 3: Client */}
              <FormSection delay={section3Delay} title="Informations du Client">
                <FormField label="Nom complet du client *" value="Martin Durand" delay={section3Delay + 15} />
                <div className="grid grid-cols-2 gap-3 mt-3">
                  <FormField label="SIRET / SIREN" value="842 931 000 001" delay={section3Delay + 25} />
                  <FormField label="Téléphone" value="06 12 34 56 78" delay={section3Delay + 35} />
                </div>
              </FormSection>
            </div>
          </div>
        </PhoneFrame>
      </div>
    </AbsoluteFill>
  );
};
