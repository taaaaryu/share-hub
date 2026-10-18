import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const host = document.getElementById('viewer');
const status = document.getElementById('viewer-status');
try {
  const [modelResponse, trackResponse] = await Promise.all([fetch('model.json'), fetch('minimap-track.json')]);
  if (!modelResponse.ok || !trackResponse.ok) throw new Error('model data unavailable');
  const model = await modelResponse.json();
  const track = await trackResponse.json();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#101923');
  const camera = new THREE.PerspectiveCamera(45, 1, .1, 1200);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(host.clientWidth, host.clientHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  host.replaceChildren(renderer.domElement);
  renderer.domElement.setAttribute('aria-label', 'ミニマップを基準に作った3Dモデル。ドラッグで回転できます。');
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.minDistance = 12;
  controls.maxDistance = 420;
  scene.add(new THREE.HemisphereLight(0xe3eeff, 0x47515b, 2.4));
  const light = new THREE.DirectionalLight(0xffecd7, 3);
  light.position.set(60, 100, 90);
  scene.add(light);
  const group = new THREE.Group();
  scene.add(group);
  const meshes = [];
  for (const part of model.components) {
    const [a, b] = [part.min, part.max];
    const material = new THREE.MeshStandardMaterial({ color: new THREE.Color(...part.color.map(c => c / 255)), roughness: .84 });
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(b[0] - a[0], b[2] - a[2], b[1] - a[1]), material);
    mesh.position.set((a[0] + b[0]) / 2, (a[2] + b[2]) / 2, -(a[1] + b[1]) / 2);
    mesh.userData = part;
    mesh.visible = part.layer !== 'context';
    group.add(mesh);
    meshes.push(mesh);
    const edge = new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry), new THREE.LineBasicMaterial({ color: 0x465362, transparent: true, opacity: .45 }));
    mesh.add(edge);
  }
  const grid = new THREE.GridHelper(200, 20, 0x344555, 0x243443);
  grid.position.y = -11;
  scene.add(grid);
  const pin = new THREE.Group();
  const pinMat = new THREE.MeshBasicMaterial({ color: 0x38e2e8 });
  const stem = new THREE.Mesh(new THREE.CylinderGeometry(.45, .45, 7, 12), pinMat);
  stem.position.y = 3.5;
  const head = new THREE.Mesh(new THREE.SphereGeometry(1.4, 16, 10), pinMat);
  head.position.y = 7.5;
  pin.add(stem, head);
  scene.add(pin);
  for (let i = 1; i < track.rows.length; i++) {
    const a = track.rows[i - 1], b = track.rows[i];
    if (!a.player_xy || !b.player_xy || b.file_timestamp - a.file_timestamp > 1.01) continue;
    const points = [a.player_xy, b.player_xy].map(p => new THREE.Vector3(p[0], .15, -p[1]));
    scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), new THREE.LineBasicMaterial({ color: 0x38a4b7 })));
  }
  function view(mode) {
    if (mode === 'top') { camera.position.set(-30, 170, .01); controls.target.set(-30, -2, 0); }
    else if (mode === 'entry') { camera.position.set(22, 35, 45); controls.target.set(-22, -3, 0); }
    else { camera.position.set(75, 90, 115); controls.target.set(-30, 0, 0); }
    controls.update();
  }
  view('whole');
  for (const button of document.querySelectorAll('[data-view]')) button.addEventListener('click', () => view(button.dataset.view));
  document.getElementById('context-toggle').addEventListener('change', e => {
    for (const mesh of meshes) if (mesh.userData.layer === 'context') mesh.visible = e.target.checked;
  });
  const sample = document.getElementById('sample');
  sample.max = track.rows.length - 1;
  const cursor = document.getElementById('mini-cursor');
  function setSample(index) {
    const row = track.rows[index];
    document.getElementById('sample-label').textContent = `素材ファイルの ${row.file_timestamp.toFixed(1)} 秒`;
    pin.visible = Boolean(row.player_xy);
    cursor.style.display = row.player_xy ? '' : 'none';
    if (row.player_xy) {
      pin.position.set(row.player_xy[0], 0, -row.player_xy[1]);
      cursor.setAttribute('cx', row.registration.reference_pixel[0]);
      cursor.setAttribute('cy', row.registration.reference_pixel[1]);
      document.getElementById('position-status').textContent = row.reference_frame ? '基準場面の平面位置です。高さ・階層は不明です。' : 'ミニマップの照合条件を通った平面位置です。高さ・階層は不明です。';
    } else document.getElementById('position-status').textContent = 'このサンプルは照合条件を満たさないため、位置を表示していません。';
  }
  sample.addEventListener('input', () => setSample(Number(sample.value)));
  setSample(0);
  const raycaster = new THREE.Raycaster();
  let down = null;
  renderer.domElement.addEventListener('pointerdown', e => { down = [e.clientX, e.clientY]; });
  renderer.domElement.addEventListener('pointerup', e => {
    if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
    const rect = renderer.domElement.getBoundingClientRect();
    raycaster.setFromCamera(new THREE.Vector2((e.clientX - rect.left) / rect.width * 2 - 1, -(e.clientY - rect.top) / rect.height * 2 + 1), camera);
    const hit = raycaster.intersectObjects(meshes, false).find(h => h.object.visible);
    if (!hit) return;
    const p = hit.object.userData;
    const plan = p.xy_source === 'manual_minimap_trace' ? '平面の輪郭をミニマップから手動で指定しました。' : '平面上の細かな位置は、映像を参考に仮置きしています。';
    document.getElementById('selected-part').textContent = `${plan} 高さは未測定の仮の設定です。`;
  });
  new ResizeObserver(() => {
    camera.aspect = host.clientWidth / host.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(host.clientWidth, host.clientHeight);
  }).observe(host);
  status.textContent = `${model.components.length}個の形状を表示しています。ドラッグで回転、スクロールで拡大できます。`;
  host.dataset.ready = 'true';
  function animate() { requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }
  animate();
} catch (error) {
  status.textContent = '3D表示を読み込めませんでした。下の静止画とOBJファイルでも確認できます。';
  host.dataset.ready = 'false';
}
