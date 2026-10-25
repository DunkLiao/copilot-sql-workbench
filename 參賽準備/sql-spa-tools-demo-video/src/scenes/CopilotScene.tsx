import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors, fonts} from '../theme';

export const CopilotScene = () => <>
  <SceneFrame number={4} title="讓 Copilot 整理證據" eyebrow="摘要確認與人工交接" sceneStart={110} durationSeconds={40} dark>
    <Reveal at={1.5} style={{position: 'absolute', top: 12, left: 0, width: 780}}>
      <Card style={{height: 485, padding: 35}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div style={{fontSize: 35, fontWeight: 800}}>匯出欄位示意</div>
          <Label>預覽後下載</Label>
        </div>
        <div style={{fontFamily: fonts.mono, fontSize: 24, lineHeight: 1.55, marginTop: 20, color: colors.deepIce, overflowWrap: 'anywhere'}}>
          <div>source · SQL SPA Tools column lineage</div>
          <div>changes[0].object · DEMO_CUSTOMER</div>
          <div>changes[0].origin · operator_entered</div>
          <div>changes[0].verification · not_verified_by_tool</div>
          <div>impacts · 2 個下游關係</div>
          <div>limitations · 載入範圍限制</div>
        </div>
        <div style={{fontSize: 26, marginTop: 12, fontWeight: 700}}>變更欄位依 SQL Compare 人工核對後輸入</div>
        <div style={{fontSize: 24, marginTop: 6, color: colors.warning}}>不含原始 SQL；物件與欄位名稱仍須檢查</div>
      </Card>
    </Reveal>
    <Reveal at={10} style={{position: 'absolute', top: 12, right: 0, width: 780}}>
      <Card style={{height: 485, padding: 35}}>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
          <div style={{fontSize: 35, fontWeight: 800}}>Copilot Chat 整理</div>
          <Label tone="warning">畫面示意</Label>
        </div>
        <div style={{marginTop: 31, fontSize: 31, lineHeight: 1.55}}>
          <div>① 依 JSON 列出兩項候選影響</div>
          <div style={{marginTop: 17}}>② 區分人工輸入與血緣證據</div>
          <div style={{marginTop: 17}}>③ 產出工程師待辦與限制說明</div>
        </div>
        <div style={{marginTop: 35, borderTop: '2px solid ' + colors.silver, paddingTop: 17, fontSize: 25, color: colors.warning, fontWeight: 700}}>個人帳戶僅有文字探索；銀行租用戶與附件流程尚未驗收</div>
      </Card>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="copilot" />
</>;
