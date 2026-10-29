/* Thumaster 2.0 — design-review wireframe. Static-file mode is fictional; FastAPI mode is enhanced by live-workspace.js. */
const screens = [
  ['SCR-AUTH-01','ログイン','auth','◈'],['SCR-AUTH-02','パスワード再設定の申請','auth','◈'],
  ['SCR-AUTH-03','パスワード再設定','auth','◈'],['SCR-AUTH-04','メールアドレス確認','auth','◈'],
  ['SCR-AUTH-05','チーム招待','auth','◈'],['SCR-AUTH-06','初期設定','auth','◈'],
  ['SCR-DASH-01','振り返りを始める','workspace','◫'],['SCR-SESSION-01','振り返る試合を選ぶ','workspace','▤'],
  ['SCR-SESSION-02','試合情報を登録・編集','workspace','▤'],['SCR-INGEST-01','視点映像を揃える','workspace','⇧'],
  ['SCR-REVIEW-01','映像から事実を確認','workspace','▷'],['SCR-MAP-01','位置と時刻を照合','workspace','⌖'],
  ['SCR-TREND-01','改善行動の効果を確認','workspace','▥'],['SCR-OPP-01','対戦相手の動きを調べる','workspace','◎'],
  ['SCR-ROSTER-01','出場メンバーを比較','workspace','♟'],['SCR-REPORT-01','選手向け資料を選ぶ','workspace','▣'],
  ['SCR-REPORT-02','事実と次回行動をまとめる','workspace','▣'],['SCR-SHARE-01','共有された改善行動を見る','share','▣'],
  ['SCR-TEAM-01','チーム基本情報を設定','admin','⚙'],['SCR-MEMBER-01','メンバーと権限を管理','admin','♙'],
  ['SCR-ACCOUNT-01','自分の表示設定を変更','admin','◉'],['SCR-USAGE-01','利用量と上限を確認','admin','▥'],
  ['SCR-ERROR-01','アクセス権限なし','error','!'],['SCR-ERROR-02','資料が見つかりません','error','?'],
  ['SCR-ERROR-03','サービス利用不可','error','!']
];
const panels = [
  ['SCR-SEARCH-01','横断検索'],['SCR-NOTIFY-01','通知'],
  ['SCR-INGEST-02','録画登録'],['SCR-INGEST-03','録画の処理詳細'],
  ['SCR-REVIEW-02','根拠映像の編集'],['SCR-OPP-02','対戦相手の観測元'],
  ['SCR-OPP-03','対戦相手の比較'],['SCR-SHARE-02','共有設定']
];
// One user task per screen. Shared by page intros and drawer descriptions.
const screenPurpose = {
  'SCR-AUTH-01':'メールアドレスとパスワードで本人確認し、許可されたチームの作業へ進む。',
  'SCR-AUTH-02':'登録したメールアドレスを入力し、パスワードを再設定するための案内を受け取る。',
  'SCR-AUTH-03':'再設定リンクから新しいパスワードを登録し、ログインへ戻る。',
  'SCR-AUTH-04':'メールアドレスの確認状態を確かめ、未確認なら確認メールを再送する。',
  'SCR-AUTH-05':'招待されたチームと権限を確認し、自分のアカウントで参加する。',
  'SCR-AUTH-06':'表示名、言語、通知を設定して最初の作業を始める。',
  'SCR-DASH-01':'未確認のシーンを映像で確かめ、次回の改善行動を選手に共有する。',
  'SCR-SESSION-01':'分析するセッションと試合を登録し、対象の試合を選ぶ。',
  'SCR-SESSION-02':'セッションと試合の日時、地図、出場選手を登録・修正し、録画との対応を確認する。',
  'SCR-INGEST-01':'試合ごとの録画の有無と解析状態を確認し、不足・失敗に対応する。',
  'SCR-REVIEW-01':'複数視点の同じ場面を照合し、確認した事実と解釈を分けて記録する。',
  'SCR-MAP-01':'試合中の移動と接敵位置を地図と時間で確認し、元映像へ戻る。',
  'SCR-TREND-01':'決めた行動を次回試合で実行できたか、結果が変わったかを比較する。',
  'SCR-OPP-01':'公開資料から対戦相手の動きと出典を確認し、自チームの仮説と照合する。',
  'SCR-ROSTER-01':'出場編成案の実績と不確実な点を比較し、採用理由を残す。',
  'SCR-REPORT-01':'選手向け資料の下書きと共有済みの版を確認し、作成または編集する。',
  'SCR-REPORT-02':'確認した事実、解釈、次回の行動を選手向け資料にまとめ、共有前に点検する。',
  'SCR-SHARE-01':'自分に共有された資料で根拠映像と次回の行動を確認する。',
  'SCR-TEAM-01':'チーム名、言語、データの扱い方を確認して変更する。',
  'SCR-MEMBER-01':'メンバーを招待し、役割とアクセス権を確認・変更する。',
  'SCR-ACCOUNT-01':'自分のプロフィール、パスワード、通知、ログイン状態を管理する。',
  'SCR-USAGE-01':'メンバー数、保存容量、解析量の使用状況と上限を確認する。',
  'SCR-ERROR-01':'アクセスできない理由と必要な権限を確認し、管理者に相談する。',
  'SCR-ERROR-02':'指定した資料が見つからない理由を確認し、別の資料へ戻る。',
  'SCR-ERROR-03':'障害の影響と保存状態の確認方法を把握し、復旧を待つ。',
  'SCR-SEARCH-01':'試合、シーン、選手、レポートを検索して目的の資料を開く。',
  'SCR-NOTIFY-01':'解析完了、失敗、確認待ちの通知から該当作業へ戻る。',
  'SCR-INGEST-02':'録画ファイルに試合と撮影者の視点を指定して登録する。',
  'SCR-INGEST-03':'録画の処理工程と失敗理由を確認し、対象だけを再試行する。',
  'SCR-REVIEW-02':'根拠となる映像の開始・終了時刻、視点、共有範囲を編集する。',
  'SCR-OPP-02':'相手チームについて観測した事実、出典、更新日時を確かめる。',
  'SCR-OPP-03':'一覧の相手チームを同じ地図・期間・資料条件で比較する。',
  'SCR-SHARE-02':'選手向け表示を確認し、共有相手、期限、閲覧条件を決める。'
};
const screenUseCase = {
  'SCR-AUTH-01':'練習後の資料を開こうとして、まだログインしていないとき。',
  'SCR-AUTH-02':'パスワードが分からずログインできないとき。',
  'SCR-AUTH-03':'再設定メールに記載されたリンクを開いたとき。',
  'SCR-AUTH-04':'登録したメールアドレスの確認リンクを開いたとき。',
  'SCR-AUTH-05':'チームから参加の招待を受け取ったとき。',
  'SCR-AUTH-06':'初めて参加し、表示や通知の設定を決めるとき。',
  'SCR-DASH-01':'練習後に、未確認の場面や途中の作業から振り返りを再開するとき。',
  'SCR-SESSION-01':'新しい練習日を登録するか、振り返る試合を探すとき。',
  'SCR-SESSION-02':'試合の日時・地図・出場選手を訂正し、録画との対応を確認するとき。',
  'SCR-INGEST-01':'各試合の視点が揃ったか、録画の送信と解析が終わったか確認するとき。',
  'SCR-REVIEW-01':'解析候補が実際に起きたか、複数視点の映像で判断するとき。',
  'SCR-MAP-01':'移動や接敵の地点と時刻を映像と照合するとき。',
  'SCR-TREND-01':'前回決めた行動を次の試合で試せたか、結果と分けて確かめるとき。',
  'SCR-OPP-01':'対戦前に、公開資料から相手の移動や交戦の傾向を調べるとき。',
  'SCR-ROSTER-01':'次の試合の出場者と役割について、複数の案を比較するとき。',
  'SCR-REPORT-01':'資料の下書きを再開するか、共有済みの版を確認するとき。',
  'SCR-REPORT-02':'確認した事実と次回行動を、選手に伝える資料へまとめるとき。',
  'SCR-SHARE-01':'選手が自分に共有された振り返りと次回の行動を確認するとき。',
  'SCR-TEAM-01':'チーム名、言語、保存に関する設定を見直すとき。',
  'SCR-MEMBER-01':'新しいメンバーを招くか、所属者の役割を変更するとき。',
  'SCR-ACCOUNT-01':'自分の表示名、通知、認証情報を変更するとき。',
  'SCR-USAGE-01':'録画の追加前などに保存容量と解析量の残りを確認するとき。',
  'SCR-ERROR-01':'資料を開けず、必要な権限や相談先を確認するとき。',
  'SCR-ERROR-02':'共有されたURLなどから資料を開けなかったとき。',
  'SCR-ERROR-03':'障害や保守で作業を続けられず、保存状態を確かめるとき。',
  'SCR-SEARCH-01':'試合名や選手名から、チーム内の資料を探すとき。',
  'SCR-NOTIFY-01':'解析完了や失敗の連絡から、必要な作業へ戻るとき。',
  'SCR-INGEST-02':'試合と撮影者の視点が分かっている録画を登録するとき。',
  'SCR-INGEST-03':'特定の録画が失敗した理由と再試行の可否を調べるとき。',
  'SCR-REVIEW-02':'事実の根拠にする映像の区間・視点を直すとき。',
  'SCR-OPP-02':'相手の動きについて、観測に使った公開資料を確かめるとき。',
  'SCR-OPP-03':'一覧にある相手の動きを同じ条件で見比べるとき。',
  'SCR-SHARE-02':'資料を送る直前に、同じチーム内の受信者と期限を確かめるとき。'
};
const screenMap = Object.fromEntries(screens.map(s => [s[0],s]));
const uiTranslations = createUiTranslations(screens, panels, screenPurpose, screenUseCase);
const savedLocale = (() => { try { return localStorage.getItem('thumaster-wireframe-language') === 'en' ? 'en' : 'ja'; } catch { return 'ja'; } })();
const state = {
  screen: 'SCR-DASH-01', panel: null, theme: 'light', locale: savedLocale, scenario: 'normal', toast: '', mobileNav: false,
  reviewDecision: '未判定', sharePreview: false, selectedGame: '06', selectedSessionNew: false, selectedMapPoint: '02', selectedOpponent: 'Aster Union', selectedRecording: 'Kai', rosterChoice: '',
  reportDraft: {
    title: '次のスクリムでピーク前の確認を揃える',
    audience: 'チーム全員',
    fact: 'RenとMioの射撃開始に1.4秒の差。該当シーンを視点ごとに確認してください。',
    interpretation: 'カバー到着前にピークした可能性。理由は断定せず、次回も確認します。',
    action: '接敵前に位置・準備・3、2、1をコールする。担当：全員。'
  }
};
const opponentDetails = {
  'Aster Union': {place:'ザ・ウォール',observation:'3試合のうち1試合で内入りを選択し、北側高台から中央を通過。',source:'公開配信 Game 03 / 12:34 · 9/11確認'},
  'Cobalt Nine': {place:'チェックポイント',observation:'4試合のうち2試合で外周から橋へ移動。',source:'公開配信 Game 05 / 15:01 · 9/11確認'},
  'Ember Collective': {place:'カスケードフォール',observation:'5試合のうち3試合で南西から川沿いへ移動。',source:'公開配信 Game 04 / 10:23 · 9/10確認'}
};
const safe = value => String(value ?? '').replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const useCaseLine = id => `<p class="screen-usecase"><strong>使う場面</strong> ${safe(screenUseCase[id] || '')}</p>`;
const brandLogo = () => `<img class="brand-logo" src="./thumaster-logo-exact.svg" alt="Thumaster">`;
const languageControl = () => `<label class="language-control"><span>言語</span><select data-language aria-label="言語"><option value="ja" ${state.locale==='ja'?'selected':''}>日本語</option><option value="en" ${state.locale==='en'?'selected':''}>English</option></select></label>`;
const btn = (label, action, style='') => `<button class="btn ${style}" data-action="${safe(action)}">${safe(label)}</button>`;
const link = (label, id, style='') => btn(label, `screen:${id}`, style);
const open = (label,id,style='') => btn(label,`panel:${id}`,style);
const badge = (text,kind='') => `<span class="badge ${kind}">${safe(text)}</span>`;
const card = (title,body,action='') => `<section class="card"><div class="card-head"><h2>${title}</h2>${action}</div><div class="card-body">${body}</div></section>`;
const metric = (label,value,note) => `<div class="card metric"><div class="metric-label">${safe(label)}</div><div class="metric-value">${safe(value)}</div><div class="metric-note">${note}</div></div>`;
const field = (label,value='',type='text') => `<label class="field"><span>${safe(label)}</span><input class="input" type="${type}" value="${safe(value)}"></label>`;
const select = (label,options,selected=0) => `<label class="field"><span>${safe(label)}</span><select class="select" ${label==='言語'?'data-language aria-label="言語"':''}>${options.map((x,i)=>`<option ${label==='言語'?`value="${i===0?'ja':'en'}"`:''} ${(label==='言語'?(i===(state.locale==='ja'?0:1)):i===selected)?'selected':''}>${safe(x)}</option>`).join('')}</select></label>`;
const textarea = (label,value='') => `<label class="field"><span>${safe(label)}</span><textarea class="textarea">${safe(value)}</textarea></label>`;
const check = (label,checked=false) => `<label class="check"><input type="checkbox" ${checked?'checked':''}><span>${safe(label)}</span></label>`;
const notice = (title,detail,kind='') => `<div class="notice ${kind}"><span>●</span><div><strong>${title}</strong>${detail?`<br>${detail}`:''}</div></div>`;
const table = (columns,rows) => `<div class="table-wrap"><table class="table"><thead><tr>${columns.map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${x}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
const list = rows => `<div class="list">${rows.map(([n,title,sub,action,right])=>`<button class="list-item" data-action="${action}"><span class="index-square">${n}</span><span class="grow"><strong>${title}</strong><span class="sub">${sub}</span></span>${right || '<span class="muted">↗</span>'}</button>`).join('')}</div>`;
const map = () => `<div class="map-placeholder"><div class="map-path"></div><button class="map-pin ${state.selectedMapPoint==='01'?'selected':''}" data-action="map:01" aria-label="地点01を選ぶ" style="left:28%;top:62%">01</button><button class="map-pin ${state.selectedMapPoint==='02'?'selected':''}" data-action="map:02" aria-label="地点02を選ぶ" style="left:52%;top:39%">02</button><button class="map-pin ${state.selectedMapPoint==='03'?'selected':''}" data-action="map:03" aria-label="地点03を選ぶ" style="left:69%;top:25%">03</button><div class="map-label">MAP / POSITION IS ESTIMATED</div></div>`;
const chart = () => `<div class="chart">${[47,69,58,76,62,85,72].map((h,i)=>`<div class="chart-bar ${i%2?'secondary':''}" style="height:${h}%"><span>${i+1}</span></div>`).join('')}</div><p class="tiny muted" style="margin:27px 0 0">説明用のダミーチャート · 数値と計算式は未確定</p>`;
const page = (id,title,description,actions,body) => `<div class="page-head"><div><div class="screen-id">${id} / WIREFRAME</div><h1>${screenMap[id]?.[1] || title}</h1><p>${screenPurpose[id] || description}</p></div><div class="page-actions">${actions}</div></div>${context()}${scenarioBanner()}${body}<div class="wireframe-note">THUMASTER 2.0 · 設計検討用 / 架空データ / 実際の処理・認証・共有は行いません</div>`;
const context = () => `<div class="context-bar"><span class="eyebrow">分析条件</span><span>Pro Scrim Week 3</span><span class="context-sep">/</span><span>Storm Point</span><span class="context-sep">/</span><span>9/7–9/11</span><span class="context-sep">/</span><span>全選手</span></div>`;
const scenarioBanner = () => state.scenario === 'normal' ? '' : `<div class="state-banner">${state.scenario==='empty'?notice('空状態の確認','この画面で対象データがない場合の導線を確認できます。'):state.scenario==='partial'?notice('一部の資料を表示できません','録画1本が欠損しています。取得済みの結果は表示し、失敗部分だけ再試行します。','warn'):notice('通信エラー','直前の操作は確定していません。追跡ID: WF-2026-0919','danger')}</div>`;
const empty = (title,detail,action,id) => `<div class="card state-empty"><div class="symbol">◇</div><h2>${title}</h2><p>${detail}</p>${link(action,id,'primary')}</div>`;

function renderToday(){
  if(state.scenario==='empty') return page('SCR-DASH-01','Today','今日の振り返りを、次の一手につなげる。',link('動画を追加','SCR-INGEST-01','primary'),empty('まだ作業がありません','セッションを作成し、試合と録画を登録すると優先レビューがここに表示されます。','セッションを作成','SCR-SESSION-02'));
  return page('SCR-DASH-01','Today','今日の振り返りを、次の一手につなげる。',link('レポートを見る','SCR-REPORT-01'),`<div class="grid" style="gap:18px"><div class="hero"><div><div class="eyebrow">TODAY'S FOCUS · 6 SCENES</div><h2>次のスクリムに持ち込む、<br>3つの気づき。</h2><p>ピークのずれ、良い射線の再現、移動判断を重要な順に振り返ります。</p></div>${link('5分レビューを開始 →','SCR-REVIEW-01','primary')}</div><div class="grid four">${metric('未レビュー','06','重要シーンを確認')}${metric('確認待ち','04','映像品質・解釈')}${metric('次回アクション','02','担当と期限を確認')}${metric('未共有','01','選手向け資料に追加')}</div><div class="grid aside"><div class="stack"><section class="card"><div class="card-head"><h2>優先してレビュー</h2>${link('すべて見る','SCR-REVIEW-01','sm')}</div>${list([['01','北側の高台で、ピークが1.4秒ずれた','Game 06 · 12:34–13:09 · 3視点','screen:SCR-REVIEW-01',badge('優先度 高','warn')],['02','リング先入り後、クロスで押し返した','Game 04 · 10:23–10:58 · 良い再現例','screen:SCR-REVIEW-01',badge('良い動き','ok')],['03','橋の横断中に接敵、離脱の判断は妥当か','Game 05 · 15:01–15:36 · 2視点','screen:SCR-REVIEW-01',badge('判断を確認','info')]])}</section>${card('前回からの変化',`<div class="grid two">${metric('安置先入り時の生存率','72%','Week 2 → Week 3 / n=18')}${metric('ピーク時間差','1.4秒','直近6戦闘 / 悪化の候補')}</div><p class="annotation" style="margin:16px 0 0">変化だけで改善や悪化を断定しません。条件と根拠映像を照合します。</p>`,link('根拠を比較','SCR-TREND-01','sm'))}</div><div class="stack">${card('直近のセッション',`<h3>Pro Scrim Week 3</h3><p class="small">Storm Point · 6試合 · ロスター4名</p><div class="field-row"><span class="pill ok">完了 5</span><span class="pill warn">確認待ち 1</span></div>`,link('試合を見る','SCR-SESSION-01','sm'))}${card('取り込み・解析',`${notice('解析済みのシーンを確認できます','1本の動画でファイルの再選択が必要です。','warn')}<div style="margin-top:14px">${open('キューを見る','SCR-INGEST-03','sm')}</div>`)}${card('次回試すアクション',`${check('接敵前に「位置・準備・3、2、1」をコールする')}${check('リング2の移動開始を30秒早める')}<p class="tiny" style="margin:13px 0 0">実施と結果確認は別の状態です。</p>`,link('フィードバックをまとめる','SCR-REPORT-02','sm'))}</div></div></div>`);
}

