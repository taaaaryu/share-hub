/* Second design direction: task flow and evidence-led decisions, not Mock page composition. */
const flowHead = (id,step,title,lead,actions='') => `<div class="flow-head"><div><div class="flow-kicker">${step} / ${id}</div><h1 class="flow-title">${screenMap[id]?.[1] || title}</h1><p class="flow-lead">${screenPurpose[id] || lead}</p></div><div class="flow-head-actions">${actions}</div></div>${context()}${scenarioBanner()}`;
const surfaceCopy = {
  '根拠の充足':['録画と確認の不足を調べる','不足している視点と未確認の作業を分けて表示します。'],
  '前回から続く問い':['未解決の問いを開く','前回の調査を続けるときは、比較条件から確認します。'],
  '試合ごとの資料充足':['録画が足りない試合を探す','出場した選手の録画がない場合だけ、追加対応が必要です。'],
  '次の取り込み':['録画を登録する手順を確認する','試合と視点を選んでからファイルを登録します。'],
  '証拠台帳':['視点ごとの確認状況を見る','未確認の視点を開き、候補を事実として採用できるか判断します。'],
  '指標の扱い':['VPSの根拠を確認する','指標の値だけで判断せず、対象映像と欠損を確認します。'],
  '指標の裏付け':['OPSの対象と欠損を確認する','どの試合が集計に含まれるかを確認します。'],
  '時刻と地点を結ぶ':['地図の地点から映像を開く','地点と時刻を選び、映像で位置関係を確認します。'],
  '選択地点 / Game 06':['選択地点の根拠を確認する','推定位置は映像で再確認してから判断に使います。'],
  '検証中の問い':['この移動に関する問いを確認する','接触しなかった試合も比較対象に含めます。'],
  '検証するアクション':['前回決めた行動の実施を確認する','実行できた試合と、結果まで確認できた試合を分けます。'],
  '比較条件':['比較する試合の条件を揃える','地図、期間、選手を変更して同じ条件で比べます。'],
  '結果の推移':['行動後の結果を比べる','対象試合と除外理由を見てから傾向を読みます。'],
  '比較対象の試合':['結果の元になった試合を開く','各試合の映像へ戻り、例外や欠損を確認します。'],
  '仮説ボード':['相手の動きについて仮説を検証する','支持する観測と反例を同じ条件で見比べます。'],
  '資料の条件':['観測元と更新日を確認する','公開資料の出典と鮮度を確認してから比較します。'],
  '判断の理由':['編成案を選んだ理由を残す','数値だけでは分からない判断と、次回試すことを記録します。'],
  '採用前のチェック':['編成案の不足を確認する','実績の少なさと条件の違いを採用前に確認します。'],
  '共有の状態':['下書き・共有済み資料を開く','編集する資料か、選手が読む版かを選びます。'],
  '共有前に残っている仕事':['資料を共有するまでの手順を見る','事実を選び、選手向け表示と共有条件を確認します。'],
  '共有前の関門':['共有してよい内容か確認する','内部メモと音声、共有相手、期限を確認します。'],
  '編集対象':['選手向けの本文を編集する','下書きを直し、左の選手向け表示で読み方を確かめます。']
};
const flowSurface = (title,body,side='') => { const [label,guide]=surfaceCopy[title] || [title,'']; return `<section class="flow-surface"><header><h2>${label}</h2>${side}</header>${guide?`<p class="surface-guide">${guide}</p>`:''}<div class="flow-body">${body}</div></section>`; };
const flowStage = active => `<div class="flow-stage" aria-label="分析ワークフロー">${[
  ['01','録画を揃える'],['02','シーンを確認'],['03','行動を共有'],['04','結果を確認']
].map((x,i)=>`<div class="${i===active?'active':''}"><small>STEP ${x[0]}</small><strong>${x[1]}</strong></div>`).join('')}</div>`;
const flowRow = (n,title,description,right='') => `<div class="flow-row"><span class="num">${n}</span><div><h3>${title}</h3><p>${description}</p></div><div class="row-actions">${right}</div></div>`;
const draftInput = (key,label) => `<label class="field"><span>${label}</span><input class="input" data-draft="${key}" value="${safe(state.reportDraft[key])}"></label>`;
const draftTextarea = (key,label) => `<label class="field"><span>${label}</span><textarea class="textarea" data-draft="${key}">${safe(state.reportDraft[key])}</textarea></label>`;
const draftSelect = (key,label,options) => `<label class="field"><span>${label}</span><select class="select" data-draft="${key}">${options.map(value=>`<option ${value===state.reportDraft[key]?'selected':''}>${safe(value)}</option>`).join('')}</select></label>`;
const flowNote = `<div class="wireframe-note">設計検討用 · 架空のデータ · 認証・送信・共有・算出は実行しません</div>`;

