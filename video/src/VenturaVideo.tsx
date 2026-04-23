import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { Scene1Problem } from "./scenes/Scene1Problem";
import { Scene2Dashboard } from "./scenes/Scene2Dashboard";
import { Scene3Mobile } from "./scenes/Scene3Mobile";
import { Scene4CTA } from "./scenes/Scene4CTA";

// 30s video at 30fps = 900 frames
// Scene 1: 0-150 (0-5s)
// Scene 2: 150-450 (5-15s)
// Scene 3: 450-750 (15-25s)
// Scene 4: 750-900 (25-30s)

export const VenturaVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill className="bg-ventura-slate-50 font-sans">
      {/* Scene 1: La Problématique (0-5s) */}
      <Sequence from={0} durationInFrames={165}>
        <Scene1Problem />
      </Sequence>

      {/* Scene 2: Le Tableau de Bord (5-15s) */}
      <Sequence from={150} durationInFrames={315}>
        <Scene2Dashboard />
      </Sequence>

      {/* Scene 3: Efficacité sur le Terrain (15-25s) */}
      <Sequence from={450} durationInFrames={315}>
        <Scene3Mobile />
      </Sequence>

      {/* Scene 4: Appel à l'Action (25-30s) */}
      <Sequence from={750} durationInFrames={150}>
        <Scene4CTA />
      </Sequence>
    </AbsoluteFill>
  );
};