function renderSessions(){
  if(state.scenario==='empty') return page('SCR-SESSION-01','セッション・試合','振り返る範囲と資料を整理します。',link('新しいセッションを作成','SCR-SESSION-02','primary'),empty('セッションはまだありません','最初の練習または大会を登録してください。','セッションを作る','SCR-SESSION-02'));
  return page('SCR-SESSION-01','セッション・試合','振り返る範囲と資料を整理します。',link('新しいセッションを作成','SCR-SESSION-02','primary'),`${card('セッション一覧',table(['セッション','期間 / 地図','試合','録画','レビュー','操作'],[['<strong>Pro Scrim Week 3</strong><small>練習試合</small>','9/7–9/11 · Storm Point','6','18本 · 1本再選択','6件未レビュー',link('試合情報を編集','SCR-SESSION-02','sm')],['<strong>Pro Scrim Week 2</strong><small>練習試合</small>','8/31–9/4 · Storm Point','6','17本 · 2視点不足','完了',link('試合情報を編集','SCR-SESSION-02','sm')]]))}<div class="grid three" style="margin-top:16px">${metric('対象セッション','02','チーム内')}${metric('登録試合','12','直近2週')}${metric('録画不足','02','非出場とは区別')}</div>`);
}

function renderSessionEdit(){return page('SCR-SESSION-02','セッション編集','セッション、試合、出場選手と録画の関係を管理します。',`${link('セッション一覧に戻る','SCR-SESSION-01')}${btn('変更を保存','toast:保存しました','primary')}`,`<div class="grid aside"><div class="stack">${card('基本情報',`<div class="form-stack">${field('セッション名','Pro Scrim Week 3')}<div class="field-row">${select('種別',['練習試合','大会','ランク戦'])}${select('地図',['Storm Point','World’s Edge'])}</div><div class="field-row">${field('開始日時','2026-09-07','date')}${field('終了日時','2026-09-11','date')}</div>${textarea('メモ','リング先入りと接敵の判断を重点確認。')}</div>`)}${card('試合',table(['試合','出場選手','録画・視点','状態'],[['Game 06','Sora / Ren / Mio','3選手 + 観戦','解析完了'],['Game 05','Sora / Ren / Kai','Kai視点が品質確認待ち','一部利用可能'],['Game 04','Sora / Ren / Mio','3選手','解析完了']]))}</div><div class="stack">${card('出場と録画の区別',`${notice('試合ごとに確認','「非出場」と「出場したが録画なし」を区別します。')}<div class="form-stack" style="margin-top:16px">${['Sora','Ren','Mio','Kai'].map((n,i)=>`<div class="list-item" style="padding:8px 0"><strong class="grow">${n}</strong>${select('',i===3?['非出場','出場・録画なし','出場・録画あり']:['出場・録画あり','出場・録画なし','非出場'])}</div>`).join('')}</div>`)}${card('関連付けの変更',`<p class="small">解析後に試合や視点を変更する場合、影響するシーン、集計、レポートを確認してから確定します。</p>${open('録画の関連付けの影響を確認','SCR-INGEST-03','sm')}`)}</div></div>`)}