function todayWorkflow(){
  if(state.scenario==='empty') return `${flowHead('SCR-DASH-01','WORKSPACE','次の判断を始める','まず振り返る試合と録画を用意します。')}${flowStage(0)}${empty('まだ調査対象がありません','最初のセッションと試合を登録してください。','セッションを作成','SCR-SESSION-02')}`;
  return `${flowHead('SCR-DASH-01','MATCH REVIEW','Pro Scrim Week 3 の振り返り','まず未確認のシーンを映像で確かめます。確認後、次回の改善行動をまとめて選手へ共有できます。',open('チーム内を検索','SCR-SEARCH-01'))}
    ${flowStage(1)}
    <div class="flow-frame">
      <section class="case-banner"><div><div class="flow-kicker">ACTIVE CASE / PRO SCRIM WEEK 3 · GAME 06</div><h2>北側高台でピークの開始がずれた。<br>原因はコールか、位置取りか？</h2><p>確認できた時間差と、理由についての仮説を分けて調べる。</p><div class="case-meta"><span>3選手視点＋観戦</span><span>事実 1件 / 仮説 2件</span><span>未確認の根拠 2件</span></div></div>${link('Game 06 の映像を確認','SCR-REVIEW-01','primary')}</section>
      <div class="flow-grid split"><section class="flow-surface"><header><h2>担当作業を選んで再開する</h2><span class="flow-stamp">優先順 / 担当付き</span></header>
        ${flowRow('01','Game 06 の射撃開始差を映像で確認','分析担当 · 3視点の同時刻を照合する',link('Game 06 の映像を確認','SCR-REVIEW-01','sm'))}
        ${flowRow('02','Game 03 の欠損録画を補う','Kai視点の再選択が必要。別試合の解析は継続中',link('録画の不足を確認','SCR-INGEST-01','sm'))}
        ${flowRow('03','次回のコール手順を選手へ共有','コーチ · 内部メモを除外して資料化',link('選手向け資料を編集','SCR-REPORT-02','sm'))}
        </section><div class="flow-frame">${flowSurface('根拠の充足',`<div class="evidence-score"><div><span>映像</span><strong>3 / 4 視点</strong></div><div><span>機械読取</span><strong>一部欠損</strong></div><div><span>人の確認</span><strong>未完了</strong></div></div><p class="annotation" style="margin:15px 0 0">一つの「信頼度%」にまとめず、何が不足しているかを示します。</p>`)}${flowSurface('前回から続く問い',`<strong>リング先入りは生存につながっているか？</strong><p class="small" style="margin:8px 0 15px">対象18試合。地図と出場構成を揃えて比較する必要があります。</p>${link('次回試合の結果を比較','SCR-TREND-01','sm')}`)}</div></div>
    </div>${flowNote}`;
}

function ingestWorkflow(){
  const coverage=`<div class="table-wrap"><table class="coverage"><thead><tr><th>試合 / 視点</th><th>Sora</th><th>Ren</th><th>Mio</th><th>Kai</th><th>観戦</th></tr></thead><tbody><tr><td>Game 06</td><td class="present">あり</td><td class="present">あり</td><td class="present">あり</td><td class="absent">非出場</td><td class="present">あり</td></tr><tr><td>Game 05</td><td class="present">あり</td><td class="present">あり</td><td class="absent">非出場</td><td class="missing">出場・録画なし</td><td class="present">あり</td></tr><tr><td>Game 03</td><td class="present">あり</td><td class="present">あり</td><td class="absent">非出場</td><td class="missing">送信失敗</td><td class="missing">未登録</td></tr></tbody></table></div>`;
  return `${flowHead('SCR-INGEST-01','01 / PREPARE','資料を揃える','「何本処理したか」より先に、試合の誰の視点があり、何が欠けているかを確認します。',open('録画を登録','SCR-INGEST-02','primary'))}${flowStage(0)}
    <div class="flow-frame"><div class="flow-grid split">${flowSurface('試合ごとの資料充足',`${coverage}<p class="annotation" style="margin:14px 0 0">非出場と、出場したが録画がない状態を分けて表示。</p>`,link('試合を編集','SCR-SESSION-02','sm'))}
      ${flowSurface('次の取り込み',`<ol class="step-list"><li><i>1</i><div><strong>試合を選ぶ</strong><small>セッションと出場選手を先に確定</small></div></li><li><i>2</i><div><strong>映像の視点を指定する</strong><small>選手視点か観戦視点かを区別</small></div></li><li><i>3</i><div><strong>送信後の品質を確認する</strong><small>送信完了と解析完了は別</small></div></li></ol>${open('動画登録を始める','SCR-INGEST-02','primary full')}`)}</div>
      <section class="flow-surface"><header><h2>録画の処理結果を確認する</h2><span class="flow-stamp">アップロード / 解析 / 品質</span></header>
        ${flowRow('A1','Game 06 · Ren視点','送信済み → 解析完了 · 問題なし',`${badge('利用可能','ok')}${link('レビュー','SCR-REVIEW-01','sm')}`)}
        ${flowRow('A2','Game 06 · Sora視点','送信済み → 確認待ち · HUD一部読取不可',`${badge('一部利用可','warn')}${btn('Sora視点の品質を確認','recording:Sora','sm')}`)}
        ${flowRow('A3','Game 03 · Kai視点','送信失敗 → 解析未開始 · 元ファイルの再選択が必要',`${badge('要対応','danger')}${btn('Kai視点の失敗理由を見る','recording:Kai','sm')}`)}
      </section>${notice('解析できない値は0点にしません','欠損理由と影響する指標を示し、再試行しても人の確認記録は上書きしません。','warn')}
    </div>${flowNote}`;
}

