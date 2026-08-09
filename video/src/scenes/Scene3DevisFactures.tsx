import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
} from "remotion";

// Scene 3 — Devis & Factures (15–23.5s / 255 frames within sequence)
// Left: feature points. Right: document morphs Devis → Facture (Factur-X).

const FeaturePoint: React.FC<{
  delay: number;
  color: string;
  bg: string;
  icon: React.ReactNode;
  title: string;
  sub: string;
}> = ({ delay, color, bg, icon, title, sub }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = spring({ frame: frame - delay, fps, config: { damping: 14, stiffness: 90 } });

  return (
    <div
      style={{
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateX(${interpolate(appear, [0, 1], [-25, 0])}px)`,
      }}
      className="flex items-center gap-4 bg-white p-5 rounded-2xl shadow-md border border-artisangestion-slate-100"
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

const LineItem: React.FC<{ delay: number; desc: string; qty: number; pu: number; tva: number }> = ({
  delay, desc, qty, pu, tva,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const appear = spring({ frame: frame - delay, fps, config: { damping: 16, stiffness: 100 } });
  const total = (qty * pu * (1 + tva / 100)).toFixed(2);

  return (
    <div
      style={{
        opacity: interpolate(appear, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(appear, [0, 1], [10, 0])}px)`,
      }}
      className="grid grid-cols-12 gap-2 py-2.5 border-b border-artisangestion-slate-100 text-xs items-center"
    >
      <div className="col-span-6 font-semibold text-artisangestion-slate-900">{desc}</div>
      <div className="col-span-2 text-center text-artisangestion-slate-500">{qty}</div>
      <div className="col-span-2 text-right text-artisangestion-slate-500">{pu.toLocaleString("fr-FR")} €</div>
      <div className="col-span-2 text-right font-bold text-artisangestion-slate-900">{total} €</div>
    </div>
  );
};

