import { AbsoluteFill, Sequence } from "remotion";
import { Scene1Intro } from "./scenes/Scene1Intro";
import { Scene2Dashboard } from "./scenes/Scene2Dashboard";
import { Scene3DevisFactures } from "./scenes/Scene3DevisFactures";
import { Scene4MobileAI } from "./scenes/Scene4MobileAI";
import { Scene5CTA } from "./scenes/Scene5CTA";

// 40s video at 30fps = 1200 frames
// Scene 1 — Intro / Problématique        : 0    – 165  (0s    – 5.5s)
// Scene 2 — Tableau de bord web          : 150  – 465  (5s    – 15.5s)
// Scene 3 — Devis & Factures             : 450  – 705  (15s   – 23.5s)
// Scene 4 — Mobile + Assistant IA        : 690  – 1005 (23s   – 33.5s)
// Scene 5 — Appel à l'action             : 990  – 1200 (33s   – 40s)
// (15 frames overlap between scenes for crossfade transitions)

export const ArtisanGestionVideo: React.FC = () => {
  return (
    <AbsoluteFill className="bg-artisangestion-slate-50 font-sans">
      <Sequence durationInFrames={165}>
        <Scene1Intro />
      </Sequence>

      <Sequence from={150} durationInFrames={315}>
        <Scene2Dashboard />
      </Sequence>

      <Sequence from={450} durationInFrames={255}>
        <Scene3DevisFactures />
      </Sequence>

      <Sequence from={690} durationInFrames={315}>
        <Scene4MobileAI />
      </Sequence>

      <Sequence from={990} durationInFrames={210}>
        <Scene5CTA />
      </Sequence>
    </AbsoluteFill>
  );
};