function reviewWorkflow(){
  return `${flowHead('SCR-REVIEW-01','02 / VERIFY','主張を検証する','画面の中心は4本の動画ではなく「何を確認し、何をまだ言えないか」です。',`${open('根拠映像の区間を編集','SCR-REVIEW-02')}${btn('記録内容を確認','toast:ワイヤーフレームでは保存しません','primary')}`)}${flowStage(1)}
    <div class="flow-frame"><div class="case-banner"><div><div class="flow-kicker">QUESTION / GAME 06 · 12:34–13:09</div><h2>射撃開始の時間差は、<br>カバー到着前のピークによるものか？</h2><div class="case-meta"><span>事実候補 2</span><span>解釈候補 2</span><span>候補の判定 ${state.reviewDecision}</span></div></div>${badge(state.reviewDecision==='未判定'?'判断保留':'判定を編集中',state.reviewDecision==='未判定'?'warn':'ok')}</div>
      <div class="flow-grid triple"><section class="flow-surface"><header><h2>事実候補を判定する</h2><span class="flow-stamp">SCENE 01 / 06</span></header>
        <div class="claim ${state.reviewDecision==='事実として採用'?'confirmed':'pending'}"><span class="flow-kicker">事実候補 · ${state.reviewDecision}</span><p>RenとMioの射撃開始に1.4秒の差があった。</p><button class="source-link" data-action="panel:SCR-REVIEW-02">この候補の時刻と視点を確認 ↗</button><div class="claim-actions">${btn('事実として採用','review:adopt','sm')}${btn('候補を却下','review:reject','sm')}${open('時刻・視点を修正','SCR-REVIEW-02','sm')}</div></div>
        <div class="claim pending"><span class="flow-kicker">機械による推定</span><p>接敵時の最大選手間距離は32mの可能性。</p><button class="source-link" data-action="panel:SCR-REVIEW-02">推定方法を見る ↗</button></div>
        <div class="claim"><span class="flow-kicker">人の解釈 · 仮説</span><p>カバー到着前にピークした可能性。コールの重なりも確認する。</p></div>
        <div class="flow-body">${notice('採用・修正・却下は人が行う','検出結果をそのまま確認済みの事実にしません。','warn')}</div>
      </section>
      <section class="flow-surface"><header><h2>同じ時刻の映像を見比べる</h2><span class="flow-stamp">COMMON TIME 12:50</span></header><div class="review-stage"><div class="video-placeholder"><span>▷ Ren視点 · 12:50 · 主視点</span></div><div class="review-thumbs"><div>Sora · IGL</div><div>Mio · Anchor</div><div>Coach · 観戦</div></div></div><div class="review-tools">${btn('◀ 5秒','toast:5秒戻る','sm')}${btn('▷ 同期再生','toast:再生の動作例','sm')}${select('音声',['Ren','Sora','Mio','Coach'])}${btn('同期補正','toast:視点間の時刻ずれを調整','sm')}</div><div class="flow-body"><div class="timeline"><i style="left:14%"></i><small style="left:14%">コール</small><i style="left:42%"></i><small style="left:42%">射撃開始</small><i style="left:76%"></i><small style="left:76%">被弾</small></div></div></section>
      <div class="flow-frame">${flowSurface('証拠台帳',`<ol class="step-list"><li><i>✓</i><div><strong>Ren視点 · 12:50</strong><small>射撃開始を確認</small></div></li><li><i>?</i><div><strong>Mio視点 · 12:51</strong><small>開始時刻に同期ずれの可能性</small></div></li><li><i>?</i><div><strong>観戦視点 · 12:49</strong><small>位置関係を要確認</small></div></li></ol>${open('映像区間と視点を編集','SCR-REVIEW-02','sm')}`)}${flowSurface('指標の扱い',`<div class="flow-number">VPS 66 <small>/ 説明用</small></div><p class="small" style="margin:10px 0">正式指標として扱う。ただし算出式と尺度は未確定。欠損・算出版・元映像を表示する。</p>${link('VPSの対象試合を確認','SCR-TREND-01','sm')}`)}</div></div>
      <div class="flow-grid three"><div class="decision-sheet"><span class="flow-kicker">01 / 事実として記録する内容</span>${textarea('映像で確かめた内容',state.reviewDecision==='候補を却下'?'': 'Renの射撃開始からMioの射撃開始まで1.4秒。')}${badge(state.reviewDecision,state.reviewDecision==='事実として採用'?'ok':'warn')}<p class="annotation">候補を採用すると文案を表示し、却下すると欄を空にします。ここでの変更は保存されません。</p></div><div class="decision-sheet"><span class="flow-kicker">02 / 理由についての解釈</span>${textarea('仮説として残す内容','カバー到着前にピークした可能性がある。')}${check('内部メモとして保持',true)}</div><div class="decision-sheet"><span class="flow-kicker">03 / 次回試す行動</span>${textarea('実際に試すこと','接敵前に位置と準備完了をコールする。')}${select('担当',['全員','Ren','Sora','Mio'])}</div></div>
      <div class="flow-grid equal">${link('地図で移動と接敵を確認','SCR-MAP-01','full')}${link('選手に伝える内容を編集','SCR-REPORT-02','full primary')}</div>
    </div>${flowNote}`;
}

