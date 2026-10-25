import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors, fonts} from '../theme';

export const ImpactScene = () => <>
  <SceneFrame number={3} title="合成案例：找出兩項下游影響" eyebrow="正常案例操作" sceneStart={55} durationSeconds={55}>
    <Reveal at={1.5} style={{position: 'absolute', left: 0, top: 12, width: 670}}>
      <Card style={{height: 398, padding: 36}}>
        <Label>SQL Compare：人工核對 · 示意</Label>
        <div style={{fontFamily: fonts.mono, fontSize: 29, marginTop: 31, overflowWrap: 'anywhere'}}>DEMO_CUSTOMER<br />.CUSTOMER_SEGMENT</div>
        <div style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 25, fontFamily: fonts.mono, fontSize: 29, fontWeight: 800}}>
          <span style={{padding: 13, background: colors.silver, borderRadius: 9}}>VARCHAR2(20)</span>
          <span style={{color: colors.deepIce}}>→</span>
          <span style={{padding: 13, background: 'rgba(112,183,213,0.18)', borderRadius: 9}}>VARCHAR2(40)</span>
        </div>
        <div style={{marginTop: 24, color: colors.warning, fontSize: 26, fontWeight: 700}}>變更資訊由操作者確認，工具未自行驗證差異</div>
      </Card>
    </Reveal>
    <Reveal at={9} style={{position: 'absolute', right: 0, top: 12, width: 945}}>
      <Card style={{height: 398, padding: 32}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
          <div style={{fontSize: 37, fontWeight: 800}}>與變更欄位相符的影響</div>
          <Label tone="success">預期 2 項</Label>
        </div>
        <div style={{marginTop: 25, borderLeft: '8px solid ' + colors.ice, paddingLeft: 24}}>
          <div style={{fontSize: 26, color: colors.deepIce, fontWeight: 800}}>直接影響 · 管理報表</div>
          <div style={{fontFamily: fonts.mono, fontSize: 28, marginTop: 7}}>DEMO_MONTHLY_REPORT<br />.SEGMENT_LABEL</div>
        </div>
        <div style={{marginTop: 23, borderLeft: '8px solid ' + colors.deepIce, paddingLeft: 24}}>
          <div style={{fontSize: 26, color: colors.deepIce, fontWeight: 800}}>間接影響 · 風險分群</div>
          <div style={{fontFamily: fonts.mono, fontSize: 28, marginTop: 7}}>DEMO_RISK_SEGMENTATION<br />.RISK_BUCKET</div>
        </div>
      </Card>
    </Reveal>
    <Reveal at={25} style={{position: 'absolute', left: 0, right: 0, top: 443}}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: 18, padding: '18px 34px', border: '2px solid ' + colors.silver, background: colors.white, fontSize: 28}}>
        <span><b>候選關係 4 筆</b> · 其中 2 筆屬未變更的 CUSTOMER_ID</span>
        <span style={{color: colors.deepIce, fontWeight: 800}}>靜態候選清單仍須工程師覆核</span>
      </div>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="impact" />
</>;
