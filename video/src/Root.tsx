import "./index.css";
import { Composition } from "remotion";
import { VenturaVideo } from "./VenturaVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VenturaPromo"
        component={VenturaVideo}
        durationInFrames={900}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
