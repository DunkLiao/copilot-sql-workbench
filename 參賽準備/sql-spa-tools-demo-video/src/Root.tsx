import {Audio} from '@remotion/media';
import {Composition, Series, staticFile, useVideoConfig} from 'remotion';
import {ProblemScene} from './scenes/ProblemScene';
import {SecurityFlowScene} from './scenes/SecurityFlowScene';
import {ImpactScene} from './scenes/ImpactScene';
import {CopilotScene} from './scenes/CopilotScene';
import {WarningScene} from './scenes/WarningScene';
import {RegressionScene} from './scenes/RegressionScene';
import {MeasurementScene} from './scenes/MeasurementScene';
import {NextStepsScene} from './scenes/NextStepsScene';

const SqlCopilotDemo = () => {
  const {fps} = useVideoConfig();
  return <>
    <Series>
      <Series.Sequence name="問題與目的" durationInFrames={25 * fps} premountFor={fps}><ProblemScene /></Series.Sequence>
      <Series.Sequence name="資料流程" durationInFrames={30 * fps} premountFor={fps}><SecurityFlowScene /></Series.Sequence>
      <Series.Sequence name="正常案例" durationInFrames={55 * fps} premountFor={fps}><ImpactScene /></Series.Sequence>
      <Series.Sequence name="摘要與 Copilot" durationInFrames={40 * fps} premountFor={fps}><CopilotScene /></Series.Sequence>
      <Series.Sequence name="解析警告" durationInFrames={35 * fps} premountFor={fps}><WarningScene /></Series.Sequence>
      <Series.Sequence name="技術回歸" durationInFrames={25 * fps} premountFor={fps}><RegressionScene /></Series.Sequence>
      <Series.Sequence name="效益量測" durationInFrames={30 * fps} premountFor={fps}><MeasurementScene /></Series.Sequence>
      <Series.Sequence name="下一步" durationInFrames={30 * fps} premountFor={fps}><NextStepsScene /></Series.Sequence>
    </Series>
    <Audio name="01 問題與目的旁白" from={0} src={staticFile('audio/01-problem.mp3')} premountFor={fps} />
    <Audio name="02 資料流程旁白" from={25 * fps} src={staticFile('audio/02-security.mp3')} premountFor={fps} />
    <Audio name="03 正常案例旁白" from={55 * fps} src={staticFile('audio/03-impact.mp3')} premountFor={fps} />
    <Audio name="04 摘要與 Copilot 旁白" from={110 * fps} src={staticFile('audio/04-copilot.mp3')} premountFor={fps} />
    <Audio name="05 解析警告旁白" from={150 * fps} src={staticFile('audio/05-warning.mp3')} premountFor={fps} />
    <Audio name="06 技術回歸旁白" from={185 * fps} src={staticFile('audio/06-regression.mp3')} premountFor={fps} />
    <Audio name="07 效益量測旁白" from={210 * fps} src={staticFile('audio/07-measurement.mp3')} premountFor={fps} />
    <Audio name="08 下一步旁白" from={240 * fps} src={staticFile('audio/08-next.mp3')} premountFor={fps} />
  </>;
};

export const RemotionRoot = () => <Composition id="SqlCopilotDemo" component={SqlCopilotDemo} durationInFrames={8100} fps={30} width={1920} height={1080} />;