const mapPoints = {
  '01': {name:'降下後の合流地点',time:'00:45',detail:'降下後の合流位置は映像からの推定です。選んだ地点の前後を映像で確認します。'},
  '02': {name:'北側高台の接敵地点',time:'12:34',detail:'接敵前にリング3へ進入。最大選手間距離32mは映像からの推定です。'},
  '03': {name:'リング3への進入地点',time:'13:20',detail:'接敵後に移動を再開した地点です。移動の時刻とルートを映像で確認します。'}
};
function mapWorkflow(){const point=mapPoints[state.selectedMapPoint] || mapPoints['02'];return `${flowHead('SCR-MAP-01','02 / CONTEXT','移動を検証する','地図は戦術評価の結果ではなく、時間と場所の根拠へ入る索引です。',link('Game 06 の映像を確認','SCR-REVIEW-01'))}${flowStage(1)}<div class="flow-grid split">${flowSurface('時刻と地点を結ぶ',`${map()}<div class="timeline"><i style="left:15%"></i><small style="left:15%">降下</small><i style="left:51%"></i><small style="left:51%">接敵</small><i style="left:83%"></i><small style="left:83%">リング3</small></div><div class="field-row three">${check('味方の軌跡',true)}${check('リング',true)}${check('接触地点',true)}</div>`)}<div class="flow-frame">${flowSurface('選択地点 / Game 06',`<span class="flow-marker">推定位置 · 地点 ${state.selectedMapPoint}</span><h2 style="margin-top:12px">${point.name} · ${point.time}</h2><p>${point.detail}</p>${link('Game 06 の映像画面を開く','SCR-REVIEW-01','primary full')}`)}${flowSurface('検証中の問い',`<strong>収縮後の北側ルートは接触しやすいか？</strong><p class="small" style="margin:10px 0">接触3件 / 6試合。反例と対戦相手の移動を併せて確認します。</p>${link('北側に来る相手を調べる','SCR-OPP-01','sm')}`)}</div></div>${flowNote}`}

