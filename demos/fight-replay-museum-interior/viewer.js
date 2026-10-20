import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const host=document.querySelector('#viewer'),status=document.querySelector('#viewer-status');
try {
 const responses=await Promise.all([fetch('interior.json?v=20261020-v3'),fetch('context-model.json?v=20261020-v3')]);
 if(responses.some(r=>!r.ok))throw new Error('model unavailable');
 const [model,context]=await Promise.all(responses.map(r=>r.json()));
 const scene=new THREE.Scene();scene.background=new THREE.Color('#17212b');
 const camera=new THREE.PerspectiveCamera(48,1,.03,10000);
 const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));host.replaceChildren(renderer.domElement);
 renderer.domElement.setAttribute('aria-label','博物館の内部構造の仮説モデル。ドラッグで回転できます。');
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.minDistance=.5;controls.maxDistance=6500;
 scene.add(new THREE.HemisphereLight(0xecf2ff,0x53616b,2.7));const light=new THREE.DirectionalLight(0xfff2dc,2.5);light.position.set(600,1000,-400);scene.add(light);
 const hall=new THREE.Group(),world=new THREE.Group(),shop=new THREE.Group();scene.add(hall,world,shop);
 const clickable=[];
 function add(part,group,inspect=false){
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices.flatMap(p=>[p[0],p[2],-p[1]]),3));geo.setIndex(part.triangles.flat());geo.computeVertexNormals();
  const glass=part.role==='glass';const mesh=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:part.color||'#9ba8b3',roughness:.82,side:THREE.DoubleSide,transparent:glass,opacity:glass?.22:1,depthWrite:!glass}));mesh.userData=part;group.add(mesh);if(inspect)clickable.push(mesh);return mesh;
 }
 const hallMeshes=model.components.map(p=>add(p,hall,true));
 for(const p of [context.terrain,...context.rocks,...context.buildings,...context.landmarks])add(p,world);
 for(const space of model.unlocated_spaces||[])for(const p of space.components)add(p,shop,true);
 const matrix=model.world_attachment.local_xy_to_world_xy,scale=model.world_attachment.z_scale;
 function point(u,v,z){const x=u-122.5,y=122.5-v;return new THREE.Vector3(matrix[0][0]*x+matrix[0][1]*y+matrix[0][2],z*scale,-(matrix[1][0]*x+matrix[1][1]*y+matrix[1][2]));}
 const roof=document.querySelector('#roof'),walls=document.querySelector('#walls'),contextToggle=document.querySelector('#context');let mode='cutaway';
 const graph=new Map(model.navigation.nodes.map(n=>[n.id,[]]));for(const e of model.navigation.edges){graph.get(e.from).push(e.to);graph.get(e.to).push(e.from);}
 const queue=[['court']],seen=new Set(['court']);let route=[];
 while(queue.length){const path=queue.shift(),id=path.at(-1);if(id==='shop_counter_front'){route=path;break;}for(const n of graph.get(id)){if(!seen.has(n)){seen.add(n);queue.push([...path,n]);}}}
 const nodeById=new Map(model.navigation.nodes.map(n=>[n.id,n]));
 const routePoints=route.map(id=>{const [x,y,z]=nodeById.get(id).world_position;return new THREE.Vector3(x,z+.25*scale,-y);});
 const routeLine=new THREE.Line(new THREE.BufferGeometry().setFromPoints(routePoints),new THREE.LineBasicMaterial({color:0x42dce7}));hall.add(routeLine);
 const marker=new THREE.Mesh(new THREE.SphereGeometry(.5*scale,14,10),new THREE.MeshBasicMaterial({color:0x42dce7}));hall.add(marker);
 const routeSlider=document.querySelector('#route');routeSlider.max=Math.max(0,route.length-1);
 function layers(){
  for(const mesh of hallMeshes)mesh.visible=(mesh.userData.layer!=='roof'||roof.checked)&&(mesh.userData.layer!=='side_wall'||walls.checked);
  world.visible=contextToggle.checked;hall.visible=true;shop.visible=false;contextToggle.disabled=false;
  routeLine.visible=mode!=='world';marker.visible=mode!=='world';
 }
 function view(name){
  mode=name;controls.enableRotate=true;contextToggle.checked=name==='world';
  if(name==='world'){camera.position.set(1450,1300,1500);controls.target.set(0,0,0);}
  else if(name==='shop'){camera.position.copy(point(48,143,14));controls.target.copy(point(34,123,0));}
  else if(name==='floor'){camera.position.copy(point(104,123,-7));controls.target.copy(point(78,123,-7));walls.checked=true;}
  else if(name==='stairs'){camera.position.copy(point(101,105,12));controls.target.copy(point(106,123,-5));walls.checked=false;}
  else {camera.position.copy(point(132,155,33));controls.target.copy(point(91,123,-3));walls.checked=false;}
  document.querySelector('#mode-status').textContent=name==='shop'?'S17の見学映像では、展示室から二段階の階段と中央の斜路を経て売店へ進めます。モデルも接続しました。距離・高さは仮定です。':name==='world'?'全域モデルの同じ座標に内部モデルを暫定配置しています。配置の根拠はミニマップの画像照合で、高さと部屋の向きは未校正です。':'展示ホール・上の通路・階段の形状を確認しています。部屋の配置と寸法は、複数の映像を参考にした仮説です。';
  layers();controls.update();
 }
 for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>view(button.dataset.view);
 for(const input of [roof,walls,contextToggle])input.onchange=layers;
 function setRoute(i,follow=false){
  if(!route.length)return;marker.position.copy(routePoints[i]).add(new THREE.Vector3(0,.35*scale,0));
  document.querySelector('#route-label').textContent=`モデル内の経路確認点 ${i+1} / ${route.length}。実際に歩いた軌跡や、プレイヤーの推定位置ではありません。`;
  if(follow){mode='floor';contextToggle.checked=false;walls.checked=true;const n=nodeById.get(route[i]).world_position;camera.position.set(n[0],n[2]+2*scale,-n[1]);
   const next=nodeById.get(route[Math.min(i+1,route.length-1)]).world_position;const target=new THREE.Vector3(next[0],next[2]+2*scale,-next[1]);
   if(target.distanceTo(camera.position)<.1)target.add(new THREE.Vector3(-scale,0,0));controls.target.copy(target);layers();controls.update();}
 }
 routeSlider.oninput=()=>{setRoute(Number(routeSlider.value),true);document.querySelector('#mode-status').textContent='作成したモデル内の床と階段の接続を確認しています。実ゲームの歩行経路や人物の推定位置ではありません。';};setRoute(0);view('cutaway');
 const raycaster=new THREE.Raycaster();let down=null;
 renderer.domElement.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);
 renderer.domElement.addEventListener('pointerup',e=>{
  if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;
  const r=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);
  const hit=raycaster.intersectObjects(clickable).find(h=>h.object.visible&&h.object.parent.visible);if(!hit)return;
  const p=hit.object.userData;const names={floor:'床',step:'階段',wall:'壁・開口部の周囲',exhibit:'展示・什器',glass:'ガラス屋根',beam:'屋根の梁',column:'柱'};
  document.querySelector('#part-status').textContent=`${names[p.role]||'形状'}：${p.evidence_ids.length?'映像に同種の構造を確認しています。':'見えていない範囲を補う仮の形状です。'} この位置・高さ・寸法は未測定です。`;
 });
 new ResizeObserver(()=>{renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();}).observe(host);
 status.textContent=`展示室から売店まで、接続した内部の${model.components.length}形状を読み込みました。`;host.dataset.ready='true';
 function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}animate();
}catch(error){status.textContent='内部モデルを読み込めませんでした。下の動画・モデルデータでも確認できます。';host.dataset.ready='false';}