const Signature: React.FC<{ delay: number }> = ({ delay }) => {
  const frame = useCurrentFrame();
  const progress = interpolate(frame - delay, [0, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Hand-drawn signature path (a stylized "P.M")
  const path = "M5 35 C 10 10, 18 10, 20 30 S 14 45, 8 38 M25 15 L25 40 M25 18 C 32 12, 40 18, 38 28 S 28 38, 30 40 M45 18 L55 18 M50 15 L50 42";
  const pathLength = 120;
  const dashOffset = pathLength * (1 - progress);

  return (
    <div className="flex items-center gap-4 mt-5">
      <div className="relative w-[180px] h-[60px] border-b-2 border-dashed border-artisangestion-slate-300">
        <svg width="180" height="60" viewBox="0 0 60 50" className="absolute inset-0">
          <path
            d={path}
            fill="none"
            stroke="#2563EB"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            style={{
              strokeDasharray: pathLength,
              strokeDashoffset: dashOffset,
            }}
          />
        </svg>
      </div>
      <span className="text-xs text-artisangestion-slate-400 font-medium">Signature du client</span>
    </div>
  );
};

const Document: React.FC<{ isInvoice: boolean; morphProgress: number }> = ({ isInvoice, morphProgress }) => {
  return (
    <div
      className="bg-white rounded-2xl shadow-2xl border border-artisangestion-slate-200 w-full overflow-hidden flex flex-col"
      style={{ height: 720, transform: `translateX(${interpolate(morphProgress, [0, 1], [0, -30])}px)` }}
    >
      {/* Document header */}
      <div className="px-10 py-6 flex items-start justify-between border-b border-artisangestion-slate-100">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-extrabold text-lg"
              style={{ background: isInvoice ? "linear-gradient(135deg, #8B5CF6, #6D28D9)" : "linear-gradient(135deg, #3B82F6, #2563EB)" }}
            >
              M
            </div>
            <div>
              <div className="font-extrabold text-artisangestion-slate-900 text-lg leading-tight">Martin Plomberie</div>
              <div className="text-[11px] text-artisangestion-slate-500">15 rue de l'Eau • 75011 Paris</div>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div
            className="text-2xl font-extrabold tracking-tight"
            style={{ color: isInvoice ? "#8B5CF6" : "#2563EB" }}
          >
            {isInvoice ? "FACTURE" : "DEVIS"}
          </div>
          <div className="text-xs text-artisangestion-slate-500 font-mono mt-0.5">
            {isInvoice ? "F-2026-0042" : "D-2026-0017"}
          </div>
        </div>
      </div>

      {/* Meta */}
      <div className="px-10 py-4 flex justify-between text-xs">
        <div>
          <div className="text-artisangestion-slate-400 font-semibold uppercase tracking-wide text-[10px] mb-1">Client</div>
          <div className="font-bold text-artisangestion-slate-900">Martin Durand</div>
          <div className="text-artisangestion-slate-500">8 avenue du Chantier, 92100 Boulogne</div>
        </div>
        <div className="text-right">
          <div className="text-artisangestion-slate-400 font-semibold uppercase tracking-wide text-[10px] mb-1">
            {isInvoice ? "Échéance" : "Validité"}
          </div>
          <div className="font-bold text-artisangestion-slate-900">{isInvoice ? "23/05/2026" : "30 jours"}</div>
          <div className="text-artisangestion-slate-500">Date : 23/04/2026</div>
        </div>
      </div>

      {/* Line items header */}
      <div className="px-10 pt-2">
        <div className="grid grid-cols-12 gap-2 py-2 border-b-2 border-artisangestion-slate-200 text-[10px] font-bold text-artisangestion-slate-400 uppercase tracking-wide">
          <div className="col-span-6">Description</div>
          <div className="col-span-2 text-center">Qté</div>
          <div className="col-span-2 text-right">P.U. HT</div>
          <div className="col-span-2 text-right">Total TTC</div>
        </div>

        <LineItem delay={50} desc="Remplacement chauffe-eau 100L" qty={1} pu={680} tva={20} />
        <LineItem delay={65} desc="Main d'œuvre (3h)" qty={3} pu={55} tva={20} />
        <LineItem delay={80} desc="Fournitures & raccordement" qty={1} pu={120} tva={20} />
      </div>

      {/* Totals */}
      <div className="px-10 pt-3 flex justify-end">
        <div className="w-[280px] text-xs space-y-1.5">
          <div className="flex justify-between text-artisangestion-slate-500">
            <span>Sous-total HT</span><span className="font-semibold text-artisangestion-slate-900">1 065,00 €</span>
          </div>
          <div className="flex justify-between text-artisangestion-slate-500">
            <span>TVA (20%)</span><span className="font-semibold text-artisangestion-slate-900">213,00 €</span>
          </div>
          <div className="flex justify-between pt-2 border-t border-artisangestion-slate-200">
            <span className="font-extrabold text-artisangestion-slate-900 text-base">Total TTC</span>
            <span className="font-extrabold text-artisangestion-blue text-base">1 278,00 €</span>
          </div>
        </div>
      </div>

      {/* Signature (devis only) */}
      {!isInvoice && (
        <div className="px-10 flex-1">
          <Signature delay={110} />
        </div>
      )}

      {/* Factur-X badge (facture only) */}
      {isInvoice && (
        <div className="px-10 pb-6 mt-auto flex items-center gap-3">
          <div className="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-lg border border-emerald-200">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 12l2 2 4-4" /><circle cx="12" cy="12" r="10" />
            </svg>
            <span className="text-xs font-bold text-emerald-700">Factur-X • Facture électronique conforme</span>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="px-10 py-3 bg-artisangestion-slate-50 border-t border-artisangestion-slate-100 text-[10px] text-artisangestion-slate-400 text-center">
        Martin Plomberie • SIRET 842 931 000 001 • TVA FR 42 842 931 000 • IBAN FR76 • noreply@artisangestion.com
      </div>
    </div>
  );
};

export const Scene3DevisFactures: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const entryOpacity = interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const exitOpacity = interpolate(frame, [235, 255], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Morph from devis → facture around frame 160
  const morphStart = 160;
  const morph = spring({ frame: frame - morphStart, fps, config: { damping: 18, stiffness: 70 } });
  const isInvoice = morph > 0.5;

  // Convert button highlight (before morph)
  const convertHighlight = interpolate(frame, [130, 150], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Overlay text
  const overlayDelay = 175;
  const overlaySpring = spring({ frame: frame - overlayDelay, fps, config: { damping: 14, stiffness: 60 } });

  return (
    <AbsoluteFill style={{ opacity: entryOpacity * exitOpacity }} className="bg-artisangestion-slate-100">
      <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at top right, rgba(139, 92, 246, 0.06) 0%, transparent 60%)" }} />

      <div className="absolute inset-0 flex items-center justify-center gap-20 px-24">
        {/* Left feature points */}
        <div style={{ maxWidth: 560 }} className="flex flex-col gap-5">
          <div
            style={{
              opacity: interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `translateY(${interpolate(frame, [10, 25], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
            }}
          >
            <h2 className="text-5xl font-extrabold text-artisangestion-slate-900 tracking-tight leading-tight mb-2">
              Devis & factures<br /><span className="text-artisangestion-blue">en quelques clics.</span>
            </h2>
          </div>
          <FeaturePoint
            delay={40}
            color="#2563EB"
            bg="bg-blue-50"
            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="9" y1="15" x2="15" y2="15" /></svg>}
            title="Devis professionnels"
            sub="Lignes, TVA, conditions, signature"
          />
          <FeaturePoint
            delay={75}
            color="#16A34A"
            bg="bg-emerald-50"
            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 12h18M3 6h18M3 18h18" /><path d="M5 12l4-4M5 12l4 4" /></svg>}
            title="Convertir en facture en 1 clic"
            sub="Numérotation automatique"
          />
          <FeaturePoint
            delay={110}
            color="#8B5CF6"
            bg="bg-purple-50"
            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><path d="M9 15l2 2 4-4" /></svg>}
            title="Factures conformes Factur-X"
            sub="XML embarqué, norme européenne"
          />
        </div>

        {/* Right document */}
        <div className="relative" style={{ width: 640 }}>
          <Document isInvoice={isInvoice} morphProgress={morph} />

          {/* Convert button floating (before morph) */}
          <div
            style={{
              position: "absolute",
              bottom: 30,
              right: -50,
              opacity: (1 - morph) * interpolate(frame, [120, 145], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
              transform: `scale(${1 + convertHighlight * 0.08}) translateY(${interpolate(frame, [130, 160], [0, -10], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
              boxShadow: `0 10px 40px rgba(37, 99, 235, ${0.3 + convertHighlight * 0.2})`,
            }}
            className="bg-artisangestion-blue text-white px-5 py-3 rounded-xl font-bold text-sm flex items-center gap-2 pointer-events-none"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
            Convertir en facture
          </div>
        </div>
      </div>

      {/* Overlay text after morph */}
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
        <div className="bg-artisangestion-slate-900/90 backdrop-blur-sm px-9 py-4 rounded-2xl shadow-2xl">
          <span className="text-white text-2xl font-extrabold tracking-tight">
            Du devis à la facture, sans recopier une seule ligne.
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