function renderIngest(){
  return page('SCR-INGEST-01','Ingest','録画を試合・視点に紐付け、送信と解析を別々に追跡します。',open('動画を追加','SCR-INGEST-02','primary'),`<div class="grid aside"><div class="stack">${card('解析キュー',table(['録画 / 試合','送信','解析','品質','操作'],[['<strong>Ren視点 · Game 06</strong><small>MP4 · 28分</small>',badge('送信済み','ok'),badge('完了','ok'),'問題なし',open('詳細','SCR-INGEST-03','sm')],['<strong>Sora視点 · Game 06</strong><small>MP4 · 31分</small>',badge('送信済み','ok'),badge('確認待ち','warn'),'HUD一部読取不可',open('詳細','SCR-INGEST-03','sm')],['<strong>Kai視点 · Game 03</strong><small>MOV · 26分</small>',badge('失敗','danger'),badge('未開始'),'ファイル再選択が必要',open('再試行','SCR-INGEST-03','sm')]]))}${card('送信と解析の流れ',`<div class="grid three">${['01 · ファイルを登録','02 · 視点と時刻を同期','03 · 候補を確認'].map(x=>`<div class="placeholder" style="min-height:80px"><strong>${x}</strong></div>`).join('')}</div><p class="small" style="margin:14px 0 0">送信完了は解析完了を意味しません。進捗を工程別に表示します。</p>`)}</div><div class="stack">${card('受付前の確認',`${notice('ファイル条件は未決定','対応形式、容量、長さ、同時処理数は決定後にここへ表示します。','warn')}<div class="form-stack" style="margin-top:15px">${select('映像の種別',['選手視点','観戦視点'])}${select('視点の担当',['Ren','Sora','Mio','Kai'])}${select('紐付ける試合',['Game 06','Game 05','Game 04'])}${open('ファイルを選択','SCR-INGEST-02','full')}</div>`)}${card('映像品質',`${badge('一部利用可能','warn')}<p class="small" style="margin:12px 0 0">Game 05：音声なし、HUD読取が不安定。音声・HUD由来の指標は利用できないか、推定として扱います。</p>`)}</div></div>`);
}

