import {useCurrentFrame, useVideoConfig} from 'remotion';
import {captionsByScene, type SceneId} from '../data/scenes';
import {colors, fonts} from '../theme';

export const Subtitle = ({sceneId}: {sceneId: SceneId}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const seconds = frame / fps;
  const cue = captionsByScene[sceneId].find((item) => seconds >= item.start && seconds < item.end + 0.22);
  if (!cue) return null;
  return <div style={{position: 'absolute', bottom: 89, left: 170, right: 170, minHeight: 76, padding: '16px 34px', background: 'rgba(32,42,51,0.96)', color: colors.white, borderRadius: 17, fontFamily: fonts.sans, fontSize: 32, fontWeight: 700, textAlign: 'center', lineHeight: 1.35, overflowWrap: 'anywhere', boxShadow: '0 16px 40px rgba(0,0,0,0.18)'}}>{cue.text}</div>;
};