function trendsWorkflow(){return `${flowHead('SCR-TREND-01','04 / LEARN','前後を確かめる','「実行したか」と「結果が変わったか」を別々に評価します。',link('Game 06 の映像を確認','SCR-REVIEW-01'))}${flowStage(3)}<div class="flow-frame"><div class="flow-grid split">${flowSurface('検証するアクション',`<div class="flow-kicker">NEXT ACTION / 全員</div><h2 style="margin:10px 0">接敵前に位置と準備完了をコールする</h2><div class="evidence-score"><div><span>実施</span><strong>2 / 3試合</strong></div><div><span>結果確認</span><strong>1 / 3試合</strong></div><div><span>判断</span><strong>継続検証</strong></div></div>`)}${flowSurface('比較条件',`${select('期間',['Week 2 → Week 3','Week 1 → Week 2'])}${select('地図',['Storm Point','全地図'])}${select('対象選手',['Ren','Sora','Mio'])}<p class="annotation" style="margin:12px 0 0">構成・地図・ゲーム更新が違う場合は単純比較しません。</p>`)}</div><div class="flow-grid split">${flowSurface('結果の推移',`${chart()}<p style="margin:30px 0 0" class="small">指標：ピーク時間差の中央値。映像欠損1試合を集計から除外。</p>`)}${flowSurface('指標の裏付け',`<div class="flow-number">OPS 76 <small>/ 指定期間</small></div><p class="small">VPSは各シーン、OPSは期間単位。両者とも算出式・尺度・入力値・版・欠損を確認できる設計とします。</p>${notice('欠損は0点ではない','計算できない試合は件数と理由を別表示します。','warn')}`)}</div>${flowSurface('比較対象の試合',`${flowRow('01','Game 06 · 北側高台','実施なし / 結果確認済み',link('該当映像を確認','SCR-REVIEW-01','sm'))}${flowRow('02','Game 04 · リング先入り','実施あり / 結果確認済み','<span class="flow-stamp">個別映像への導線は設計中</span>')}${flowRow('03','Game 05 · 橋の横断','実施あり / 視点欠損で結果保留','<span class="flow-stamp">個別映像への導線は設計中</span>')}`)}</div>${flowNote}`}

function opponentsWorkflow(){return `${flowHead('SCR-OPP-01','02 / EXTERNAL EVIDENCE','相手を調べる','対戦相手を順位表にせず、検証中の問いと資料の鮮度から読む。',open('一覧の相手を同条件で比較','SCR-OPP-03','primary'))}${flowStage(1)}<div class="flow-grid split">${flowSurface('仮説ボード',`${field('問い','外入りチームが増えると北側ルートの接触が増えるか？')}<div class="flow-grid equal" style="margin-top:16px"><div class="scenario-card"><span class="flow-kicker">支持する観測</span><h3>北側で接触 3件</h3><p>対象6試合。各試合の位置と映像へ戻れる。</p></div><div class="scenario-card"><span class="flow-kicker">反例・不足</span><h3>接触しない試合 3件</h3><p>録画欠損と異なるリング位置を確認する。</p></div></div>`)}${flowSurface('資料の条件',`${notice('公開された資料のみ','取得元、利用条件、更新日時を観測ごとに保持します。')}<p style="margin:14px 0 0" class="small">同名チーム、改名、選手交代による取り違えを訂正できる必要があります。</p>`)}</div><section class="flow-surface"><header><h2>相手ごとの観測元を開く</h2><span class="flow-stamp">観測数と鮮度を優先表示</span></header>${flowRow('01','Aster Union','内入り · 北側高台 → 中央 / 3試合 / 9月11日更新',btn('Aster Union の観測元','opponent:Aster Union','sm'))}${flowRow('02','Cobalt Nine','外入り · 外周 → 橋 / 4試合 / 9月11日更新',btn('Cobalt Nine の観測元','opponent:Cobalt Nine','sm'))}${flowRow('03','Ember Collective','外入り · 南西 → 川沿い / 5試合 / 9月10日更新',btn('Ember Collective の観測元','opponent:Ember Collective','sm'))}</section>${flowNote}`}