function renderReview(){
  return page('SCR-REVIEW-01','Review','映像で事実を確かめ、解釈と次の行動を分けて残します。',`${open('クリップを作成','SCR-REVIEW-02')}${btn('レビュー済みにする','toast:シーンを確認済みにしました','primary')}`,`<div class="grid review"><section class="card"><div class="card-head"><h2>戦闘シーン</h2>${badge('6件')}</div>${list([['06','北側の高台でピークがずれた','12:34 · ピーク連携','toast:このシーンを表示中',badge('未確認','warn')],['04','リング先入り後に押し返した','10:23 · 良い再現例','toast:別シーンの表示例',badge('確認済み','ok')],['05','橋の横断中に接敵','15:01 · 移動判断','toast:別シーンの表示例',badge('保留','info')]])}</section><div class="stack">${card('同期ビュー · Game 06',`<div class="grid two">${['Sora / IGL','Ren / Entry','Mio / Anchor','Coach / 観戦'].map(x=>`<div class="video-placeholder"><span>▷ ${x} · 12:34</span></div>`).join('')}</div><div class="field-row" style="margin-top:14px">${btn('◀ 5秒','toast:5秒戻る','sm')}${btn('▷ 同期再生','toast:再生プレビュー','sm')}</div><div class="timeline"><i style="left:12%"></i><small style="left:12%">コール</small><i style="left:38%"></i><small style="left:38%">戦闘開始</small><i style="left:68%"></i><small style="left:68%">被弾</small></div><div class="field-row">${select('再生速度',['1×','0.5×','1.5×','2×'])}${select('音声視点',['Sora','Ren','Mio','Coach'])}</div><div style="margin-top:15px">${btn('音量・同期ずれを調整','toast:同期補正パネルの検討対象','sm')}</div>`)}${card('計測値と元映像',`<div class="grid four">${metric('VPS','66','選手・シーン単位 / 算出式未定義')}${metric('ピーク時間差','1.4秒','映像で要確認')}${metric('最大選手間距離','32m','位置推定')}${metric('命中率','35.0%','49命中 / 140発')}</div><div style="margin-top:14px">${open('定義・入力値・版を確認','SCR-REVIEW-02','sm')}</div>`)}${card('観測 → 解釈 → アクション',`<div class="form-stack">${textarea('確認した事実','Renの射撃開始からMioの射撃開始まで1.4秒。')}${textarea('人の解釈','カバー到着前にピークした可能性。')}${textarea('次に試す行動','接敵前に位置と準備完了をコールする。')}<div class="field-row">${select('担当',['全員','Sora','Ren','Mio'])}${select('状態',['未実施','実施中','実施済み','結果確認済み'])}</div>${btn('根拠付きで保存','toast:保存しました','primary')}</div>`)}</div><div class="stack">${card('判断の裏付け',`${badge('検出候補','info')}<p style="margin:12px 0">映像上では射撃開始の時間差が見えます。理由は人が検証します。</p>${notice('資料充足','3選手視点 + 観戦視点。位置は推定、人の確認は未完了。')}<div style="margin-top:14px">${open('クリップ・根拠を見る','SCR-REVIEW-02','sm')}</div>`)}${card('戦闘位置',`${map()}<div style="margin-top:13px">${link('Macro Mapで見る','SCR-MAP-01','sm')}</div>`)}${card('アナリストのノート',`${textarea('ノート','そのタイミングを選んだ理由は？')}${check('内部メモとして保存',true)}<div style="margin-top:12px">${btn('ノートを保存','toast:ノートを保存しました','sm')}</div>`)}</div></div>`);
}

function renderMap(){return page('SCR-MAP-01','Macro Map','移動と接敵の文脈から、チームの判断を振り返る。',btn('表示レイヤー','toast:レイヤーを切り替えます'),`<div class="grid aside"><div class="stack">${card('Storm Point · Game 06',`<div class="field-row three">${check('移動軌跡',true)}${check('リング推移',true)}${check('戦闘・接敵',true)}</div><div style="margin-top:14px">${map()}</div><div class="timeline"><i style="left:18%"></i><small style="left:18%">移動</small><i style="left:53%"></i><small style="left:53%">接敵</small><i style="left:83%"></i><small style="left:83%">リング進入</small></div>`)}${card('時間帯別ファイト',chart())}</div><div class="stack">${card('選択した地点',`${badge('Game 06 · 敗北','danger')}<h3 style="margin-top:12px">北側の高台で、ピークがずれた</h3><p>12:34 · リング3 · 推定位置</p>${notice('観測と解釈を分離','射撃開始差1.4秒は観測値。連携不足は仮説です。','warn')}<div style="margin-top:15px">${link('Reviewで映像を見る','SCR-REVIEW-01','primary')}</div>`)}${card('このルートの仮説',`<h3>北側ルートは収縮後に接触しやすい？</h3><p>接触3件 / 6試合。少数サンプルとして表示します。</p>${link('対戦相手と比較','SCR-OPP-01','sm')}`)}</div></div>`)}

function renderTrends(){return page('SCR-TREND-01','Team Trends','指標の変化を、対象条件と元映像と一緒に確認します。',link('Reviewを開く','SCR-REVIEW-01'),`<div class="grid aside"><div class="stack">${card('比較条件',`<div class="field-row three">${select('期間',['全期間','Week 3','Week 2'])}${select('選手',['Ren','Sora','Mio'])}${select('地図',['Storm Point','全地図'])}</div><p class="annotation" style="margin:15px 0 0">期間内の5戦闘、欠損0。ゲーム更新・解析方式変更時は比較可否を表示します。</p>`)}<div class="grid three">${metric('OPS','76','選手・指定期間単位 / 版 v1')}${metric('期間内命中率','40.3%','347命中 / 860発')}${metric('期間内総ダメージ','4,957','有効5戦闘')}</div>${card('シーン別履歴',table(['戦闘 / 時刻','VPS','命中率','ダメージ','根拠'],[['<strong>Game 06 · 北側高台</strong><small>Week 3 · 12:34</small>','69','38.0%','1,064',link('映像','SCR-REVIEW-01','sm')],['<strong>Game 05 · 橋の横断</strong><small>Week 3 · 15:01</small>','62','45.0%','1,485',link('映像','SCR-REVIEW-01','sm')],['<strong>Game 02 · 再接敵</strong><small>Week 2 · 12:21</small>','84','35.0%','819',link('映像','SCR-REVIEW-01','sm')]]))}</div><div class="stack">${card('VPS / OPS の読み方',`${badge('正式指標','ok')}<p style="margin-top:12px">VPS は選手・シーン単位、OPS は選手・指定期間単位です。算出式・尺度・入力値は要件確定時に別途定義します。</p>${notice('算出不能 ≠ 0点','映像欠損時は理由を示し、0と区別します。','warn')}`)}${card('指標の推移',chart())}${card('選択シーン',`<div class="video-placeholder"><span>▷ Ren / Game 06 / 12:34</span></div><p class="small" style="margin-top:12px">各値から対象シーンと元映像へ追跡します。</p>${link('Reviewで開く','SCR-REVIEW-01','sm')}`)}</div></div>`)}

