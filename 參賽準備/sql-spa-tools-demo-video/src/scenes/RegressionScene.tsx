import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors} from '../theme';

const categories = [
  {count: '10', label: 'Node 契約'},
  {count: '12', label: '頁面載入'},
  {count: '4', label: '主要操作'},
  {count: '4', label: '個資檢查'},
];

export const RegressionScene = () => <>
  <SceneFrame number={6} title="技術回歸：30 項實際通過" eyebrow="客觀研發證據" sceneStart={185} durationSeconds={25}>
    <Reveal at={1.2} style={{position: 'absolute', left: 0, top: 9, width: 530}}>
      <Card style={{height: 386, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', borderColor: colors.success}}>
        <div style={{fontSize: 176, lineHeight: 1, fontWeight: 900, color: colors.success}}>30</div>
        <div style={{fontSize: 42, fontWeight: 800, marginTop: 24}}>項實際通過</div>
        <div style={{fontSize: 27, color: colors.deepIce, marginTop: 14}}>Colab full · 工具層</div>
      </Card>
    </Reveal>
    <div style={{position: 'absolute', left: 578, right: 0, top: 9, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 15}}>
      {categories.map((category, index) => <Reveal key={category.label} at={3 + index * 2}>
        <Card style={{height: 386, padding: 24, textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
          <div style={{fontSize: 86, fontWeight: 900, color: colors.deepIce}}>{category.count}</div>
          <div style={{fontSize: 30, fontWeight: 800, marginTop: 19}}>{category.label}</div>
        </Card>
      </Reveal>)}
    </div>
    <Reveal at={13} style={{position: 'absolute', left: 0, right: 0, top: 428}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 22, background: colors.white, border: '2px solid ' + colors.silver, padding: '20px 30px', borderRadius: 19, fontSize: 29}}>
        <Label tone="slate">1,000 筆 prepared</Label>
        <span>合成案例僅完成準備，尚未逐筆執行；以上數據不等於 Copilot 或銀行流程驗收。</span>
      </div>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="regression" />
</>;