function rosterWorkflow(){return `${flowHead('SCR-ROSTER-01','03 / DECIDE','編成案を比べる','数値で選手を自動選抜せず、条件、実績、懸念、試したいことを並べます。',btn('比較結果を記録（デモ）','toast:ワイヤーフレームでは保存しません','primary'))}${flowStage(2)}<div class="flow-frame"><div class="flow-grid three">${select('地図',['Storm Point','World’s Edge'])}${select('戦術',['先入り・射線保持','外入り・接敵重視'])}${select('キャラクター構成',['バンガロール / ワットソン / ニューキャッスル','別構成'])}</div><div class="flow-grid equal"><div class="scenario-card ${state.rosterChoice==='A'?'highlight':''}"><div class="flow-kicker">OPTION A / 実績あり</div><h3>Sora · Ren · Mio</h3><p>共同出場24試合。先入り後の射線形成に再現例あり。</p><div class="gate-item"><span>＋</span>連携の型が共有されている</div><div class="gate-item"><span>?</span>ピーク前の準備確認が必要</div>${btn('案Aを採用候補にする','roster:A','sm')}</div><div class="scenario-card ${state.rosterChoice==='B'?'highlight':''}"><div class="flow-kicker">OPTION B / 実績少</div><h3>Sora · Ren · Kai</h3><p>共同出場3試合。比較できる映像が不足。</p><div class="gate-item"><span>＋</span>新しい視点・柔軟な役割変更</div><div class="gate-item"><span>?</span>リセット時のコールを試す必要</div>${btn('案Bを採用候補にする','roster:B','sm')}</div></div><div class="flow-grid split">${flowSurface('判断の理由',`<p>採用候補：<strong>${state.rosterChoice?`案${state.rosterChoice}`:'未選択'}</strong></p>${textarea('コーチ・分析担当者の内部記録',state.rosterChoice==='A'?'案Aを採用候補とする。次回はピーク前の確認コールを試す。':state.rosterChoice==='B'?'案Bを採用候補とする。共同出場の資料が少ないため、まず連携を試す。':'案を選んでから、理由と次回試すことを記録する。')}${check('内部メモとして扱う',true)}${btn('理由を保存（デモ）','toast:ワイヤーフレームでは保存しません','sm')}`)}${flowSurface('採用前のチェック',`<div class="gate-item"><span>✓</span>共同出場の対象件数を確認</div><div class="gate-item"><span>✓</span>実績のない案を明示</div><div class="gate-item"><span>!</span>相手・地図の条件差を確認</div><div class="gate-item"><span>!</span>数値だけで出場者を決めない</div>`)}</div></div>${flowNote}`}

function reportsWorkflow(){return `${flowHead('SCR-REPORT-01','03 / COMMUNICATE','伝える資料を選ぶ','レポートの件数より、誰へ何を共有済みかを先に確認します。',link('新しい資料を作る','SCR-REPORT-02','primary'))}${flowStage(2)}<div class="flow-grid split">${flowSurface('共有の状態',`${flowRow('01','スクリム終了後の5分サマリー','チーム全員向け · 下書き · 根拠2件',link('下書きを編集','SCR-REPORT-02','sm'))}${flowRow('02','リング先入りの再現ポイント','Sora / Ren / Mio向け · 共有済み · 版2',link('選手向け表示を見る','SCR-SHARE-01','sm'))}`)}${flowSurface('共有前に残っている仕事',`<ol class="step-list"><li><i>1</i><div><strong>未共有インサイトを選ぶ</strong><small>確認済みの事実と解釈を分ける</small></div></li><li><i>2</i><div><strong>相手の表示を確かめる</strong><small>内部メモと編成理由を除く</small></div></li><li><i>3</i><div><strong>版と閲覧条件を確定</strong><small>期限・取消条件を確認</small></div></li></ol>`)}</div>${flowNote}`}

function reportEditWorkflow(){return `${flowHead('SCR-REPORT-02','03 / COMMUNICATE','選手に伝える','入力画面と選手プレビューを横並びにせず、送る内容を一枚の資料として編集します。',`${btn('下書きを保存','toast:下書き保存の動作例')}${open('共有相手と期限を確認','SCR-SHARE-02','primary')}`)}${flowStage(2)}
  <div class="flow-grid split"><div class="flow-frame"><div class="editorial-sheet"><div class="flow-kicker">THUMASTER / PLAYER BRIEF · DRAFT 03</div><h2 data-preview="title">${safe(state.reportDraft.title)}</h2><p class="small">対象：<span data-preview="audience">${safe(state.reportDraft.audience)}</span> · Pro Scrim Week 3</p><div class="editorial-section"><span class="flow-kicker">01 / WHAT WE SAW</span><strong>映像で確認した事実</strong><p data-preview="fact">${safe(state.reportDraft.fact)}</p><div style="margin-top:12px" class="video-placeholder"><span>▷ Game 06 · 12:34–13:09</span></div></div><div class="editorial-section"><span class="flow-kicker">02 / OUR INTERPRETATION</span><strong>人の解釈・仮説</strong><p data-preview="interpretation">${safe(state.reportDraft.interpretation)}</p></div><div class="editorial-section"><span class="flow-kicker">03 / TRY NEXT</span><strong>次回試す行動</strong><p data-preview="action">${safe(state.reportDraft.action)}</p></div></div></div><div class="flow-frame">${flowSurface('共有前の関門',`<div class="gate-item"><span>?</span>事実と解釈が混ざっていないか確認</div><div class="gate-item"><span>?</span>本文と根拠映像・時刻が一致するか確認</div><div class="gate-item"><span>?</span>本文・音声に内部情報がないか確認</div><div class="gate-item"><span>?</span>選手に見える表示をプレビューで確認</div><div class="gate-item"><span>?</span>共有相手と期限を確定</div>${notice('この項目は未検証','このワイヤーフレームでは安全性を自動判定しません。','warn')}${open('共有内容を確認','SCR-SHARE-02','primary full')}`)}${flowSurface('編集対象',`${draftInput('title','資料のタイトル')}${draftTextarea('fact','映像で確認した事実')}${draftTextarea('interpretation','人の解釈・仮説')}${draftTextarea('action','次回試す行動')}${draftSelect('audience','共有対象',['チーム全員','Ren','Sora','Mio'])}${open('Game 06 の根拠映像を確認','SCR-REVIEW-02','sm')}<p class="annotation" style="margin-top:15px">編成理由は内部記録として残し、選手向け本文へ自動追加しません。</p>`)}</div></div>${flowNote}`}

