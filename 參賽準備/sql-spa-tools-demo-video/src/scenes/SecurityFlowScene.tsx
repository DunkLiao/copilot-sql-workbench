import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors} from '../theme';

const steps = [
  {number: '01', label: '本機分析', detail: '原始 SQL 保留在瀏覽器'},
  {number: '02', label: '摘要預覽', detail: '移除 SQL、運算式與路徑'},
  {number: '03', label: '人工檢查', detail: '確認名稱與資料分類'},
  {number: '04', label: '明確下載', detail: '確認後匯出最小 JSON'},
  {number: '05', label: '手動交接', detail: '交給 Copilot Chat 整理'},
];

export const SecurityFlowScene = () => <>
  <SceneFrame number={2} title="資料留在本機，交接由人決定" eyebrow="資料流程與安全界線" sceneStart={25} durationSeconds={30}>
    <div style={{display: 'flex', gap: 19, marginTop: 52}}>
      {steps.map((step, index) => <Reveal at={1.5 + index * 2.3} key={step.number} style={{width: 325}}>
        <Card style={{height: 292, padding: '29px 24px', borderTop: '9px solid ' + (index === 2 ? colors.warning : colors.ice)}}>
          <div style={{fontSize: 29, color: colors.deepIce, fontWeight: 800}}>{step.number}</div>
          <div style={{fontSize: 40, fontWeight: 800, marginTop: 35, whiteSpace: 'nowrap'}}>{step.label}</div>
          <div style={{fontSize: 26, lineHeight: 1.5, marginTop: 15, color: colors.slate}}>{step.detail}</div>
        </Card>
      </Reveal>)}
    </div>
    <Reveal at={15} style={{position: 'absolute', left: 0, right: 0, top: 425}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 24, padding: '22px 30px', border: '3px solid ' + colors.warning, borderRadius: 24, background: 'rgba(198,93,59,0.06)'}}>
        <Label tone="warning">人工停止點</Label>
        <div style={{fontSize: 33, fontWeight: 700}}>資料分類若有疑慮，停止上傳並依治理流程確認。</div>
      </div>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="security" />
</>;
