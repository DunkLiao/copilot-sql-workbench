import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors, fonts} from '../theme';

export const WarningScene = () => <>
  <SceneFrame number={5} title="解析警告必須被看見" eyebrow="警告情境" sceneStart={150} durationSeconds={35}>
    <Reveal at={1.5} style={{position: 'absolute', top: 19, left: 0, width: 680}}>
      <Card style={{height: 387, padding: 38, background: colors.graphite, borderColor: colors.warning, color: colors.white}}>
        <Label tone="warning">合成 SQL · 故意缺漏</Label>
        <div style={{fontFamily: fonts.mono, fontSize: 31, marginTop: 31, lineHeight: 1.7, color: colors.silver}}>
          <div>SELECT * FROM ...</div>
          <div>PIVOT ( ...</div>
          <div style={{color: colors.ice}}>IN ( <span style={{color: colors.warning}}>清單缺漏</span> )</div>
        </div>
        <div style={{marginTop: 15, fontSize: 30, fontWeight: 800, color: colors.ice}}>analysisMessages: warn × 1</div>
      </Card>
    </Reveal>
    <Reveal at={8} style={{position: 'absolute', top: 19, right: 0, width: 950}}>
      <Card style={{height: 387, padding: 38, background: 'rgba(198,93,59,0.06)', borderColor: colors.warning}}>
        <div style={{fontSize: 39, fontWeight: 800, color: colors.warning}}>清單不保證完整</div>
        <div style={{fontSize: 32, lineHeight: 1.7, marginTop: 22}}>解析警告必須出現在整理結果。<br />若 Copilot 漏列警告，記為未通過。<br />工程師回到本機檢視並補查。</div>
      </Card>
    </Reveal>
    <Reveal at={17} style={{position: 'absolute', left: 0, right: 0, top: 438}}>
      <div style={{fontSize: 30, color: colors.warning, fontWeight: 800, padding: '21px 30px', background: colors.white, borderRadius: 18, border: '2px solid ' + colors.warning}}>未載入程序、排程、動態 SQL 與外部報表不在保證範圍；空結果不等於沒有風險。</div>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="warning" />
</>;
