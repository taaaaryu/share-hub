import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
const host=document.querySelector('#sparse-viewer'),status=document.querySelector('#sparse-status');
try{
 const rs=await Promise.all(['sfm-result.json','sfm-short-grid.json'].map(p=>fetch(p+'?v=20261020-v1')));if(rs.some(r=>!r.ok))throw Error('data unavailable');
 const [data,grid]=await Promise.all(rs.map(r=>r.json()));const xyz=p=>new THREE.Vector3(p[0],-p[1],-p[2]);
 const scene=new THREE.Scene();scene.background=new THREE.Color('#17212b');
 const camera=new THREE.PerspectiveCamera(48,1,.01,1000),renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));host.replaceChildren(renderer.domElement);renderer.domElement.setAttribute('aria-label','実映像から得た相対的な3D点群。建物モデルとはまだ位置を合わせていません。');
 const geometry=new THREE.BufferGeometry().setFromPoints(data.points_relative.map(xyz));scene.add(new THREE.Points(geometry,new THREE.PointsMaterial({color:0x64cfff,size:.1,sizeAttenuation:true})));
 const bounds=new THREE.Box3().setFromBufferAttribute(geometry.getAttribute('position')),centre=bounds.getCenter(new THREE.Vector3()),span=Math.max(...bounds.getSize(new THREE.Vector3()).toArray(),5);
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.copy(centre);controls.enableDamping=true;camera.position.copy(centre).add(new THREE.Vector3(span*.8,span*.45,span*.8));
 const markers=[];grid.rows.forEach((row,i)=>{if(!row.position)return;const p=xyz(row.position),marker=new THREE.Mesh(new THREE.SphereGeometry(.08,12,8),new THREE.MeshBasicMaterial({color:row.is_construction_frame?0xffb460:0x69e0b0}));marker.position.copy(p);scene.add(marker);markers[i]=marker;});
 const selected=new THREE.Mesh(new THREE.SphereGeometry(.16,12,8),new THREE.MeshBasicMaterial({color:0xffffff,wireframe:true}));scene.add(selected);
 const slider=document.querySelector('#sparse-time');slider.max=grid.rows.length-1;
 function setFrame(i){const r=grid.rows[i];selected.visible=!!r.position;if(r.position)selected.position.copy(xyz(r.position));status.textContent=`${r.file_timestamp.toFixed(3)}秒：${r.is_construction_frame?'点群の作成に使った画像（成功数から除外）':r.position?`別時刻の検証を通過。検査点のずれ ${r.holdout_p95_px.toFixed(2)}px`:'位置不明。前後をつないでいません'}。残った点 ${r.surviving_points} 個。距離はメートルではありません。`;document.querySelector('#sparse-source').href=`https://www.youtube.com/watch?v=wJGk8oiqysw&t=${r.file_timestamp.toFixed(3)}s`;host.dataset.frameId=r.frame_id;host.dataset.poseKnown=!!r.position;}
 slider.oninput=()=>setFrame(+slider.value);setFrame(0);
 new ResizeObserver(()=>{renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();}).observe(host);
 function render(){requestAnimationFrame(render);controls.update();renderer.render(scene,camera);}render();host.dataset.ready='true';
}catch(e){status.textContent='点群を読み込めませんでした。下のJSONをご確認ください。';host.dataset.ready='false';}