function renderOpponents(){return page('SCR-OPP-01','Opponents','対戦相手の観測を、出典と更新日時を添えて比較します。',open('選択チームを比較','SCR-OPP-03','primary'),`<div class="grid aside"><div class="stack">${card('検証する仮説',`${field('問い','外入りチームの増加で、北側ルートの接触が増える？')}<div style="margin-top:12px">${btn('対象チームを絞る','toast:仮説による絞り込み','sm')}</div>`)}${card('対戦相手データベース',table(['選択','チーム / 選手','構成 / POI','移動','観測 / 出典','根拠'],[['<input type="checkbox" checked aria-label="Aster Unionを比較">','<strong>Aster Union</strong><small>Aster-01 / 02 / 03</small>','攻撃型 · ザ・ウォール','内入り · 北側高台 → 中央','3試合 · 公開配信',open('見る','SCR-OPP-02','sm')],['<input type="checkbox" checked aria-label="Cobalt Nineを比較">','<strong>Cobalt Nine</strong><small>Cobalt-01 / 02 / 03</small>','防御型 · チェックポイント','外入り · 外周 → 橋','4試合 · 公開配信',open('見る','SCR-OPP-02','sm')],['<input type="checkbox" aria-label="Ember Collectiveを比較">','<strong>Ember Collective</strong><small>Ember-01 / 02 / 03</small>','混成 · カスケードフォール','外入り · 南西 → 川沿い','5試合 · 公開配信',open('見る','SCR-OPP-02','sm')]]))}</div><div class="stack">${card('構成の変化',`${chart()}<p class="small" style="margin-top:26px">期間ごとの代表構成。現行環境のピック率ではありません。</p>`)}${card('観測メモ',`${badge('解釈','info')}<h3 style="margin-top:10px">攻撃型の構成が増加</h3><p>構成だけで攻撃性を決めず、交戦開始位置と時間を確認します。</p>${open('観測元を確認','SCR-OPP-02','sm')}`)}</div></div>`)}

function renderRoster(){return page('SCR-ROSTER-01','Roster Lab','数字と、いっしょに戦うための条件を並べて検討します。',`${btn('A / B を比較','toast:編成案の比較')}${btn('編成案を保存','toast:編成案を保存しました','primary')}`,`<div class="grid aside"><div class="stack">${card('編成条件',`<div class="field-row three">${select('地図',['Storm Point','World’s Edge'])}${select('戦術',['先入り・射線で保持','外入り・接敵重視'])}${select('キャラクター構成',['バンガロール / ワットソン / ニューキャッスル','別構成'])}</div>`)}${card('出場編成 · 案 A',`<div class="grid three">${['Sora · IGL','Ren · Entry','Mio · Anchor'].map((x,i)=>`<div class="placeholder" style="min-height:115px"><div><span class="eyebrow">SLOT 0${i+1}</span><h3 style="margin:8px 0">${x}</h3><span class="small">${['バンガロール','ワットソン','ニューキャッスル'][i]}</span></div></div>`).join('')}</div><div style="margin-top:13px">${btn('編成案 B を表示','toast:編成案 B の検討','sm')}</div>`)}${card('一緒に出場した際の観測',`<div class="grid three">${metric('共同出場','24','試合')}${metric('ファイト勝率','58%','条件差あり')}${metric('ピーク時間差','0.8秒','観測値')}</div><p class="annotation" style="margin:15px 0 0">実績がない編成は「実績なし」と表示し、推定で埋めません。</p>`)}</div><div class="stack">${card('候補選手',list([['S','Sora','IGL / Support · コール負荷 高','toast:Soraを配置'],['R','Ren','Entry / Fragger · 近距離','toast:Renを配置'],['M','Mio','Anchor / Flex · コール負荷 低','toast:Mioを配置'],['K','Kai','Flex / Reserve · 近〜中距離','toast:Kaiを配置']]))}${card('判断理由 · 内部',`${textarea('この編成を選ぶ理由','Soraの状況整理とMioのリセットを軸に、Renの初動を活かす。')}${notice('選手向け資料には含めません','編成理由は内部メモとして管理します。','warn')}`)}</div></div>`)}

function renderReports(){return page('SCR-REPORT-01','Reports','事実、解釈、次回行動を選手に伝わる資料へまとめます。',link('新しいレポート','SCR-REPORT-02','primary'),`${card('レポート一覧',table(['タイトル','対象','状態','更新','操作'],[['<strong>スクリム終了後の5分サマリー</strong><small>Pro Scrim Week 3</small>','チーム全員',badge('下書き','warn'),'9/11 21:48',link('編集','SCR-REPORT-02','sm')],['<strong>リング先入りの再現ポイント</strong><small>Pro Scrim Week 2</small>','Sora / Ren / Mio',badge('共有済み','ok'),'9/4 18:10',link('表示','SCR-SHARE-01','sm')]]))}<div class="grid three" style="margin-top:16px">${metric('下書き','01','共有前に内容を確認')}${metric('共有済み','01','版と対象者を記録')}${metric('未共有インサイト','01','Reviewから追加')}</div>`)}

function renderReportEdit(){return page('SCR-REPORT-02','レポート編集','共有相手が見る内容だけを選び、根拠とともに伝えます。',`${link('一覧に戻る','SCR-REPORT-01')}${btn('下書きを保存','toast:下書きを保存しました')}${open('共有設定へ','SCR-SHARE-02','primary')}`,`<div class="grid aside"><div class="stack">${card('本文の編集',`<div class="form-stack">${field('タイトル','スクリム終了後の5分サマリー')}${select('対象',['チーム全員','Sora','Ren','Mio'])}${textarea('01 · 確認した事実','Renの射撃開始からMioの射撃開始まで1.4秒。')}${textarea('02 · 人の解釈','カバー到着前にピークした可能性があります。')}${textarea('03 · 次回の行動','接敵前に「位置・準備・3、2、1」をコールする。')}${open('クリップを選択','SCR-REVIEW-02','sm')}</div>`)}${card('選手向けプレビュー',`<div class="eyebrow">REPORT / PLAYER VIEW</div><h3 style="margin:12px 0">今日の5分レビュー</h3><p>まず映像で事実を見て、次回の行動を確認してください。</p><div class="video-placeholder" style="max-width:470px"><span>▷ Game 06 · 12:34–13:09</span></div><p class="small" style="margin:12px 0 0">接敵前に位置と準備完了をコールする · 担当：全員</p>`)} </div><div class="stack">${card('保存したインサイト',`${badge('根拠付き','ok')}<h3 style="margin-top:10px">先入り後のクロスで押し返した</h3><p>選手視点3本と観戦視点で確認済み。</p>${link('根拠を開く','SCR-REVIEW-01','sm')}`)}${card('共有から除外',`${badge('内部メモ','warn')}<p style="margin-top:12px">編成理由と内部ノートは、本文、クリップ、書き出しに含めません。</p>${notice('共有前に再確認','プレビューと実際の閲覧権限を同じ条件にします。','warn')}`)}${card('共有操作',`${open('共有対象・期限を確認','SCR-SHARE-02','full primary')}<div style="margin-top:8px">${btn('本文をコピー','toast:コピーの動作例','full')}</div><p class="tiny" style="margin:12px 0 0">外部サービスへ自動投稿しません。</p>`)}</div></div>`)}

