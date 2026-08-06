import "./index.css";
import { Composition } from "remotion";
import { ArtisanGestionVideo } from "./ArtisanGestionVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ArtisanGestionPromo"
        component={ArtisanGestionVideo}
        durationInFrames={1200}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
