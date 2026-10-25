import {narration, type NarrationScene} from './narration';
import captions from './captions.json';

export type SceneId = NarrationScene['id'];

export const scenes = narration;

export const captionsByScene = captions as Record<SceneId, Array<{
  start: number;
  end: number;
  text: string;
}>>;

export const sceneStarts: Record<SceneId, number> = {
  problem: 0,
  security: 25,
  impact: 55,
  copilot: 110,
  warning: 150,
  regression: 185,
  measurement: 210,
  next: 240,
};
