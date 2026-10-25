import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors} from '../theme';

export const MeasurementScene = () => <>
  <SceneFrame number={7} title="效益：用配對量測回答" eyebrow="成效驗證計畫" sceneStart={210} durationSeconds={30}>
    <Reveal at={1.5} style={{position: 'absolute', left: 0, top: 14, width: 790}}>
      <Card style={{height: 303, padding: 37}}>
        <Label>人工流程</Label>
        <div style={{fontSize: 45, fontWeight: 800, marginTop: 25}}>逐份腳本追查與交接</div>
        <div style={{fontSize: 30, marginTop: 19}}>使用相同的固定合成案例</div>
      </Card>
    </Reveal>
    <Reveal at={5} style={{position: 'absolute', right: 0, top: 14, width: 790}}>
      <Card style={{height: 303, padding: 37, borderColor: colors.ice}}>
        <Label tone="success">原型流程</Label>
        <div style={{fontSize: 45, fontWeight: 800, marginTop: 25}}>本機分析＋Copilot 整理</div>
        <div style={{fontSize: 30, marginTop: 19}}>至少 3 組真人配對試次</div>
      </Card>
    </Reveal>
    <Reveal at={11} style={{position: 'absolute', left: 0, right: 0, top: 362}}>
      <Card style={{height: 142, padding: '22px 30px'}}>
        <div style={{fontSize: 30, fontWeight: 800, color: colors.deepIce}}>量測指標</div>
        <div style={{fontSize: 28, marginTop: 9}}>完成時間與步驟 · 命中／漏列／誤列 · JSON 證據一致性 · 警告揭露</div>
      </Card>
    </Reveal>
    <Reveal at={18} style={{position: 'absolute', right: 18, top: 212}}>
      <Label tone="warning">尚無實測節省比例</Label>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="measurement" />
</>;
