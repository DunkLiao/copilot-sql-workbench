import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors, fonts} from '../theme';

export const ProblemScene = () => <>
  <SceneFrame number={1} title="一個欄位變更，牽動多少報表？" eyebrow="問題與提案目的" sceneStart={0} durationSeconds={25} dark>
    <Reveal at={1} style={{position: 'absolute', left: 0, top: 25, width: 780}}>
      <Card style={{height: 355, color: colors.white, background: 'rgba(112,183,213,0.10)', borderColor: colors.deepIce, padding: 42}}>
        <Label tone="light">傳統覆核</Label>
        <div style={{fontSize: 56, fontWeight: 800, marginTop: 24}}>跨腳本追查影響</div>
        <div style={{fontSize: 33, lineHeight: 1.55, marginTop: 15, color: colors.silver}}>欄位異動 → 下游 SQL → 風險指標 → 管理報表</div>
        <div style={{fontSize: 29, lineHeight: 1.5, marginTop: 20, color: colors.ice}}>證據分散，人工交接不易保持一致</div>
      </Card>
    </Reveal>
    <Reveal at={5} style={{position: 'absolute', right: 0, top: 25, width: 780}}>
      <Card style={{height: 355, padding: 42}}>
        <Label tone="success">提案流程</Label>
        <div style={{fontSize: 52, fontWeight: 800, marginTop: 23, color: colors.graphite}}>先建立證據，再整理待辦</div>
        <div style={{fontSize: 31, lineHeight: 1.6, marginTop: 18}}>SQL SPA Tools 分析欄位關係<br />M365 Copilot Chat 協助轉譯說明</div>
        <div style={{fontSize: 27, marginTop: 13, color: colors.deepIce}}>工程師與風控覆核者保留最終判斷</div>
      </Card>
    </Reveal>
    <Reveal at={11} style={{position: 'absolute', left: 180, right: 180, top: 432}}>
      <div style={{borderTop: '5px solid ' + colors.ice, paddingTop: 22, textAlign: 'center', color: colors.white, fontSize: 40, fontWeight: 800}}>讓 Copilot 整理分析證據，讓人員負責核對與決策</div>
    </Reveal>
    <div style={{position: 'absolute', top: 193, left: 785, width: 115, height: 4, background: colors.ice}} />
    <div style={{position: 'absolute', top: 177, left: 876, fontFamily: fonts.mono, fontSize: 28, color: colors.ice}}>→</div>
  </SceneFrame>
  <Subtitle sceneId="problem" />
</>;