function renderShared(){const report=state.sharePreview?state.reportDraft:{title:'リング先入りの再現ポイント',audience:'Sora / Ren / Mio',fact:'Renの射撃開始からMioの射撃開始まで1.4秒。',interpretation:'カバー到着前にピークした可能性があります。',action:'接敵前に位置と準備完了をコールする。'};return `<div class="auth-shell"><div class="auth-form-panel"><div class="brand">${brandLogo()}</div><div class="auth-content" style="max-width:620px"><div class="screen-id">SCR-SHARE-01 / PLAYER VIEW</div><h1>${screenMap['SCR-SHARE-01'][1]}</h1><p>${screenPurpose['SCR-SHARE-01']}</p>${useCaseLine('SCR-SHARE-01')}<p>Pro Scrim Week 3 · ${state.sharePreview?'共有前プレビュー（未共有）':'共有済み · 9/11 21:48'}</p><div class="player-next"><span>次回のスクリムで ${safe(report.audience)} が試すこと</span><strong>${safe(report.action)}</strong><small>次回スクリムの終了後に、実行できたかと結果をコーチと確認します。</small></div>${state.sharePreview?notice('共有前プレビュー','編集した本文と対象が反映されています。ここではまだ共有されません。','warn'):notice('あなたに共有された資料','選手向けの事実・解釈・行動のみを表示します。','ok')}<div class="card" style="margin-top:22px"><div class="card-body"><div class="eyebrow">01 / FACT</div><h2 style="margin-top:8px">${safe(report.title)}</h2><p>${safe(report.fact)}</p><div class="video-placeholder"><span>根拠映像の配置案 · Game 06 · 12:34–13:09（このデモでは再生不可）</span></div><div class="eyebrow" style="margin-top:18px">02 / INTERPRETATION</div><p>${safe(report.interpretation)}</p><div class="eyebrow">03 / NEXT ACTION</div><p style="color:var(--ink)">${safe(report.action)}</p></div></div><div style="margin-top:20px">${state.sharePreview?link('資料の編集に戻る','SCR-REPORT-02'):btn('閲覧を終える（デモ）','toast:ワイヤーフレームでは画面を閉じません')}</div></div><div class="auth-footer">設計レビュー用 · 共有や動画配信は行いません。</div></div><div class="auth-art"><div class="eyebrow">THUMASTER / REPORT</div><div><h2>根拠を見て、<br>次の一手を揃える。</h2><p>共有先には内部メモと編成理由を表示しません。</p></div><span class="mono tiny">NORTHSTAR · APEX LEGENDS</span></div></div>`}

function renderTeam(){return page('SCR-TEAM-01','チーム設定','チームの基本情報とデータ管理方針を確認します。',btn('変更を保存','toast:チーム設定を保存しました','primary'),`<div class="grid aside"><div class="stack">${card('基本情報',`<div class="form-stack">${field('チーム名','Northstar')}${select('タイムゾーン',['Asia/Tokyo','UTC'])}${select('既定言語',['日本語','English'])}</div>`)}${card('データ保存',`${notice('方針の決定が必要','動画、解析結果、メモ、共有資料ごとに保存期間と削除条件を定めます。','warn')}<p class="small" style="margin:15px 0 0">チーム削除や契約終了時はデータの取り出し・引き継ぎ・削除を別手順で確認します。</p>`)}</div><div class="stack">${card('管理メニュー',`${link('メンバーと招待','SCR-MEMBER-01','full')}<div style="margin-top:8px">${link('利用量と契約','SCR-USAGE-01','full')}</div>`)}${card('アクセス',`<p>チーム管理者のみ変更できます。チームを切り替えると未保存の編集内容を確認します。</p>`)}</div></div>`)}

function renderMembers(){return page('SCR-MEMBER-01','メンバー・招待','誰がどの範囲の資料を扱えるか管理します。',btn('メンバーを招待','toast:招待ダイアログの検討対象','primary'),`${card('メンバー一覧',table(['氏名','メール','役割','状態','操作'],[['<strong>Akira</strong>','akira@example.test','管理者',badge('参加済み','ok'),btn('変更','toast:役割変更の確認','sm')],['<strong>Sora</strong>','sora@example.test','コーチ',badge('参加済み','ok'),btn('変更','toast:役割変更の確認','sm')],['<strong>Ren</strong>','ren@example.test','選手',badge('参加済み','ok'),btn('変更','toast:役割変更の確認','sm')],['<strong>Mio</strong>','mio@example.test','選手',badge('招待中','warn'),btn('再送','toast:再送前の確認','sm')]]))}<div class="grid two" style="margin-top:16px">${card('新しい招待',`<div class="form-stack">${field('メールアドレス','','email')}${select('役割',['選手','分析担当者','コーチ','管理者'])}${btn('宛先と権限を確認','toast:招待内容を確認します','primary')}</div>`)}${card('安全な変更',`${notice('最後の管理者は停止できません','役割変更と利用停止は既存のアクセスを失効させ、監査記録を残します。','warn')}`)}</div>`)}

function renderAccount(){return page('SCR-ACCOUNT-01','アカウント・セキュリティ','本人情報と認証・通知の設定を確認します。',btn('変更を保存','toast:アカウント設定を保存しました','primary'),`<div class="grid aside"><div class="stack">${card('プロフィール',`<div class="form-stack">${field('表示名','Akira')}${field('メールアドレス','akira@example.test','email')}${badge('メール確認済み','ok')}${select('言語',['日本語','English'])}</div>`)}${card('セキュリティ',`${notice('再認証が必要','メール、パスワード、多要素認証の変更時は本人確認を行います。')}<div class="field-row" style="margin-top:15px">${btn('パスワードを変更','screen:SCR-AUTH-03')}${btn('すべての端末からログアウト','toast:確認ダイアログを表示します')}</div>`)}</div><div class="stack">${card('通知',`${check('解析完了',true)}${check('確認待ち',true)}${check('アクション期限',true)}`)}${card('現在のセッション',`<p>このブラウザ · 最終利用 9/19 10:00</p>${btn('現在の端末からログアウト','screen:SCR-AUTH-01','sm')}`)}</div></div>`)}

function renderUsage(){return page('SCR-USAGE-01','利用量・契約','集計期間と上限、残量、到達時の動作を確認します。',link('チーム情報を変更','SCR-TEAM-01'),`${notice('料金・上限は未確定','この画面の数値はレイアウト確認用の架空データです。','warn')}<div class="grid three" style="margin-top:16px">${metric('メンバー','4 / 10','集計期間：9月')}${metric('保存容量','128 / 500 GB','元動画と派生動画を含む案')}${metric('解析量','48 / 100 時間','月間動画時間の案')}</div>${card('利用の内訳',table(['項目','使用量','上限','期間','到達時'],[['メンバー','4名','10名','契約期間','招待を停止'],['動画保存','128 GB','500 GB','累積','新規送信を停止'],['解析時間','48時間','100時間','月間','新規解析を停止']]))}`)}

function renderError(id){const data={'SCR-ERROR-01':['アクセス権限がありません','この資料の内容は表示できません。現在のチームとアカウントを確認し、必要なら管理者へお問い合わせください。','403'], 'SCR-ERROR-02':['対象が見つかりません','URLが変わったか、資料が削除・共有取消されている可能性があります。','404'], 'SCR-ERROR-03':['現在ご利用いただけません','障害またはメンテナンス中です。直前の操作が保存されたかは復旧後に確認してください。','503']}[id];return `<div class="auth-shell"><div class="auth-form-panel"><div class="brand">${brandLogo()}</div><div class="auth-content"><div class="eyebrow">${id} / ${data[2]}</div><h1 style="margin-top:12px">${data[0]}</h1><p>${screenPurpose[id]}</p>${useCaseLine(id)}<p>${data[1]}</p>${id==='SCR-ERROR-03'?notice('追跡ID：WF-2026-0919','問い合わせ時にこの番号をお知らせください。','warn'):''}<div style="margin-top:24px">${link('今日の作業に戻る','SCR-DASH-01','primary')}</div></div><div class="auth-footer">設計レビュー用の状態画面です。</div></div><div class="auth-art"><div class="eyebrow">THUMASTER / SYSTEM STATE</div><div><h2>状態を伝え、<br>次の行動を示す。</h2><p>権限がない場合は保護対象の内容を表示しません。</p></div><span class="mono tiny">ERROR / ${data[2]}</span></div></div>`}

