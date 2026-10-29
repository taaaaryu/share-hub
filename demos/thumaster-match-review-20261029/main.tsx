import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AimAnalysisPanel } from './AimAnalysisPanel';
const data = (window as any).THUMASTER_LOCAL_DATA;
const anchors = data.route.anchors.filter((a:any) => a.t < 47.4);
const events = data.detail.analysis_events;
const canConnect = (a:any,b:any) => a.map_id === b.map_id && a.segment_id === b.segment_id && b.bucket-a.bucket <= 2 && b.t-a.t <= data.route.interval_sec*3;
const clock = (s:number) => `00:${s.toFixed(1).padStart(4,'0')}`;
function locate(t:number) {
 if (t >= 47.4) return null;
 const i=anchors.findIndex((a:any)=>a.t>=t);
 if(i<0) return null;
 const b=anchors[i]; if(Math.abs(b.t-t)<.025) return {...b, status:'照合点'};
 if(i===0 || !canConnect(anchors[i-1],b)) return null;
 const a=anchors[i-1], f=(t-a.t)/(b.t-a.t);
 return {map_x:a.map_x+f*(b.map_x-a.map_x),map_y:a.map_y+f*(b.map_y-a.map_y),status:'点間を直線補間'};
}
function App() {
 const [time,setTime]=useState(0);
 useEffect(()=>{const v=document.querySelector('video')!;const tick=()=>setTime(v.currentTime); v.addEventListener('timeupdate',tick);v.addEventListener('seeked',tick);return()=>{v.removeEventListener('timeupdate',tick);v.removeEventListener('seeked',tick)}},[]);
 const seek=(t:number)=>{const v=document.querySelector('video')!;v.currentTime=t;setTime(t)};
 const p=locate(time);
 const past=anchors.filter((a:any)=>a.t<=time+.001);
 const path=past.map((a:any,i:number)=>`${i&&canConnect(past[i-1],a)?'L':'M'}${a.map_x},${a.map_y}`).join(' ')+(p?.status==='点間を直線補間'&&past.length?` L${p.map_x},${p.map_y}`:'');
 const xs=anchors.map((a:any)=>a.map_x),ys=anchors.map((a:any)=>a.map_y);
 const side=Math.max(Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys),60)+48;
 const bounds=`${(Math.min(...xs)+Math.max(...xs)-side)/2} ${(Math.min(...ys)+Math.max(...ys)-side)/2} ${side} ${side}`;
 const map=(zoom:boolean)=><svg className="map" viewBox={zoom?bounds:'0 0 2048 2048'} role="img" aria-label={zoom?'移動範囲の拡大':'ワールズエッジ全体マップ'}><image href="map.png" width="2048" height="2048"/><path d={path} fill="none" stroke="#00f5ff" strokeWidth={zoom?2:8} strokeLinejoin="round"/>{anchors.map((a:any,i:number)=><circle key={i} cx={a.map_x} cy={a.map_y} r={zoom?2.2:11} fill={a.t<=time?'#b5fff3':'#687774'} opacity={a.t<=time?1:.5} onClick={()=>seek(a.t)} role="button" tabIndex={0} onKeyDown={e=>{if(e.key==='Enter'||e.key===' ')seek(a.t)}} aria-label={`${clock(a.t)}へ移動`}><title>{clock(a.t)}</title></circle>)}{p&&<circle data-current-position cx={p.map_x} cy={p.map_y} r={zoom?4:24} fill="#ffae63" stroke="white" strokeWidth={zoom?1:5} pointerEvents="none"/>}</svg>;
 return <main className="site"><header><img src="vendor/thumaster-logo-exact.svg" alt="Thumaster"/><span>実戦分析サンプル / 48秒</span></header><section className="intro"><p className="section-kicker">MATCH REVIEW / WORLDS EDGE</p><h1>プレイレポート</h1><p>同じ実戦映像を、戦闘と移動の両面から振り返ります。</p><nav><a href="#micro">ミクロ：戦闘</a><a href="#macro">マクロ：移動</a></nav></section><section id="micro"><div className="section-title"><p className="section-kicker">MICRO ANALYSIS</p><h2>戦闘を振り返る</h2><p>Thumasterデモの解析画面を使用。動画を再生・シークすると、下の地図も同じ時刻に動きます。</p></div><AimAnalysisPanel preview={{url:'match.mp4',content_type:'video/mp4',filename:'実戦クリップ'}} aim={null} damageTimeline={[]} durationSec={data.detail.duration_sec}/><div className="score-grid"><article className="score-card"><p className="section-kicker">AIM ACCURACY</p><h2>命中率</h2><strong>未取得</strong><p>命中を確認できるデータがありません。</p></article><article className="score-card"><p className="section-kicker">TOTAL DAMAGE</p><h2>総ダメージ</h2><strong>未確定</strong><p>映像カットで累積HUDが切り替わるため全編の合計は不明です。</p></article><article className="score-card"><p className="section-kicker">WEAPON</p><h2>武器の読取</h2><strong>フラットライン</strong><p>既存解析による読み取り。精度は未検証。</p></article></div><div className="facts"><b>この映像の観測</b><p>弾薬減少の候補 {events.length} 件。0秒の累積HUD 422 → 47.4秒の 734（差分 +312）。途中の読取に欠損があり、全編の与ダメージや命中回数を意味しません。</p><p>敵の検出結果は未取得のため、照準のずれやVPSは表示していません。</p></div></section><section id="macro"><div className="section-title"><p className="section-kicker">MACRO ANALYSIS</p><h2>地図で移動を振り返る</h2><p>上の動画と同じ時刻です。再生に合わせて現在位置と通過した照合点が動きます。</p></div><div className="macro-layout"><article className="map-card"><div className="map-head"><span>WORLD’S EDGE</span><strong>{clock(time)}</strong></div>{map(true)}<div className="legend"><span className="orange">● 現在位置</span><span className="cyan">━ 移動の推定線</span><span>● 照合点</span></div><input type="range" min="0" max={data.detail.duration_sec} step="0.05" value={time} onChange={e=>seek(Number(e.target.value))} aria-label="動画と地図の時刻"/><div className="time-line"><span>00:00.0</span><span>00:48.0</span></div><p id="position-status">{p?`現在位置：${p.status}`:'この時刻の位置は不明です'}</p></article><aside className="map-side"><div className="overview"><span>全体マップ</span>{map(false)}</div><p>緑の点は取得した照合点。水色の線と点の間の位置は直線補間で、実際の通過経路とは限りません。位置の正解精度は未検証です。</p><p>47.4〜47.7秒に映像カットがあるため、47.4秒以降は位置を表示しません。照合点は20区間中17区間です。</p><div className="anchor-list">{anchors.map((a:any,i:number)=><button key={i} onClick={()=>seek(a.t)} aria-label={`${clock(a.t)}の照合点へ移動`}>{clock(a.t)}</button>)}</div><a href="#micro">↑ 動画に戻る</a></aside></div></section><footer>THUMASTER / 実戦分析サンプル · 1動画 / 1視点</footer></main>
}
createRoot(document.getElementById('root')!).render(<App/>);
