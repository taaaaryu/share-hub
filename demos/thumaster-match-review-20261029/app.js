/* PR #35 shell and components, with existing local analysis instead of fictional records. */
(() => {
  'use strict';
  const source = window.THUMASTER_LOCAL_DATA;
  if (!source?.detail?.analysis_events || !source?.route?.anchors || !source?.review) {
    document.getElementById('app').innerHTML = '<main style="padding:32px"><h1>解析データを読み込めません</h1><p>同梱データとREADMEの開き方を確認してください。</p></main>';
    return;
  }
  const { detail, review } = source;
  const route = { ...source.route, anchors: source.route.anchors.filter(anchor => anchor.t < 47.4) };
  const videoUrl = './match.mp4';
  const mapUrl = './map.png';
  const storageKey = 'thumaster-macro-micro-review-48s-v1';
  const events = detail.analysis_events.map((event, index) => ({ ...event, index, t: event.frame_number / detail.fps }));
  const ammoConsumed = events.reduce((sum, event) => sum + Math.max(0, event.ammo_before - event.ammo_after), 0);
  const scenes = [];
  events.forEach(event => {
    let scene = scenes.at(-1);
    if (!scene || event.t - scene.end > 2) { scene = { start: event.t, end: event.t, events: [] }; scenes.push(scene); }
    scene.events.push(event); scene.end = event.t;
  });
  const readSaved = () => { try { return JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch { return {}; } };
  const saved = readSaved();
  const ui = { time: events[0].t, eventIndex: 0, decisions: saved.decisions || {}, draft: saved.draft || {
    title: '48秒クリップの戦闘と移動を振り返る',
    fact: `弾薬減少イベント${events.length}件、観測された弾数差分の合計${ammoConsumed}発。HUD確認値は0秒422、47.4秒734（差分+312）。47.4〜47.7秒の間に映像カットがあり、カット後は658。全動画のダメージ合計は未確定。`,
    interpretation: '', action: '',
  }, anchorIndex: 0, showRoute: true, showAnchors: true, saveStatus: '', playing: false };
  const persist = () => { try { localStorage.setItem(storageKey, JSON.stringify({ decisions: ui.decisions, draft: ui.draft })); ui.saveStatus = 'このブラウザーに保存済み'; } catch { ui.saveStatus = '保存できませんでした。ブラウザーの保存設定を確認してください。'; } };
  const fmt = time => `${Math.floor(time / 60).toString().padStart(2, '0')}:${(time % 60).toFixed(1).padStart(4, '0')}`;
  const value = number => Number.isFinite(number) && number >= 0 ? String(number) : '未取得';
  const localButton = (label, action, extra = '', style = '') => `<button class="btn ${style}" data-local-action="${action}" ${extra}>${safe(label)}</button>`;
  const footer = () => '<div class="local-footer">実動画の既存解析 · 48秒 / 1視点 · 地図の正解精度とHUD読取精度は未検証 · 47.4秒以降の位置は不明</div>';
  const condition = () => '<div class="context-bar"><span class="eyebrow">分析条件</span><span>実戦クリップ 01</span><span class="context-sep">/</span><span>World’s Edge（照合結果）</span><span class="context-sep">/</span><span>0:00–0:48.0</span><span class="context-sep">/</span><span>記録視点 1名</span></div>';
  const localPage = (id, lead, body, actions = '') => `<div class="flow-head"><div><div class="flow-kicker">${id} / SAMPLE ANALYSIS</div><h1>${safe(screenMap[id]?.[1] || id)}</h1><p class="flow-lead">${lead}</p></div><div class="flow-head-actions">${actions}</div></div>${condition()}${body}${footer()}`;
  const kpi = (label, number, note) => `<div class="local-kpi"><span>${safe(label)}</span><strong>${safe(number)}</strong><small>${safe(note)}</small></div>`;
  const summary = () => `<div class="local-kpis">${kpi('弾薬減少イベント', events.length, '1件が複数発の減少を含む場合あり')}${kpi('観測された弾薬消費', `${ammoConsumed}発`, '弾数差分の合計 / 命中数は未取得')}${kpi('カット前のHUD差分', '+312', '確認点 0秒422 → 47.4秒734')}${kpi('地図照合区間', `${route.anchors.length} / ${route.summary.bucket_count}`, '2.5秒区間 / 正解精度は未検証')}</div>`;
  const evidenceLinks = () => '<p class="local-caption">既存解析の抜粋。時刻はフレーム÷fpsで算出。元映像との厳密な時刻差は未検証です。</p>';
  const transport = () => `<div class="local-transport">${localButton('▶', 'play', 'aria-label="再生または一時停止"')}<output id="local-clock">${fmt(ui.time)}</output><input id="local-seek" aria-label="共通時刻" type="range" min="0" max="${detail.duration_sec}" step="0.05" value="${ui.time}"><output>${fmt(detail.duration_sec)}</output></div>`;
  const video = () => `<video class="local-video" id="local-video" src="${videoUrl}" controls preload="metadata" playsinline aria-label="解析した48秒の元動画"></video>${transport()}`;
  const eventAt = time => events.findLast(event => event.t <= time + 0.001) || null;
  const decision = index => ui.decisions[index]?.status || '未確認';
  const damageText = event => event.rejected_damage_reading != null ? '読取棄却' : event.damage_counter_reset ? '減少を検出・要確認' : value(event.damage);
  const timeline = () => `<div class="local-timeline" aria-label="イベントタイムライン">${scenes.map((scene, index) => `<button class="scene-range" title="区間${index + 1} ${fmt(scene.start)}–${fmt(scene.end)} / ${scene.events.length}件" aria-label="区間${index + 1}の先頭 ${fmt(scene.start)}" data-scene-index="${index}" data-time="${scene.start}" style="left:${scene.start / detail.duration_sec * 100}%;width:${Math.max(0.6, (scene.end - scene.start) / detail.duration_sec * 100)}%"></button>`).join('')}${review.damage_checkpoints.map(point => `<button class="checkpoint" title="${fmt(point.time_sec)} HUD確認値 ${point.damage}" aria-label="${fmt(point.time_sec)} HUD確認値 ${point.damage}" data-time="${point.time_sec}" style="left:${point.time_sec / detail.duration_sec * 100}%"></button>`).join('')}</div>`;
  const eventList = () => `<div class="local-events" id="local-event-list">${events.map(event => `<button class="local-event${ui.eventIndex === event.index ? ' selected' : ''}" data-event="${event.index}"><time>${fmt(event.t)}</time><span>弾数 ${event.ammo_before} → ${event.ammo_after}<br><small>HP ${event.hp} / Shield ${event.shield} · ${safe(decision(event.index))}</small></span><small>累積HUD ${safe(damageText(event))}</small></button>`).join('')}</div>`;
  const stateValues = () => `<div class="local-state"><div><span>体力</span><strong id="hud-hp">—</strong></div><div><span>シールド</span><strong id="hud-shield">—</strong></div><div><span>弾数</span><strong id="hud-ammo">—</strong></div><div><span>累積HUD</span><strong id="hud-damage">—</strong></div></div><p class="local-caption" id="hud-observed">解析イベントを選んで確認します。</p>`;
  function chart() {
    const series = [['hp', 100, '#d46e80', '体力 0–100'], ['shield', 100, '#338eaa', 'シールド 0–100'], ['ammo', 30, '#bf8444', '弾数 0–30']];
    return `<svg viewBox="0 0 760 180" class="local-chart" role="img" aria-label="イベントで観測した体力、シールド、弾数の推移">${[25, 80, 140].map(y => `<line x1="20" y1="${y}" x2="740" y2="${y}" stroke="var(--line)"/>`).join('')}${series.map(([key, max, color]) => events.filter(event => Number.isFinite(event[key])).map(event => `<circle cx="${20 + event.t / detail.duration_sec * 720}" cy="${140 - event[key] / max * 115}" r="2" fill="${color}"/>`).join('')).join('')}<line id="local-chart-cursor" x1="20" x2="20" y1="15" y2="148" stroke="var(--ink)"/><text x="20" y="171" fill="var(--muted)" font-size="10">0:00</text><text x="700" y="171" fill="var(--muted)" font-size="10">0:48</text></svg><div class="local-legend">${series.map(([, , color, label]) => `<span><i style="background:${color}"></i>${label}</span>`).join('')}</div><p class="local-caption">HUDテンプレートによるイベント時の読取値。点の間は補間せず、非発砲時の回復や被弾を網羅した結果ではありません。</p>`;
  }
  function reviewPage() {
    const event = events[ui.eventIndex];
    const record = ui.decisions[event.index] || {};
    return localPage('SCR-REVIEW-01', '弾薬変化の候補を元映像と照合し、事実・解釈・次回行動を記録します。', `
      <section id="micro"><div class="case-banner"><div><div class="flow-kicker">QUESTION / 48秒の実動画</div><h2>弾数・防御値の変化は、<br>映像のどの場面に対応するか？</h2><div class="case-meta"><span>${events.length}候補</span><span>1視点</span><span>47.4〜47.7秒に映像カット</span></div></div>${badge('人の確認待ち', 'warn')}</div>
      <div class="local-layout"><div class="stack">${card('同じ時刻の元映像を確認', `<div id="evidence-video">${video()}</div>${timeline()}${stateValues()}`)}${card('イベント時の状態変化', chart())}${card('解析した場面を選ぶ', `<div class="local-scene-row">${scenes.map((scene, index) => localButton(`区間${index + 1} ${fmt(scene.start)}–${fmt(scene.end)}`, 'seek', `data-time="${scene.start}"`, 'sm')).join('')}</div><p class="local-caption">弾薬変化の間隔が2秒を超えた箇所で分けた候補区間です。交戦の確定判定ではありません。</p>${eventList()}`)}</div>
      <div class="stack">${card('事実候補を判定する', `<p class="eyebrow">候補 ${event.index + 1} / ${events.length} · ${fmt(event.t)}</p><h3>弾数 ${event.ammo_before} → ${event.ammo_after}</h3><p>フレーム ${event.frame_number} / ${detail.fps}fps。HP ${event.hp}・シールド ${event.shield}。${event.rejected_damage_reading != null ? `ダメージ読取 ${event.rejected_damage_reading} は棄却。` : `累積HUDは ${safe(damageText(event))}。`}</p>${badge(decision(event.index), record.status === '採用' || record.status === '修正して採用' ? 'ok' : 'warn')}<label class="field"><span>映像で確認した本文</span><textarea class="textarea" id="local-review-body">${safe(record.body || `弾数が${event.ammo_before}から${event.ammo_after}に減少した。`)}</textarea></label><div class="field-row">${localButton('採用', 'decision', 'data-status="採用"', 'primary')}${localButton('修正して採用', 'decision', 'data-status="修正して採用"')}${localButton('却下', 'decision', 'data-status="却下"')}${localButton('保留', 'decision', 'data-status="保留"')}</div><p class="local-caption">判定はこのブラウザーに保存します。</p>`)}
      ${card('根拠の充足', table(['対象', '取得した値'], [['録画', '選手視点 1本'], ['武器', 'フラットライン（読取結果）'], ['体力 / シールド', 'イベント時に読取 / 精度未検証'], ['ダメージOCR', '46件棄却 / 3回の減少を検出'], ['命中数・部位', '未取得'], ['別選手・音声・コール', '未解析']]) + evidenceLinks())}
      ${card('地図と解釈を確認', `${notice('位置は推定', 'カット前の照合点17件。点間は直線補間で実際の経路ではありません。', 'info')}<div class="field-row"><a class="btn sm" href="#macro">この時刻を地図で確認</a></div>`)}
      </div></div></section>${macroSection()}`, '<a class="btn" href="#macro">地図へ移動</a>');
  }
  const connectable = (a, b) => a.map_id === b.map_id && a.segment_id === b.segment_id && b.bucket - a.bucket <= 2 && b.t - a.t <= route.interval_sec * 3;
  function locate(time) {
    if (time >= 47.4) return null;
    const index = route.anchors.findIndex(anchor => anchor.t >= time);
    if (index < 0) return null;
    const b = route.anchors[index];
    if (Math.abs(b.t - time) < 0.025) return { ...b, status: '照合点' };
    if (index === 0) return null;
    const a = route.anchors[index - 1];
    if (!connectable(a, b)) return null;
    const ratio = (time - a.t) / (b.t - a.t);
    return { map_x: a.map_x + (b.map_x - a.map_x) * ratio, map_y: a.map_y + (b.map_y - a.map_y) * ratio, status: '直線補間' };
  }
  function routePath() {
    return route.anchors.map((a, i) => `${i && connectable(route.anchors[i - 1], a) ? 'L' : 'M'}${a.map_x},${a.map_y}`).join(' ');
  }
  function mapSvg(zoom = false) {
    const anchors = route.anchors;
    const xs = anchors.map(a => a.map_x), ys = anchors.map(a => a.map_y);
    const side = Math.max(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys), 60) + 48;
    const bounds = `${(Math.min(...xs) + Math.max(...xs) - side) / 2} ${(Math.min(...ys) + Math.max(...ys) - side) / 2} ${side} ${side}`;
    return `<svg class="${zoom ? '' : 'local-map'}" data-map-view="${zoom ? 'zoom' : 'full'}" viewBox="${zoom ? bounds : '0 0 2048 2048'}" role="img" aria-label="${zoom ? '移動範囲の拡大' : 'World’s Edge上の推定経路'}"><image href="${mapUrl}" x="0" y="0" width="2048" height="2048"/>${ui.showRoute ? `<path d="${routePath()}" stroke="#65d8e7" stroke-width="${zoom ? 2 : 8}" fill="none" stroke-linejoin="round"/>` : ''}${ui.showAnchors ? anchors.map((a, index) => `<circle data-anchor="${index}" tabindex="0" role="button" aria-label="${fmt(a.t)}の照合点" cx="${a.map_x}" cy="${a.map_y}" r="${zoom ? 2.5 : 13}" fill="#a3e6ad" stroke="#143e37" stroke-width="${zoom ? 0.6 : 4}"><title>${fmt(a.t)}の照合点</title></circle>`).join('') : ''}<circle data-current-position r="${zoom ? 4 : 24}" fill="#ffad70" stroke="#fff" stroke-width="${zoom ? 1 : 5}" visibility="hidden"/></svg>`;
  }
  function macroSection() {
    const anchor = route.anchors[ui.anchorIndex];
    return `<section id="macro"><div class="flow-head"><div><div class="flow-kicker">MACRO / MAP</div><h2>マクロ｜地図と移動</h2><p class="flow-lead">地図の照合点と上の動画を同じ時刻で確認します。</p></div></div><div class="local-map-layout"><div class="stack">${card('World’s Edge / 記録視点の動き', `<div class="field-row">${localButton(ui.showRoute ? '経路を隠す' : '経路を表示', 'toggle-route', '', 'sm')}${localButton(ui.showAnchors ? '照合点を隠す' : '照合点を表示', 'toggle-anchors', '', 'sm')}</div><div class="local-map-wrap">${mapSvg()}<div class="local-map-zoom"><strong>移動範囲を拡大 / 照合点を選択</strong>${mapSvg(true)}</div></div><p class="local-caption">緑:照合点 / 水色:点間を結ぶ推定線 / 橙:現在位置。地点を押すと動画も移動します。点が重なる場合は「照合点を選ぶ」の時刻一覧を使えます。</p>${table(['照合区間', '欠測', '位置の単位', 'リング・敵位置'], [[`${route.anchors.length} / ${route.summary.bucket_count}`, `${route.summary.bucket_count - route.anchors.length}区間（欠測・カット除外）`, '参照マップ画像上のpx', '未取得']])}`)}</div><div class="stack">${card('選択時刻の根拠映像', '<p>このページ上部の動画と時刻を共有しています。</p><a class="btn sm" href="#evidence-video">動画へ戻る</a>')}${card('地点と事実を確認', `<p id="local-position-status">推定位置を確認中</p><div class="local-state"><div><span>X</span><strong id="map-x">—</strong></div><div><span>Y</span><strong id="map-y">—</strong></div></div><p>選択照合点 ${fmt(anchor.t)} / 区間 ${anchor.bucket + 1}</p><p class="annotation">点の取得率は位置の正解率とは異なります。映像カットは47.4〜47.7秒の間。47.4秒以降の位置は不明として扱い、最後の照合点より後も位置を表示しません。</p><a class="btn primary" href="#micro">この時刻のHUDを確認</a>${evidenceLinks()}`)}${card('照合点を選ぶ', `<div class="local-events">${route.anchors.map((a, index) => localButton(`${fmt(a.t)} · (${a.map_x.toFixed(1)}, ${a.map_y.toFixed(1)})`, 'anchor', `data-anchor="${index}"`, 'sm')).join(' ')}</div>`)}</div></div></section>`;
  }
  const supported = ['SCR-REVIEW-01'];
  Object.assign(renderers, { 'SCR-REVIEW-01': reviewPage });
  sidebar = () => `<aside class="sidebar" ${state.mobileNav ? 'style="display:flex;position:fixed;z-index:25;width:260px"' : ''}><a class="brand" href="#micro"><img class="brand-logo" src="vendor/thumaster-logo-exact.svg" alt="Thumaster"></a><div class="workspace-chip"><strong>MATCH REVIEW</strong><span>Apex Legends · 解析した録画</span></div><nav class="nav-group" aria-label="ページ内移動"><a class="nav-link active" href="#micro">ミクロ｜戦闘とHUD</a><a class="nav-link" href="#macro">マクロ｜地図と移動</a></nav><div class="sidebar-footer">試作 / 実データ差込版<br>1録画・1視点</div></aside>`;
  topbar = () => `<header class="topbar"><button class="btn sm mobile-menu" data-action="mobile-nav" aria-label="メニューを開く">☰</button><span class="team-context"><small>対象</small><strong>実戦クリップ01</strong></span><span class="pill hide-sm">World’s Edge</span><span class="spacer"></span><span class="local-current-time" id="header-time">${fmt(ui.time)}</span>${btn('テーマ切替', 'theme', 'sm')}</header>`;
  demoStrip = () => '';
  const baseNavigate = navigate;
  navigate = function localNavigate(id) {
    if (id === 'SCR-REVIEW-01') ui.eventIndex = eventAt(ui.time)?.index ?? 0;
    if (id === 'SCR-MAP-01') ui.anchorIndex = route.anchors.reduce((best, anchor, index) => Math.abs(anchor.t - ui.time) < Math.abs(route.anchors[best].t - ui.time) ? index : best, 0);
    baseNavigate(id);
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  };
  const baseRender = render;
  render = function localRender() {
    if (!supported.includes(state.screen)) state.screen = 'SCR-REVIEW-01';
    state.locale = 'ja'; state.panel = null;
    baseRender();
    const player = document.getElementById('local-video');
    if (player) {
      const resumeAt = ui.time, resumePlayback = ui.playing;
      const isCurrent = () => document.getElementById('local-video') === player;
      player.addEventListener('loadedmetadata', () => { if (!isCurrent()) return; player.currentTime = Math.min(resumeAt, player.duration - 0.02); updateTime(resumeAt); if (resumePlayback) player.play().catch(() => {}); });
      // Removed videos may still emit queued timeupdate/pause events after navigation.
      player.addEventListener('timeupdate', () => { if (isCurrent()) updateTime(player.currentTime); });
      player.addEventListener('play', () => { if (!isCurrent()) return; ui.playing = true; const b = document.querySelector('[data-local-action="play"]'); if (b) b.textContent = 'Ⅱ'; });
      player.addEventListener('pause', () => { if (!isCurrent()) return; ui.playing = false; const b = document.querySelector('[data-local-action="play"]'); if (b) b.textContent = '▶'; });
    }
    updateTime(ui.time);
    const log = document.getElementById('local-event-list');
    const active = log?.querySelector('.local-event.selected');
    if (active) log.scrollTop += active.getBoundingClientRect().top - log.getBoundingClientRect().top - log.clientHeight / 2;
  };
  const setText = (id, text) => { const node = document.getElementById(id); if (node) node.textContent = text; };
  function updateTime(time) {
    ui.time = Math.max(0, Math.min(time, detail.duration_sec));
    setText('header-time', fmt(ui.time)); setText('local-clock', fmt(ui.time));
    const slider = document.getElementById('local-seek'); if (slider) slider.value = ui.time;
    const event = eventAt(ui.time);
    setText('hud-hp', event ? value(event.hp) : '—'); setText('hud-shield', event ? value(event.shield) : '—');
    setText('hud-ammo', event ? value(event.ammo) : '—'); setText('hud-damage', event ? damageText(event) : '—');
    setText('hud-observed', event ? `直近の観測 ${fmt(event.t)} / フレーム${event.frame_number}（現在との差 ${(ui.time - event.t).toFixed(1)}秒）` : 'この時刻以前に解析イベントはありません。');
    const cursor = document.getElementById('local-chart-cursor'); if (cursor) { const x = 20 + ui.time / detail.duration_sec * 720; cursor.setAttribute('x1', x); cursor.setAttribute('x2', x); }
    const point = locate(ui.time);
    setText('local-position-status', point ? `位置: ${point.status} / ${fmt(ui.time)}` : `位置の観測なし / ${fmt(ui.time)}`);
    setText('map-x', point ? point.map_x.toFixed(1) : '—'); setText('map-y', point ? point.map_y.toFixed(1) : '—');
    document.querySelectorAll('[data-current-position]').forEach(node => { node.setAttribute('visibility', point ? 'visible' : 'hidden'); if (point) { node.setAttribute('cx', point.map_x); node.setAttribute('cy', point.map_y); } });
    document.querySelectorAll('.local-timeline [data-scene-index]').forEach(node => { const scene = scenes[Number(node.dataset.sceneIndex)]; node.classList.toggle('selected', ui.time >= scene.start && ui.time <= scene.end); });
  }
  function seek(time) {
    updateTime(Number(time));
    const player = document.getElementById('local-video'); if (player?.readyState) player.currentTime = ui.time;
  }
  function chooseEvent(index) { ui.eventIndex = index; ui.time = events[index].t; render(); }
  document.addEventListener('click', event => {
    const node = event.target.closest('[data-local-action], [data-event], [data-anchor], [data-time]');
    if (!node) return;
    const action = node.dataset.localAction;
    if (action === 'play') { const player = document.getElementById('local-video'); if (player) player.paused ? player.play().catch(() => {}) : player.pause(); }
    else if (action === 'decision') {
      ui.decisions[ui.eventIndex] = { status: node.dataset.status, body: document.getElementById('local-review-body').value, updated_at: new Date().toISOString() };
      persist(); render();
    } else if (action === 'save-draft') { persist(); setText('local-save-status', ui.saveStatus); }
    else if (action === 'toggle-route') { ui.showRoute = !ui.showRoute; render(); }
    else if (action === 'toggle-anchors') { ui.showAnchors = !ui.showAnchors; render(); }
    else if (action === 'open-evidence') { ui.time = Number(node.dataset.time); const nearest = events.findLast(item => item.t <= ui.time); if (nearest) ui.eventIndex = nearest.index; navigate('SCR-REVIEW-01'); }
    else if (node.dataset.anchor != null) { ui.anchorIndex = Number(node.dataset.anchor); seek(route.anchors[ui.anchorIndex].t); render(); }
    else if (node.dataset.event != null) chooseEvent(Number(node.dataset.event));
    else if (node.dataset.sceneIndex != null) chooseEvent(scenes[Number(node.dataset.sceneIndex)].events[0].index);
    else if (node.dataset.time != null) seek(node.dataset.time);
  });
  document.addEventListener('input', event => {
    if (event.target.id === 'local-seek') seek(event.target.value);
    const key = event.target.dataset.localDraft;
    if (key && Object.hasOwn(ui.draft, key)) { ui.draft[key] = event.target.value; document.querySelectorAll(`[data-local-preview="${key}"]`).forEach(node => { node.textContent = ui.draft[key] || '未記入'; }); setText('local-save-status', '未保存の変更があります'); }
  });
  document.addEventListener('keydown', event => { const anchor = event.target.closest('[data-anchor]'); if (anchor && ['Enter', ' '].includes(event.key)) { event.preventDefault(); ui.anchorIndex = Number(anchor.dataset.anchor); seek(route.anchors[ui.anchorIndex].t); render(); } });
  window.THUMASTER_PR35 = { events, scenes, ui, locate, seek, chooseEvent, supported, ammoConsumed };
  const initialScreen = decodeURIComponent(location.hash.slice(1));
  state.screen = supported.includes(initialScreen) ? initialScreen : 'SCR-REVIEW-01';
  render();
})();
