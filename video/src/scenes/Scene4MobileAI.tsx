import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";
import { PhoneFrame } from "../components/PhoneFrame";

// Scene 4 — Mobile + Assistant IA (23–33.5s / 315 frames within sequence)

const BenefitCard: React.FC<{
  delay: number;
  bg: string;
  color: string;
  title: string;
  sub: string;
  icon: React.ReactNode;
}> = ({ delay, bg, color, title, sub, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 90 } });

  return (
    <div
      style={{
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateX(${interpolate(appear, [0, 1], [-25, 0])}px)`,
      }}
      className="flex items-center gap-4 bg-white p-5 rounded-2xl shadow-md border border-artisangestion-slate-100 w-[420px]"
    >
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${bg}`} style={{ color }}>
        {icon}
      </div>
      <div>
        <p className="font-bold text-artisangestion-slate-900 text-lg leading-tight">{title}</p>
        <p className="text-sm text-artisangestion-slate-500">{sub}</p>
      </div>
    </div>
  );
};

const FormSection: React.FC<{
  children: React.ReactNode;
  delay: number;
  title?: string;
}> = ({ children, delay, title }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = spring({ frame: frame - delay, fps, config: { damping: 15, stiffness: 100 } });

  return (
    <div
      style={{
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(appear, [0, 1], [15, 0])}px)`,
      }}
      className="bg-white border border-artisangestion-slate-200 rounded-xl p-4 mb-3 shadow-sm"
    >
      {title && <h3 className="text-sm font-bold text-artisangestion-slate-900 mb-3">{title}</h3>}
      {children}
    </div>
  );
};

const FormField: React.FC<{ label: string; value: string; delay: number; isDate?: boolean; typing?: boolean }> = ({
  label, value, delay, isDate, typing = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = interpolate(frame - delay, [0, 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  let displayValue = value;
  if (typing) {
    const typingSpring = spring({ frame: frame - delay, fps, config: { damping: 20, stiffness: 60, mass: 1.2 } });
    displayValue = value.slice(0, Math.floor(interpolate(typingSpring, [0, 1], [0, value.length])));
  }

  return (
    <div className="mb-2.5 last:mb-0" style={{ opacity: appear }}>
      <label className="block text-[10px] font-bold text-artisangestion-slate-500 mb-1.5 uppercase tracking-wide">
        {label}
      </label>
      <div className="w-full bg-artisangestion-slate-50 border border-artisangestion-slate-200 rounded-lg px-3 py-2 text-xs text-artisangestion-slate-900 min-h-[32px] flex items-center justify-between">
        <span className="font-medium">{displayValue}</span>
        {isDate && (
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-artisangestion-slate-400">
            <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
          </svg>
        )}
      </div>
    </div>
  );
};

const SparkleButton: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const pulse = 1 + Math.sin((frame - delay) * 0.15) * 0.04;
  const opacity = interpolate(frame - delay, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <div
      style={{
        opacity,
        transform: `scale(${pulse})`,
      }}
      className="flex items-center gap-2 bg-gradient-to-r from-artisangestion-blue to-artisangestion-purple text-white px-4 py-2.5 rounded-xl font-bold text-xs shadow-lg"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3l1.5 5L19 9.5 13.5 11 12 16l-1.5-5L5 9.5 10.5 8z" />
      </svg>
      Assistant IA
    </div>
  );
};

const AIModal: React.FC<{ delay: number; closeModalProgress: number }> = ({ delay, closeModalProgress }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const appear = spring({ frame: frame - delay, fps, config: { damping: 18, stiffness: 80 } });
  const scale = interpolate(appear, [0, 1], [0.85, 1]);

  // Streaming text generation
  const fullText =
    "## Intervention réalisée\n\n**Client :** M. Durand\n**Lieu :** 8 av. du Chantier, Boulogne\n\n### Diagnostic\nFuite identifiée au niveau du raccordement du chauffe-eau. Joint détérioré nécessitant un remplacement.\n\n### Travaux effectués\n- Coupure de l'arrivée d'eau\n- Démontage du raccord défectueux\n- Remplacement du joint et raccord\n- Remise en eau et contrôle d'étanchéité\n\n### Résultat\nAucune fuite résiduelle. Installation fonctionnelle.";
  const streamStart = delay + 40;
  const streamProgress = interpolate(frame - streamStart, [0, 80], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const charCount = Math.floor(streamProgress * fullText.length);
  const visibleText = fullText.slice(0, charCount);

  // Typing cursor blink
  const cursorVisible = Math.floor((frame - streamStart) / 15) % 2 === 0;

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: "rgba(15, 23, 42, 0.4)",
        backdropFilter: "blur(4px)",
        opacity: interpolate(appear, [0, 1], [0, 1]) * (1 - closeModalProgress),
        zIndex: 20,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
      }}
    >
      <div
        style={{
          transform: `scale(${scale}) translateY(${interpolate(appear, [0, 1], [40, 0])}px)`,
          width: "100%",
          maxHeight: "92%",
        }}
        className="bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-artisangestion-slate-200"
      >
        {/* Modal header */}
        <div className="bg-gradient-to-r from-artisangestion-blue to-artisangestion-purple px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 text-white">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3l1.5 5L19 9.5 13.5 11 12 16l-1.5-5L5 9.5 10.5 8z" />
            </svg>
            <span className="font-bold text-sm">Assistant IA — Mistral</span>
          </div>
          <div className="text-white/70 text-xs font-medium">Génération…</div>
        </div>

        {/* Modal body */}
        <div className="p-4 flex-1 overflow-hidden">
          <div className="text-[11px] text-artisangestion-slate-500 mb-3">
            Type d'intervention : <span className="font-bold text-artisangestion-slate-900">Plomberie</span> • Longueur : <span className="font-bold text-artisangestion-slate-900">Normal</span>
          </div>
          <div className="bg-artisangestion-slate-50 rounded-lg p-3 border border-artisangestion-slate-200 text-[11px] text-artisangestion-slate-700 leading-relaxed whitespace-pre-wrap font-mono h-[280px] overflow-hidden">
            {visibleText}
            {streamProgress < 1 && cursorVisible && <span className="text-artisangestion-blue font-bold">▋</span>}
          </div>
        </div>

        {/* Modal footer */}
        <div className="px-4 py-3 border-t border-artisangestion-slate-100 flex items-center justify-between">
          <span className="text-[10px] text-artisangestion-slate-400">Anti-hallucination • Reprend votre description</span>
          <div className="bg-artisangestion-blue text-white px-3 py-1.5 rounded-lg text-[11px] font-bold">
            Insérer
          </div>
        </div>
      </div>
    </div>
  );
};

export const Scene4MobileAI: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entryOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const exitOpacity = interpolate(frame, [295, 315], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Timings
  const phoneDelay = 8;
  const headerDelay = 38;
  const titleDelay = 55;
  const s1Delay = 75;
  const s2Delay = 105;
  const s3Delay = 135;

  // AI modal open/close
  const modalOpenDelay = 175;
  const modalCloseStart = 255;
  const closeModalProgress = interpolate(frame - modalCloseStart, [0, 20], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const modalVisible = frame >= modalOpenDelay;

  // Sparkle button pulse before modal opens
  const sparkleHighlight = interpolate(frame, [150, 175], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Overlay text
  const overlayDelay = 265;
  const overlaySpring = spring({ frame: frame - overlayDelay, fps, config: { damping: 14, stiffness: 60 } });

  return (
    <AbsoluteFill style={{ opacity: entryOpacity * exitOpacity }} className="bg-artisangestion-slate-50">
      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at bottom left, rgba(37, 99, 235, 0.07) 0%, transparent 60%)" }} />

      <div className="absolute inset-0 flex items-center justify-center gap-16 px-20">
        {/* Left side text */}
        <div style={{ maxWidth: 540 }} className="flex flex-col gap-6">
          <div
            style={{
              opacity: interpolate(frame, [10, 28], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `translateY(${interpolate(frame, [10, 28], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
            }}
          >
            <h2 className="text-5xl font-extrabold text-artisangestion-slate-900 tracking-tight leading-tight mb-2">
              Vos rapports<br /><span className="text-artisangestion-blue">en direct du chantier.</span>
            </h2>
          </div>
          <BenefitCard
            delay={45}
            bg="bg-blue-50"
            color="#2563EB"
            title="Rapports conformes"
            sub="Photos, signatures, date, client"
            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>}
          />
          <BenefitCard
            delay={70}
            bg="bg-emerald-50"
            color="#16A34A"
            title="Photos intégrées"
            sub="Capture caméra, gallery native"
            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" /><circle cx="12" cy="13" r="4" /></svg>}
          />
          <BenefitCard
            delay={95}
            bg="bg-purple-50"
            color="#8B5CF6"
            title="Assistant IA Mistral"
            sub="Rédige votre rapport à votre place"
            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3l1.5 5L19 9.5 13.5 11 12 16l-1.5-5L5 9.5 10.5 8z" /></svg>}
          />
        </div>

        {/* Phone side */}
        <div className="relative" style={{ transform: `translateY(${interpolate(sparkleHighlight, [0, 1], [0, -8], { extrapolateRight: "clamp" })}px)` }}>
          <PhoneFrame delay={phoneDelay}>
            <div className="h-full bg-artisangestion-slate-50 flex flex-col overflow-hidden relative">
              {/* Status bar */}
              <div className="h-6 flex justify-between items-center px-6 pt-2">
                <span className="text-[10px] font-bold text-artisangestion-slate-900">14:32</span>
                <div className="flex gap-1 items-center">
                  <div className="w-3 h-3 rounded-full border border-artisangestion-slate-900/20" />
                  <div className="w-4 h-2 rounded-sm bg-artisangestion-slate-900" />
                </div>
              </div>

              {/* App Header */}
              <div
                style={{ opacity: interpolate(spring({ frame: frame - headerDelay, fps }), [0, 1], [0, 1]) }}
                className="px-4 py-3 flex items-center justify-between bg-white border-b border-artisangestion-slate-200"
              >
                <div className="flex items-center gap-2 text-artisangestion-slate-500 font-medium text-sm">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5" /><path d="M12 19l-7-7 7-7" /></svg>
                  Retour
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg border border-artisangestion-slate-200 flex items-center justify-center text-artisangestion-slate-500">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" /></svg>
                  </div>
                  <div className="bg-artisangestion-blue text-white px-3 py-1.5 rounded-lg flex items-center gap-1.5 text-xs font-bold shadow-sm">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
                    PDF
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-hidden p-4 pt-5">
                <h1
                  style={{ opacity: interpolate(spring({ frame: frame - titleDelay, fps }), [0, 1], [0, 1]) }}
                  className="text-xl font-extrabold text-artisangestion-slate-900 mb-4 leading-tight"
                >
                  Nouveau Rapport<br />d'Intervention
                </h1>

                <FormSection delay={s1Delay}>
                  <FormField label="Date d'intervention *" value="23/04/2026" delay={s1Delay + 10} isDate typing />
                </FormSection>

                <FormSection delay={s2Delay}>
                  <div className="flex justify-between items-center mb-3">
                    <label className="text-[10px] font-bold text-artisangestion-slate-500 uppercase tracking-wide">Titre du document PDF</label>
                    <div className="bg-artisangestion-slate-100 rounded-lg p-0.5 flex gap-0.5">
                      <div className="bg-artisangestion-blue text-white text-[9px] font-bold px-2 py-1 rounded">En cours</div>
                      <div className="text-artisangestion-slate-500 text-[9px] font-bold px-2 py-1 rounded">Terminée</div>
                    </div>
                  </div>
                  <FormField label="" value="RAPPORT D'INTERVENTION" delay={s2Delay + 10} typing={false} />
                </FormSection>

                <FormSection delay={s3Delay} title="Informations du Client">
                  <FormField label="Nom complet du client *" value="Martin Durand" delay={s3Delay + 12} typing />
                  <div className="grid grid-cols-2 gap-3 mt-2">
                    <FormField label="SIRET" value="842 931 000" delay={s3Delay + 22} typing />
                    <FormField label="Téléphone" value="06 12 34 56 78" delay={s3Delay + 32} typing />
                  </div>
                </FormSection>

                {/* AI Sparkle button */}
                <div style={{ opacity: interpolate(frame - 150, [0, 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }} className="mt-1 flex justify-center">
                  <SparkleButton delay={155} />
                </div>
              </div>

              {/* AI Modal overlay */}
              {modalVisible && <AIModal delay={modalOpenDelay} closeModalProgress={closeModalProgress} />}
            </div>
          </PhoneFrame>
        </div>
      </div>

      {/* Overlay text */}
      <div
        style={{
          position: "absolute",
          bottom: 55,
          left: 0,
          right: 0,
          opacity: interpolate(overlaySpring, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(overlaySpring, [0, 1], [25, 0])}px)`,
        }}
        className="flex justify-center"
      >
        <div className="bg-artisangestion-blue/95 backdrop-blur-sm px-9 py-4 rounded-2xl shadow-2xl">
          <span className="text-white text-2xl font-extrabold tracking-tight">
            Décrivez l'intervention, l'IA rédige le rapport.
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