function renderAuth(id){
  const content={
    'SCR-AUTH-01':['ログイン','チームの振り返りワークスペースへ。',`${field('メールアドレス','','email')}${field('パスワード','','password')}${link('ログイン','SCR-DASH-01','primary full')}<div style="margin-top:15px">${link('パスワードを忘れた場合','SCR-AUTH-02','ghost')}</div>`],
    'SCR-AUTH-02':['パスワード再設定','登録メールアドレスに再設定手順を案内します。',`${field('メールアドレス','','email')}${btn('再設定メールを送信','toast:登録有無にかかわらず同じ完了表示','primary full')}${link('ログインに戻る','SCR-AUTH-01','ghost')}`],
    'SCR-AUTH-03':['新しいパスワード','有効期限付きのリンクから変更します。',`${field('新しいパスワード','','password')}${field('確認用パスワード','','password')}${btn('パスワードを変更','toast:変更完了とセッション状態を表示','primary full')}${link('ログインへ','SCR-AUTH-01','ghost')}`],
    'SCR-AUTH-04':['メールアドレスを確認','確認メールのリンクを開いてください。',`${notice('確認待ち','リンクの期限切れや再送もこの画面で案内します。')}${btn('確認メールを再送','toast:再送完了','primary full')}${link('ログインへ','SCR-AUTH-01','ghost')}`],
    'SCR-AUTH-05':['Northstar に参加','招待先と役割を確認してから参加します。',`${notice('Akira からの招待','チーム：Northstar · 役割：分析担当者')}${field('表示名','')}${field('メールアドレス','invitee@example.test','email')}${field('パスワード','','password')}${link('招待を受けて参加','SCR-AUTH-06','primary full')}`],
    'SCR-AUTH-06':['初期セットアップ','作業を始める前に、表示と通知を整えます。',`${field('表示名','Akira')}${select('タイムゾーン',['Asia/Tokyo','UTC'])}${select('言語',['日本語','English'])}${check('解析完了の通知を受け取る',true)}${link('ワークスペースを開く','SCR-DASH-01','primary full')}`]
  }[id];
  return `<div class="auth-shell"><div class="auth-form-panel"><div class="brand">${brandLogo()}</div><div class="auth-content"><div class="screen-id">${id} / WIREFRAME</div><h1 style="margin-top:12px">${screenMap[id]?.[1] || content[0]}</h1><p>${screenPurpose[id] || content[1]}</p>${useCaseLine(id)}<div class="form-stack" style="margin-top:25px">${content[2]}</div></div><div class="auth-footer">設計レビュー用 · 認証情報は送信されません。</div></div><div class="auth-art"><div class="eyebrow">ANALYZE / DECIDE / IMPROVE</div><div><h2>勝敗の先にある、<br>判断を残す。</h2><p>同じ場面を複数視点で確かめ、次に試すことへつなげる。</p></div><span class="mono tiny">THUMASTER 2.0 · APEX LEGENDS</span></div></div>`;
}

function panelContent(id){switch(id){
  case 'SCR-SEARCH-01': return `${field('キーワード','ピーク連携')}${list([['01','Game 06 · 北側の高台','シーン · 12:34','screen:SCR-REVIEW-01'],['02','Pro Scrim Week 3','セッション · 6試合','screen:SCR-SESSION-01'],['03','ピーク時間差の推移','指標 · Team Trends','screen:SCR-TREND-01']])}`;
  case 'SCR-NOTIFY-01': return `${list([['!','Kai視点の再選択が必要','Game 03 · 解析失敗','screen:SCR-INGEST-01',badge('失敗','danger')],['✓','Game 06の解析が完了','シーンを確認できます','screen:SCR-REVIEW-01',badge('完了','ok')],['○','次回アクションの確認','担当：全員','screen:SCR-REPORT-02',badge('未読','info')]])}`;
  case 'SCR-INGEST-02': return `<div class="placeholder" style="min-height:145px"><div><strong>動画をドロップ、または選択</strong><br><span class="small">このワイヤーフレームではファイルを送信しません</span></div></div><div class="field-row">${select('セッション',['Pro Scrim Week 3'])}${select('試合',['Game 06','Game 05'])}</div><div class="field-row">${select('映像種別',['選手視点','観戦視点'])}${select('視点担当',['Ren','Sora','Mio','Coach'])}</div>${notice('送信と解析は別工程','形式・容量・長さの正式上限は未決定です。','warn')}${btn('登録して送信','toast:ワイヤーフレームでは送信しません','primary full')}`;
  case 'SCR-INGEST-03': return state.selectedRecording==='Sora' ? `${notice('Game 06 · Sora視点','解析は完了しましたがHUDの一部を読めません。HUD由来の指標は欠損として扱います。','warn')}${table(['工程','状態','時刻'],[['受付',badge('完了','ok'),'9/11 21:31'],['送信',badge('完了','ok'),'9/11 21:32'],['解析',badge('一部利用可','warn'),'9/11 21:43']])}<p class="small">録画ID: VID-DEMO-002 · 処理ID: RUN-DEMO-011</p>${btn('Sora視点の再解析を検討（デモ）','toast:ワイヤーフレームでは再解析しません','primary')}` : `${notice('Game 03 · Kai視点','ファイルの再選択が必要です。影響：この視点の音声・HUD由来指標を算出できません。','warn')}${table(['工程','状態','時刻'],[['受付',badge('完了','ok'),'9/11 21:31'],['送信',badge('失敗','danger'),'9/11 21:32'],['解析',badge('未開始'),'—']])}<p class="small">録画ID: VID-DEMO-003 · 処理ID: RUN-DEMO-012</p>${btn('Kai視点の再送を検討（デモ）','toast:ワイヤーフレームでは再送しません','primary')}`;
  case 'SCR-REVIEW-02': return `${field('クリップ名','ピーク連携の確認') }<div class="field-row">${field('開始','12:34')}${field('終了','13:09')}</div>${check('Sora視点を含める',true)}${check('Ren視点を含める',true)}${check('Mio視点を含める',true)}${check('観戦視点を含める',false)}${select('共有範囲',['分析担当者・コーチ','選手に共有可能'])}${notice('元映像への追跡','試合・視点・時刻・解析方式の版を保持します。')}${btn('裏付けを保存','toast:裏付けを保存しました','primary full')}`;
  case 'SCR-OPP-02': {const detail=opponentDetails[state.selectedOpponent] || opponentDetails['Aster Union'];return `${badge('観測事実','ok')}<h3>${safe(state.selectedOpponent)} · ${safe(detail.place)}</h3><p>${safe(detail.observation)}</p>${badge('仮説','info')}<p>この移動が自チームの北側ルートにどう影響するかは、他の試合と照合して判断します。</p>${notice('出典',`${safe(detail.source)}。移動ルートは映像からの推定です。`)}${btn('観測を記録（デモ）','toast:ワイヤーフレームでは保存しません','primary')}`;}
  case 'SCR-OPP-03': return `${notice('比較条件','Storm Point · Week 3 · 公開資料のみ')}${table(['チーム','ルート','対象','出典'],[['Aster Union','内入り / 北側','3試合','公開配信'],['Cobalt Nine','外入り / 橋','4試合','公開配信'],['Ember Collective','外入り / 南西','5試合','公開配信']])}${notice('比較時の注意','観測数や試合条件が異なります。傾向の断定は避けます。','warn')}`;
  case 'SCR-SHARE-02': return `${notice('共有範囲','同じチームの認証済みメンバーだけが閲覧できます。')}${draftSelect('audience','共有対象',['チーム全員','Ren','Sora','Mio'])}${select('共有する版',['下書きから新しい版を作成','既存の共有版'])}${field('有効期限','2026-10-01','date')}${check('クリップのダウンロードを許可する',false)}${notice('選手向け表示を確認','本文とクリップに内部メモ・編成理由が含まれていないか確認してください。','warn')}${link('選手に見える内容をプレビュー','SCR-SHARE-01','full')}${btn('共有を確定（デモ）','toast:ワイヤーフレームでは共有されません','primary full')}`;
  default: return '';
}}

