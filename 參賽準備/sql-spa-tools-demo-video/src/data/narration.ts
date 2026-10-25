import rawNarration from './narration.json';

export type NarrationScene = {
  id: 'problem' | 'security' | 'impact' | 'copilot' | 'warning' | 'regression' | 'measurement' | 'next';
  seconds: number;
  title: string;
  narration: string;
};

export const narration = rawNarration as NarrationScene[];