const gameData = {
  '06': {date:'2026-09-11',map:'Storm Point',players:['Sora','Ren','Mio'],recordings:'選手3視点＋観戦視点 · 解析済み'},
  '05': {date:'2026-09-10',map:'Storm Point',players:['Sora','Ren','Kai'],recordings:'Kai視点が録画なし · 他の視点は利用可能'},
  '04': {date:'2026-09-09',map:'Storm Point',players:['Sora','Ren','Mio'],recordings:'選手3視点 · 解析済み'},
  'new': {date:'',map:'Storm Point',players:[],recordings:'出場選手を指定した後に録画を登録'}
};
function sessionsWorkflow(){
  if(state.scenario==='empty')return `${flowHead('SCR-SESSION-01','01 / PREPARE','','',btn('新しいセッションを作る','session:new','primary'))}<div class="flow-surface"><div class="flow-body"><h2>まだ試合がありません</h2><p>まずセッションと最初の試合を登録してください。</p>${btn('セッションと試合を入力する','session:new','primary')}</div></div>${flowNote}`;
  return `${flowHead('SCR-SESSION-01','01 / PREPARE','','',btn('新しいセッションを作る','session:new')+btn('新しい試合を登録','game-screen:new','primary'))}${flowStage(0)}<div class="flow-grid split">${flowSurface('登録済みの試合を選ぶ',`${flowRow('06','Game 06 · 北側高台','9月11日 · Sora / Ren / Mio · 録画4視点',btn('Game 06 の情報を編集','game-screen:06','sm'))}${flowRow('05','Game 05 · 橋の横断','9月10日 · Sora / Ren / Kai · Kaiの録画なし',btn('Game 05 の情報を編集','game-screen:05','sm'))}${flowRow('04','Game 04 · リング先入り','9月9日 · Sora / Ren / Mio · 録画3視点',btn('Game 04 の情報を編集','game-screen:04','sm'))}`)}${flowSurface('今週の作業範囲を確認する',`<strong>Pro Scrim Week 3</strong><p>Storm Point · 6試合 · 出場選手4名</p>${notice('試合と録画は別に管理','試合を登録してから視点ごとの録画を紐付けます。')}${link('録画の不足と処理を確認','SCR-INGEST-01','primary full')}`)}</div>${flowNote}`;
}
function sessionEditWorkflow(){
  const game=gameData[state.selectedGame] || gameData['06'];
  return `${flowHead('SCR-SESSION-02','01 / PREPARE','','',`${link('試合一覧へ戻る','SCR-SESSION-01')}${btn('変更を保存（デモ）','toast:ワイヤーフレームでは保存しません','primary')}`)}${flowStage(0)}${flowSurface(state.selectedSessionNew?'新しいセッションを作る':'セッション情報を編集する',`<div class="flow-grid three">${field('セッション名',state.selectedSessionNew?'':'Pro Scrim Week 3')}${select('種別',['練習試合','大会','ランク戦'])}${field('開始日',state.selectedSessionNew?'':'2026-09-07','date')}</div>`)}<div class="flow-grid split">${flowSurface('編集する試合を選ぶ',`${state.selectedSessionNew?'<p class="small">新しいセッションにはまだ試合がありません。最初の試合を入力してください。</p>':Object.keys(gameData).filter(x=>x!=='new').map(id=>flowRow(id,`Game ${id}`,gameData[id].recordings,btn('この試合を編集',`game:${id}`,state.selectedGame===id?'sm primary':'sm'))).join('')}${btn('新しい試合を追加','game:new','sm full')}`)}${flowSurface(state.selectedGame==='new'?'新しい試合の情報を入力する':`Game ${state.selectedGame} の情報を編集する`,`${field('試合名',state.selectedGame==='new'?'':`Game ${state.selectedGame}`)}${field('試合日',game.date,'date')}${select('地図',['Storm Point','World’s Edge'])}<fieldset class="player-fieldset"><legend>この試合に出場した選手</legend>${['Sora','Ren','Mio','Kai'].map(name=>check(name,game.players.includes(name))).join('')}</fieldset><p class="annotation">録画状態：${game.recordings}</p>${open('この試合に録画を登録','SCR-INGEST-02','sm full')}`)}</div>${flowNote}`;
}

