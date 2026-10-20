const canvas=document.querySelector('#projection'),ctx=canvas.getContext('2d'),slider=document.querySelector('#mapping-time'),status=document.querySelector('#mapping-status');
try {
 const responses=await Promise.all(['interior.json','review-mapping.json'].map(p=>fetch(p+'?v=20261020-v3')));
 if(responses.some(r=>!r.ok))throw Error('data unavailable');
 const [model,data]=await Promise.all(responses.map(r=>r.json()));let player=null;
 slider.max=data.rows.length-1;
 const eligible=data.rows.filter(r=>r.independent_evaluation_eligible),accepted=eligible.filter(r=>r.camera_pose.position);
 document.querySelector('#mapping-summary').textContent=`別時刻の検証 ${eligible.length} フレームのうち、画像上の判定を通ったのは ${accepted.length} フレームです。連続した室内移動の復元には至っていません。位置のメートル誤差と、向きの角度誤差は正解座標がないため未測定です。`;
 function background(text){ctx.fillStyle='#17212b';ctx.fillRect(0,0,1280,720);ctx.fillStyle='#e8edf3';ctx.font='26px sans-serif';ctx.fillText(text,35,52);}
 function draw(index){
  const row=data.rows[index],pose=row.camera_pose,t=row.file_timestamp;slider.value=index;background(`${t.toFixed(3)} 秒`);
  document.querySelector('#source-time-link').href=`https://www.youtube.com/watch?v=wJGk8oiqysw&t=${t.toFixed(3)}s`;
  if(pose.position){
   const R=pose.world_to_camera_R,T=pose.world_to_camera_t,K=data.K;
   function cameraPoint(p){return R.map((r,i)=>r.reduce((s,v,j)=>s+v*p[j],T[i]));}
   function project(p){return [K[0][0]*p[0]/p[2]+K[0][2],K[1][1]*p[1]/p[2]+K[1][2]];}
   const faces=[];
   for(const part of model.components){
    const vertices=part.vertices.map(cameraPoint);
    for(const triangle of part.triangles){const v=triangle.map(i=>vertices[i]);if(v.some(p=>p[2]<.03))continue;faces.push({z:v.reduce((s,p)=>s+p[2],0)/3,p:v.map(project),color:part.color||'#8899aa'});}
   }
   faces.sort((a,b)=>b.z-a.z);ctx.save();ctx.beginPath();ctx.rect(0,70,1280,650);ctx.clip();
   for(const f of faces){ctx.beginPath();f.p.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.globalAlpha=.75;ctx.fillStyle=f.color;ctx.fill();ctx.globalAlpha=.5;ctx.strokeStyle='#d3e0ec';ctx.lineWidth=1;ctx.stroke();}ctx.restore();ctx.globalAlpha=1;
   status.textContent=pose.is_training?`${t.toFixed(3)}秒：寸法調整に使った画像への投影です。検証成功には数えません。注釈の一部に角の取り違え・遮蔽境界の疑いがあり、再調整中です。`:`${t.toFixed(3)}秒：画像上の判定を通過。計算点の平均二乗誤差の平方根 ${pose.reprojection_rmse_px.toFixed(2)}px、検査点の95パーセンタイル ${pose.holdout_p95_px.toFixed(2)}px。仮寸法に対する姿勢推定で、実寸精度の実証ではありません。`;
  }else{ctx.fillStyle='#e8edf3';ctx.font='30px sans-serif';ctx.fillText('位置不明 — このフレームのモデル投影は表示しません',35,130);const reasons={insufficient_independent_landmarks:'追跡できた対応点が不足',insufficient_ransac_support:'カメラ計算に十分な点が一致しない',holdout_reprojection_mismatch:'計算に使わなかった点とのずれが大きい',insufficient_holdout_spread:'確認用の点が画面の狭い範囲に偏る',reprojection_error:'計算点とのずれが大きい',intrinsics_unavailable:'カメラの画角を推定できない'};status.textContent=`${t.toFixed(3)}秒：${reasons[pose.failure_reason]||pose.failure_reason}。${pose.holdout_p95_px?`検査点のずれ ${pose.holdout_p95_px.toFixed(2)}px。`:''}座標を補っていません。`;}
  for(let i=0;i<row.observed_pixels.length;i++){const p=row.observed_pixels[i];if(!p)continue;ctx.strokeStyle=row.fit_ids.includes(i)?'#ffbd68':'#50d8f0';ctx.lineWidth=2;ctx.beginPath();ctx.arc(p[0],p[1],5,0,Math.PI*2);ctx.stroke();ctx.font='18px sans-serif';ctx.fillStyle=ctx.strokeStyle;ctx.fillText(String(i+1),p[0]+8,p[1]-7);}
  canvas.dataset.frameId=row.frame_id;canvas.dataset.poseKnown=!!pose.position;
 }
 slider.addEventListener('input',()=>{document.querySelector('#mapping-sync').checked=false;draw(+slider.value);});
 document.querySelector('#mapping-seek').onclick=()=>player?.seekTo(data.rows[+slider.value].file_timestamp,true);
 const initial=Math.max(0,data.rows.findIndex(r=>r.independent_evaluation_eligible&&r.camera_pose.position));draw(initial);
 window.onYouTubeIframeAPIReady=()=>{player=new window.YT.Player('source-player',{videoId:'wJGk8oiqysw',playerVars:{start:433,origin:location.origin,playsinline:1},events:{onError:()=>{document.querySelector('#source-time-link').textContent='埋め込み動画を表示できません。YouTubeで元の場面を見る';}}});};
 if(window.YT?.Player)window.onYouTubeIframeAPIReady();else {const script=document.createElement('script');script.src='https://www.youtube.com/iframe_api';document.head.append(script);}
 setInterval(()=>{if(!document.querySelector('#mapping-sync').checked||!player?.getCurrentTime)return;const t=player.getCurrentTime();let best=0;data.rows.forEach((r,i)=>{if(Math.abs(r.file_timestamp-t)<Math.abs(data.rows[best].file_timestamp-t))best=i;});if(Math.abs(data.rows[best].file_timestamp-t)<=.026)draw(best);else{background(`${t.toFixed(3)} 秒 — 検証区間外`);status.textContent='この時刻の姿勢データはありません。位置や動きを補間していません。';canvas.dataset.poseKnown='false';}},50);
}catch(error){status.textContent='照合結果を読み込めませんでした。下のJSONで確認できます。';canvas.dataset.ready='false';}
