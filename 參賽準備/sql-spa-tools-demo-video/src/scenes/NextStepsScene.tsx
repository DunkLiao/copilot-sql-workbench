import {Card, Label, Reveal, SceneFrame} from '../components/SceneFrame';
import {Subtitle} from '../components/Subtitle';
import {colors} from '../theme';

const nextSteps = [
  {number: '01', heading: '確認規則', detail: '競賽提交與資料治理要求'},
  {number: '02', heading: '核准環境', detail: 'M365 附件流程端到端演練'},
  {number: '03', heading: '配對量測', detail: '回填真實時間與證據指標'},
];

export const NextStepsScene = () => <>
  <SceneFrame number={8} title="下一步：核准環境演練與量測" eyebrow="原型進度與結語" sceneStart={240} durationSeconds={30} dark>
    <div style={{display: 'flex', gap: 25, marginTop: 16}}>
      {nextSteps.map((item, index) => <Reveal key={item.number} at={1.5 + index * 2.7} style={{flex: 1}}>
        <Card style={{height: 284, padding: 34}}>
          <Label>{item.number}</Label>
          <div style={{fontSize: 49, fontWeight: 800, marginTop: 25}}>{item.heading}</div>
          <div style={{fontSize: 29, lineHeight: 1.5, marginTop: 15}}>{item.detail}</div>
        </Card>
      </Reveal>)}
    </div>
    <Reveal at={12} style={{position: 'absolute', left: 0, right: 0, top: 351}}>
      <div style={{borderLeft: '10px solid ' + colors.ice, padding: '21px 34px', fontSize: 46, fontWeight: 800, lineHeight: 1.38, background: 'rgba(112,183,213,0.10)', color: colors.white}}>讓 Copilot 整理分析證據，<br />讓風險管理覆核者保留最終判斷。</div>
    </Reveal>
  </SceneFrame>
  <Subtitle sceneId="next" />
</>;
