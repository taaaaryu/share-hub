const slideEl = document.getElementById('slide');
const titleEl = document.getElementById('deck-title');
const counterEl = document.getElementById('counter');
const dotsEl = document.getElementById('progress-dots');
const prevButton = document.getElementById('prev-button');
const nextButton = document.getElementById('next-button');
const shareButton = document.getElementById('share-button');
const toast = document.getElementById('toast');
let deck = null;
let current = 1;

function node(tag, className, value) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  if (value !== undefined) el.textContent = value;
  return el;
}

function brand() {
  const wordmark = node('span', 'brand');
  wordmark.append(node('span', 'brand-mark'), node('span', 'brand-name', 'Slide Share'));
  return wordmark;
}

function hashSlide() {
  const match = location.hash.match(/^#(\d+)$/);
  const requested = match ? Number(match[1]) : 1;
  return Math.max(1, Math.min(requested, deck.slides.length));
}

function render() {
  if (!deck) return;
  current = hashSlide();
  const data = deck.slides[current - 1];
  slideEl.replaceChildren();
  slideEl.className = `slide ${data.kind || ''}`;
  slideEl.style.setProperty('--progress', `${current / deck.slides.length * 100}%`);
  const top = node('div', 'slide-top');
  top.append(node('span', 'slide-label', data.label || ''), brand());
  const content = node('div', 'slide-content');
  const heading = node('h1', '', data.title || '');
  if (data.accent) heading.prepend(node('span', 'accent-word', data.accent + ' '));
  content.append(heading, node('p', '', data.body || ''));
  if (Array.isArray(data.items) && data.items.length) {
    const list = node('div', 'slide-steps');
    for (const item of data.items) list.append(node('span', 'slide-step', item));
    content.append(list);
  }
  if (Array.isArray(data.metrics) && data.metrics.length) {
    const grid = node('div', 'slide-metrics');
    for (const metric of data.metrics) {
      const card = node('div', 'metric-card');
      card.append(node('strong', '', metric.value), node('span', '', metric.name), node('small', '', metric.note || ''));
      grid.append(card);
    }
    content.append(grid);
  }
  if (Array.isArray(data.columns) && data.columns.length) {
    const grid = node('div', 'slide-columns');
    for (const column of data.columns) {
      const card = node('div', 'column-card');
      card.append(node('strong', '', column.heading), node('span', '', column.text));
      grid.append(card);
    }
    content.append(grid);
  }
  if (Array.isArray(data.sources) && data.sources.length) {
    const list = node('div', 'slide-sources');
    for (const source of data.sources) {
      if (!/^https?:\/\//.test(source.url || '')) continue;
      const link = node('a', '', `${source.label} ↗`);
      link.href = source.url;
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      list.append(link);
    }
    content.append(list);
  }
  slideEl.append(top, content);
  if (data.kind === 'cover' && deck.theme === 'terminal-night') {
    const art = node('img', 'cover-art');
    art.src = '../../assets/analysis-dashboard.svg';
    art.alt = '';
    slideEl.append(art);
  } else if (data.visual) slideEl.append(node('div', 'slide-visual', data.visual));
  const slideFooter = node('div', 'slide-chrome-footer');
  slideFooter.append(node('span', '', '© Slide Share'), node('strong', '', String(current)));
  slideEl.append(slideFooter);
  counterEl.textContent = `${current} / ${deck.slides.length}`;
  dotsEl.replaceChildren(...deck.slides.map((_, i) => node('i', i + 1 === current ? 'active' : '')));
  prevButton.disabled = current === 1;
  nextButton.disabled = current === deck.slides.length;
  document.title = `${data.title.replace(/\n/g, ' ')} | ${deck.title}`;
}

function navigate(delta) {
  const target = Math.max(1, Math.min(current + delta, deck.slides.length));
  if (target !== current) location.hash = String(target);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('visible');
  setTimeout(() => toast.classList.remove('visible'), 2200);
}

prevButton.addEventListener('click', () => navigate(-1));
nextButton.addEventListener('click', () => navigate(1));
window.addEventListener('hashchange', render);
window.addEventListener('keydown', event => {
  if (event.key === 'ArrowRight') navigate(1);
  if (event.key === 'ArrowLeft') navigate(-1);
});
let touchStartX = null;
slideEl.addEventListener('touchstart', event => { touchStartX = event.changedTouches[0].screenX; }, { passive: true });
slideEl.addEventListener('touchend', event => {
  if (touchStartX === null) return;
  const distance = event.changedTouches[0].screenX - touchStartX;
  touchStartX = null;
  if (Math.abs(distance) > 60) navigate(distance < 0 ? 1 : -1);
}, { passive: true });
shareButton.addEventListener('click', async () => {
  const url = `${location.origin}${location.pathname}#${current}`;
  try {
    if (navigator.share) await navigator.share({ title: deck.title, url });
    else { await navigator.clipboard.writeText(url); showToast('リンクをコピーしました'); }
  } catch (error) {
    if (error.name !== 'AbortError') showToast('共有できませんでした');
  }
});

fetch('deck.json').then(response => {
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}).then(data => {
  if (!Array.isArray(data.slides) || !data.slides.length) throw new Error('No slides');
  deck = data;
  if (deck.theme === 'terminal-night') document.body.classList.add('terminal-theme');
  titleEl.textContent = deck.title || 'スライド';
  render();
}).catch(() => { slideEl.append(node('p', '', 'スライドを読み込めませんでした。ページを再読み込みしてください。')); });
