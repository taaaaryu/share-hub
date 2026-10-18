const video = document.getElementById('review-video');
const status = document.getElementById('player-status');
for (const button of document.querySelectorAll('[data-seek]')) {
  button.addEventListener('click', () => {
    const seek = () => {
      video.currentTime = Number(button.dataset.seek);
      video.play().catch(() => { status.textContent = '動画の再生ボタンを押してください。'; });
    };
    if (video.readyState >= 1) seek();
    else video.addEventListener('loadedmetadata', seek, { once: true });
  });
}
video.addEventListener('error', () => { status.textContent = '動画を読み込めませんでした。保存リンクから開いてください。'; });
