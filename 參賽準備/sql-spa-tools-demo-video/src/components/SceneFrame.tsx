import type {CSSProperties, ReactNode} from 'react';
import {interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {colors, fonts} from '../theme';

type SceneFrameProps = {
  number: number;
  title: string;
  eyebrow: string;
  sceneStart: number;
  durationSeconds: number;
  dark?: boolean;
  children: ReactNode;
};

export const SceneFrame = ({number, title, eyebrow, sceneStart, durationSeconds, dark = false, children}: SceneFrameProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const background = dark ? colors.graphite : colors.snow;
  const foreground = dark ? colors.white : colors.graphite;
  const fade = interpolate(frame, [0, 0.55 * fps, durationSeconds * fps - 0.5 * fps, durationSeconds * fps], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const progress = Math.min(100, ((sceneStart + frame / fps) / 270) * 100);

  return <div style={{position: 'absolute', inset: 0, overflow: 'hidden', background, color: foreground, fontFamily: fonts.sans, opacity: fade}}>
    <div style={{position: 'absolute', inset: 0, opacity: dark ? 0.12 : 0.25, backgroundImage: 'radial-gradient(circle, ' + colors.ice + ' 1.2px, transparent 1.2px)', backgroundSize: '36px 36px'}} />
    <div style={{position: 'absolute', top: 48, left: 96, right: 96, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
        <div style={{width: 70, height: 70, borderRadius: 20, background: colors.ice, color: colors.graphite, fontSize: 31, fontWeight: 800, display: 'grid', placeItems: 'center'}}>{String(number).padStart(2, '0')}</div>
        <div style={{fontSize: 26, letterSpacing: 2.2, fontWeight: 700, color: dark ? colors.ice : colors.deepIce}}>{eyebrow}</div>
      </div>
      <div style={{width: 290, height: 80, padding: '5px 20px', borderRadius: 18, background: colors.white, display: 'grid', placeItems: 'center'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 13, width: '100%'}}>
          <div style={{position: 'relative', width: 51, height: 56, flexShrink: 0}}>
            <div style={{position: 'absolute', left: 10, top: 0, width: 31, height: 35, border: '7px solid ' + colors.deepIce, borderBottom: 0, borderRadius: '19px 19px 0 0'}} />
            <div style={{position: 'absolute', left: 0, bottom: 0, width: 51, height: 35, borderRadius: 8, background: colors.graphite, display: 'flex', justifyContent: 'center', alignItems: 'end', gap: 4, paddingBottom: 6}}>
              <span style={{width: 6, height: 12, background: colors.ice}} /><span style={{width: 6, height: 18, background: colors.ice}} /><span style={{width: 6, height: 24, background: colors.ice}} />
            </div>
          </div>
          <div style={{color: colors.graphite, lineHeight: 1.08}}><div style={{fontSize: 30, fontWeight: 900, letterSpacing: 1}}>鎖頭銀行</div><div style={{fontSize: 16, fontWeight: 800, letterSpacing: 2.7, color: colors.deepIce}}>SQL SPA TOOLS</div></div>
        </div>
      </div>
    </div>
    <div style={{position: 'absolute', top: 145, left: 96, right: 96, fontSize: 76, fontWeight: 800, letterSpacing: 1.2, lineHeight: 1.24}}>{title}</div>
    <div style={{position: 'absolute', top: 264, left: 96, right: 96, height: 560}}>{children}</div>
    <div style={{position: 'absolute', left: 96, right: 96, bottom: 30, display: 'flex', justifyContent: 'space-between', fontSize: 21, color: dark ? colors.silver : colors.deepIce}}>
      <span>SQL SPA Tools × M365 Copilot Chat</span>
      <span>合成案例示範 · 風險管理部 Dunk</span>
    </div>
    <div style={{position: 'absolute', bottom: 0, left: 0, width: '100%', height: 9, background: dark ? colors.deepIce : colors.silver}}>
      <div style={{height: '100%', width: progress + '%', background: colors.ice}} />
    </div>
  </div>;
};

type RevealProps = {children: ReactNode; at?: number; style?: CSSProperties};

export const Reveal = ({children, at = 0, style}: RevealProps) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const opacity = interpolate(frame, [at * fps, (at + 0.7) * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const translateY = interpolate(frame, [at * fps, (at + 0.7) * fps], [34, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <div style={{opacity, transform: 'translateY(' + translateY + 'px)', ...style}}>{children}</div>;
};

export const Card = ({children, style}: {children: ReactNode; style?: CSSProperties}) => <div style={{border: '2px solid ' + colors.silver, borderRadius: 28, padding: 30, background: colors.white, boxShadow: '0 14px 35px rgba(32,42,51,0.08)', color: colors.slate, ...style}}>{children}</div>;

export const Label = ({children, tone = 'blue'}: {children: ReactNode; tone?: 'blue' | 'light' | 'warning' | 'success' | 'slate'}) => {
  const color = tone === 'light' ? colors.ice : tone === 'warning' ? colors.warning : tone === 'success' ? colors.success : tone === 'slate' ? colors.slate : colors.deepIce;
  return <span style={{display: 'inline-block', border: '2px solid ' + color, color, padding: '7px 16px', borderRadius: 999, fontSize: 23, fontWeight: 800, lineHeight: 1.2}}>{children}</span>;
};
