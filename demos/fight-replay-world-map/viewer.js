import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const host=document.querySelector('#viewer'),status=document.querySelector('#status');
try{
 const responses=await Promise.all([fetch('world-map.json?v=ice-frustum-v2'),fetch('matches.json')]);
 if(responses.some(r=>!r.ok))throw new Error('data');
 const [model,track]=await Promise.all(responses.map(r=>r.json()));
 const scene=new THREE.Scene();scene.background=new THREE.Color('#17212b');
 const camera=new THREE.PerspectiveCamera(45,1,1,12000);
 const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));host.replaceChildren(renderer.domElement);
 const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.maxDistance=6500;
 scene.add(new THREE.HemisphereLight(0xe7eeff,0x67604c,2.6));const sun=new THREE.DirectionalLight(0xffffff,2);sun.position.set(-600,1600,900);scene.add(sun);
 const parts=[];
 function addMesh(part,color){
  const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices.flatMap(p=>[p[0],p[2],-p[1]]),3));geometry.setIndex(part.triangles.flat());geometry.computeVertexNormals();
  const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color,roughness:.95,side:THREE.DoubleSide}));scene.add(mesh);return mesh;
 }
 addMesh(model.terrain,0x777763);
 for(const b of [...model.buildings,...(model.rocks||[]),...(model.landmarks||[])]){const mesh=addMesh(b,b.color||'#92a3b2');mesh.userData=b;parts.push(mesh);}
 function view(top=false){camera.position.set(top?0:1450,top?2650:1300,top?.1:1500);controls.target.set(0,0,0);controls.update();}
 view();document.querySelector('#top').onclick=()=>view(true);document.querySelector('#orbit').onclick=()=>view();
 document.querySelector('#buildings').onchange=e=>parts.forEach(p=>p.visible=e.target.checked);
 const pin=new THREE.Mesh(new THREE.SphereGeometry(15,18,12),new THREE.MeshBasicMaterial({color:0x42e8eb}));scene.add(pin);
 const rows=track.rows,slider=document.querySelector('#sample');slider.max=rows.length-1;
 function sample(i){const r=rows[i],m=r.match,p=m.holdout_outliers===0?m.atlas_pixel:null;pin.visible=Boolean(p);if(p)pin.position.set(p[0]-1024,350,p[1]-1024);document.querySelector('#sample-label').textContent=`素材 ${r.file_timestamp.toFixed(1)}秒：${p?'平面位置の照合を受理。ピンの高さは表示用で、実際の階層は不明です。':m.atlas_pixel?'受理条件は通りますが、確認用の目印に誤対応が残るため位置を非表示にしています。':'照合を受理できないため、位置は表示していません。'}`;}
 slider.oninput=()=>sample(Number(slider.value));sample(0);
 new ResizeObserver(()=>{renderer.setSize(host.clientWidth,host.clientHeight);camera.aspect=host.clientWidth/host.clientHeight;camera.updateProjectionMatrix();}).observe(host);
 status.textContent=`全域の地面、岩稜${model.rocks.length}候補、屋根${model.buildings.length}候補、設備など${model.landmarks.length}形状を表示。高さは未測定の仮定です。`;host.dataset.ready='true';
 function animate(){requestAnimationFrame(animate);controls.update();renderer.render(scene,camera);}animate();
}catch(e){status.textContent='3Dを読み込めませんでした。ダウンロード用のモデルデータを確認してください。';host.dataset.ready='false';}