const renderers = {
  'SCR-DASH-01':renderToday,'SCR-SESSION-01':renderSessions,'SCR-SESSION-02':renderSessionEdit,
  'SCR-INGEST-01':renderIngest,'SCR-REVIEW-01':renderReview,'SCR-MAP-01':renderMap,
  'SCR-TREND-01':renderTrends,'SCR-OPP-01':renderOpponents,'SCR-ROSTER-01':renderRoster,
  'SCR-REPORT-01':renderReports,'SCR-REPORT-02':renderReportEdit,
  'SCR-SHARE-01':renderShared,'SCR-TEAM-01':renderTeam,'SCR-MEMBER-01':renderMembers,
  'SCR-ACCOUNT-01':renderAccount,'SCR-USAGE-01':renderUsage
};
function sidebar(){
  const group=(title,items)=>`<div><div class="nav-heading">${title}</div><nav class="nav-group" aria-label="${title}">${items.map(([id,name,,icon])=>`<button class="nav-link ${state.screen===id?'active':''}" data-action="screen:${id}" ${state.screen===id?'aria-current="page"':''}><span class="nav-icon">${icon}</span><span>${name}</span>${id==='SCR-REVIEW-01'?'<span class="nav-count">06</span>':''}</button>`).join('')}</nav></div>`;
  return `<aside class="sidebar" ${state.mobileNav?'style="display:flex;position:fixed;z-index:25;width:260px"':''}><a class="brand" href="#SCR-DASH-01">${brandLogo()}</a><div class="workspace-chip"><strong>◈ NORTHSTAR</strong><span>Apex Legends · Coach</span></div>${group('WORKSPACE',screens.filter(x=>x[2]==='workspace' && !['SCR-SESSION-02','SCR-REPORT-02'].includes(x[0])))}${group('SETTINGS',screens.filter(x=>x[2]==='admin'))}<div class="sidebar-footer"><strong>AK　Akira</strong>Team analyst · 架空のサンプル</div></aside>`;
}
function topbar(){return `<header class="topbar"><button class="btn sm mobile-menu" data-action="mobile-nav" aria-label="メニューを開く">☰</button><select class="select" aria-label="チームを選択"><option>◈ Northstar</option><option>別チーム（例）</option></select><span class="pill hide-sm">Pro Scrim Week 3</span><span class="spacer"></span>${open('⌕ 検索','SCR-SEARCH-01','sm hide-sm')}${open('♧ 通知','SCR-NOTIFY-01','sm')}${open('⇧ 動画を追加','SCR-INGEST-02','sm primary')}</header>`}
function drawer(){if(!state.panel)return '';const name=panels.find(x=>x[0]===state.panel)?.[1]||'';return `<div class="overlay" data-action="close-panel"><aside class="drawer" role="dialog" aria-modal="true" aria-label="${name}"><div class="drawer-head"><div><div class="screen-id">${state.panel} / AUXILIARY</div><h2 style="margin:6px 0 0">${name}</h2></div><button class="close" data-action="close-panel" aria-label="閉じる">×</button></div><div class="drawer-body"><p class="drawer-purpose">${screenPurpose[state.panel] || ''}</p>${useCaseLine(state.panel)}${panelContent(state.panel)}</div></aside></div>`}
function demoStrip(){return `<div class="demo-strip"><label for="screen-picker">SCREEN</label><select id="screen-picker" aria-label="画面を選ぶ">${screens.map(([id,name])=>`<option value="${id}" ${state.screen===id?'selected':''}>${id} · ${name}</option>`).join('')}</select><label for="scenario-picker">STATE</label><select id="scenario-picker" aria-label="表示状態を選ぶ"><option value="normal" ${state.scenario==='normal'?'selected':''}>通常</option><option value="empty" ${state.scenario==='empty'?'selected':''}>空</option><option value="partial" ${state.scenario==='partial'?'selected':''}>一部失敗</option><option value="error" ${state.scenario==='error'?'selected':''}>エラー</option></select><button class="btn sm" data-action="theme" aria-label="テーマを切り替え">${state.theme==='light'?'◐':'☼'}</button></div>`}
function render(){
  document.documentElement.dataset.theme=state.theme;
  document.documentElement.lang=state.locale;
  const category=screenMap[state.screen]?.[2];
  const body=category==='auth'?renderAuth(state.screen):category==='error'?renderError(state.screen):(renderers[state.screen]||renderToday)();
  const chrome=category==='workspace'||category==='admin'?`<div class="app-shell">${sidebar()}<main class="workspace">${topbar()}<div class="content">${body}</div></main></div>`:`<div class="language-floating">${languageControl()}</div>${body}`;
  const markup=chrome+demoStrip()+drawer()+(state.toast?`<div class="toast" role="status">${safe(state.toast)}</div>`:'');
  document.getElementById('app').innerHTML=localizeMarkup(markup,state.locale,uiTranslations);
  document.title=`${state.locale==='en'?englishScreens[state.screen]?.[0]:screenMap[state.screen]?.[1]||'Thumaster'} · Thumaster 2.0 Wireframe`;
}
function changeLanguage(locale){
  if(!['ja','en'].includes(locale))return;
  const fields=[...document.querySelectorAll('#app input, #app textarea, #app select:not([data-language])')].map(node=>({value:node.value,checked:node.checked,selectedIndex:node.selectedIndex}));
  state.locale=locale;
  try{localStorage.setItem('thumaster-wireframe-language',locale)}catch{}
  render();
  [...document.querySelectorAll('#app input, #app textarea, #app select:not([data-language])')].forEach((node,index)=>{const saved=fields[index];if(!saved)return;if(node.tagName==='SELECT')node.selectedIndex=saved.selectedIndex;else if(node.type==='checkbox')node.checked=saved.checked;else node.value=saved.value});
}
function navigate(id){if(!screenMap[id])return;state.sharePreview=id==='SCR-SHARE-01'&&state.panel==='SCR-SHARE-02';state.screen=id;state.panel=null;state.toast='';state.mobileNav=false;location.hash=id;window.scrollTo(0,0);render()}
document.addEventListener('click',event=>{const node=event.target.closest('[data-action]');if(!node)return;const action=node.dataset.action;if(action==='close-panel'&&event.target.closest('.drawer')&&!event.target.closest('.close'))return;if(action.startsWith('screen:'))navigate(action.slice(7));else if(action.startsWith('panel:')){state.panel=action.slice(6);render()}else if(action==='close-panel'){state.panel=null;render()}else if(action==='theme'){state.theme=state.theme==='light'?'dark':'light';render()}else if(action==='mobile-nav'){state.mobileNav=!state.mobileNav;render()}else if(action.startsWith('review:')){state.reviewDecision=action.slice(7)==='adopt'?'事実として採用':'候補を却下';render()}else if(action==='session:new'){state.selectedSessionNew=true;state.selectedGame='new';navigate('SCR-SESSION-02')}else if(action.startsWith('game-screen:')){state.selectedSessionNew=false;state.selectedGame=action.slice(12);navigate('SCR-SESSION-02')}else if(action.startsWith('game:')){state.selectedGame=action.slice(5);render()}else if(action.startsWith('map:')){state.selectedMapPoint=action.slice(4);render()}else if(action.startsWith('recording:')){state.selectedRecording=action.slice(10);state.panel='SCR-INGEST-03';render()}else if(action.startsWith('opponent:')){state.selectedOpponent=action.slice(9);state.panel='SCR-OPP-02';render()}else if(action.startsWith('roster:')){state.rosterChoice=action.slice(7);render()}else if(action.startsWith('toast:')){state.toast=action.slice(6);render();setTimeout(()=>{state.toast='';render()},2800)}});
function updateDraft(event){const key=event.target.dataset.draft;if(!key||!Object.hasOwn(state.reportDraft,key))return;state.reportDraft[key]=event.target.value;document.querySelectorAll(`[data-preview="${key}"]`).forEach(node=>{node.textContent=event.target.value})}
document.addEventListener('input',updateDraft);
document.addEventListener('change',event=>{updateDraft(event);if(event.target.matches('[data-language]'))changeLanguage(event.target.value);if(event.target.id==='screen-picker')navigate(event.target.value);if(event.target.id==='scenario-picker'){state.scenario=event.target.value;render()}});
window.addEventListener('hashchange',()=>{const id=decodeURIComponent(location.hash.slice(1));if(screenMap[id]&&id!==state.screen){state.screen=id;state.panel=null;render()}});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&state.panel){state.panel=null;render()}if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'){event.preventDefault();state.panel='SCR-SEARCH-01';render()}});
const initial=decodeURIComponent(location.hash.slice(1));if(screenMap[initial])state.screen=initial;render();