/* The original templates remain as alternative rough layouts; this task-first direction is the default. */
Object.assign(renderers, {
  'SCR-DASH-01': todayWorkflow,
  'SCR-SESSION-01': sessionsWorkflow,
  'SCR-SESSION-02': sessionEditWorkflow,
  'SCR-INGEST-01': ingestWorkflow,
  'SCR-REVIEW-01': reviewWorkflow,
  'SCR-MAP-01': mapWorkflow,
  'SCR-TREND-01': trendsWorkflow,
  'SCR-OPP-01': opponentsWorkflow,
  'SCR-ROSTER-01': rosterWorkflow,
  'SCR-REPORT-01': reportsWorkflow,
  'SCR-REPORT-02': reportEditWorkflow
});

sidebar = function workflowSidebar(){
  const groups=[
    ['ここから始める',[['SCR-DASH-01','振り返りを始める','今やる仕事と全体の流れ','◫']]],
    ['01 試合と映像を揃える',[['SCR-SESSION-01','振り返る試合を選ぶ','対象の試合と出場者を確定','▤'],['SCR-INGEST-01','視点映像を揃える','誰の映像が足りないか確認','⇧']]],
    ['02 映像で事実を確かめる',[['SCR-REVIEW-01','映像から事実を確認','同じ場面を複数視点で照合','▷'],['SCR-MAP-01','位置と時刻を照合','地図の地点から映像へ戻る','⌖']]],
    ['03 次回行動を決めて伝える',[['SCR-REPORT-01','選手向け資料を選ぶ','事実と次回行動を共有','▣']]],
    ['04 次戦で効果を確かめる',[['SCR-TREND-01','改善行動の効果を確認','実施とVPS / OPSの変化を比較','▥']]],
    ['試合前の準備',[['SCR-OPP-01','対戦相手の動きを調べる','公開資料の根拠と鮮度を確認','◎'],['SCR-ROSTER-01','出場メンバーを比較','候補と判断理由を並べる','♟']]],
    ['設定',[['SCR-TEAM-01','チーム基本情報を設定','名前・言語を変更','⚙'],['SCR-MEMBER-01','メンバーと権限を管理','招待・権限を変更','♙'],['SCR-ACCOUNT-01','自分の表示設定を変更','言語・通知などを変更','◉'],['SCR-USAGE-01','利用量と上限を確認','容量・解析量を確認','▥']]]
  ];
  return `<aside class="sidebar" ${state.mobileNav?'style="display:flex;position:fixed;z-index:25;width:260px"':''}><a class="brand" href="#SCR-DASH-01">${brandLogo()}</a><div class="workspace-chip"><strong>◈ NORTHSTAR</strong><span>Pro Scrim Week 3 の振り返り</span></div>${groups.map(([name,items])=>`<div><div class="nav-heading">${name}</div><nav class="nav-group" aria-label="${name}">${items.map(([id,label,description,icon])=>`<button class="nav-link ${state.screen===id?'active':''}" data-action="screen:${id}" ${state.screen===id?'aria-current="page"':''}><span class="nav-icon">${icon}</span><span class="nav-copy"><strong>${label}</strong><small>${description}</small></span></button>`).join('')}</nav></div>`).join('')}<div class="sidebar-footer"><strong>AK　Akira</strong>分析担当者 · ワイヤーフレーム</div></aside>`;
};

topbar = function workflowTopbar(){return `<header class="topbar"><button class="btn sm mobile-menu" data-action="mobile-nav" aria-label="メニューを開く">☰</button><span class="team-context" aria-label="現在のチーム Northstar"><small>チーム</small><strong>Northstar</strong></span><span class="pill hide-sm">Pro Scrim Week 3</span><span class="spacer"></span>${languageControl()}${open('⌕ チーム内を検索','SCR-SEARCH-01','sm hide-sm')}${open('通知','SCR-NOTIFY-01','sm')}${open('録画を登録','SCR-INGEST-02','sm primary')}</header>`};
render();
