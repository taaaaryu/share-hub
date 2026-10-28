'use strict';

const chaptersEl = document.getElementById('chapters');
const navEl = document.getElementById('chapter-nav');
const titleEl = document.getElementById('deck-title');
const subtitleEl = document.getElementById('deck-subtitle');
const shareButton = document.getElementById('share-button');
const printButton = document.getElementById('print-button');
const toast = document.getElementById('toast');
const disclosure = document.getElementById('toc-disclosure');
const mobileQuery = window.matchMedia('(max-width: 900px)');

let deck = null;
let chapterNodes = [];
let activeChapter = 1;

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

function showToast(message) {
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('visible');
  window.setTimeout(() => toast.classList.remove('visible'), 2400);
}

function splitLabel(slide, index) {
  const number = String(index + 1).padStart(2, '0');
  const raw = (slide.label || '').trim();
  const match = raw.match(/^\d+\s*\/\s*(.+)$/);
  return { number, label: match ? match[1].trim() : (raw || slide.title || number) };
}

function chapterFigure(slide, content) {
  const figure = el('figure', 'chapter-figure');
  const link = el('a', 'chapter-figure-link');
  link.href = slide.image;
  link.target = '_blank';
  link.rel = 'noopener noreferrer';
  const image = el('img');
  if (Number.isInteger(slide.image_width) && Number.isInteger(slide.image_height)) {
    image.width = slide.image_width;
    image.height = slide.image_height;
    if (image.height > image.width) {
      figure.classList.add('portrait');
      content.classList.add('has-portrait');
    }
  }
  image.src = slide.image;
  image.alt = slide.image_alt || '';
  link.append(image);
  const caption = el('figcaption');
  if (slide.image_alt) caption.append(el('span', 'figure-alt', slide.image_alt));
  caption.append(el('span', 'figure-open', '画像を開いて拡大'));
  figure.append(link, caption);
  const markPortrait = () => {
    if (image.naturalHeight > image.naturalWidth && image.naturalWidth > 0) {
      figure.classList.add('portrait');
      content.classList.add('has-portrait');
    }
  };
  image.addEventListener('load', markPortrait);
  if (image.complete) window.requestAnimationFrame(markPortrait);
  return figure;
}

function chapterMetrics(slide) {
  const list = el('dl', 'chapter-metrics');
  for (const metric of slide.metrics) {
    const item = el('div', 'metric');
    item.append(el('dt', null, metric.name || ''));
    item.append(el('dd', null, metric.value === undefined ? '' : metric.value));
    if (metric.note) item.append(el('p', 'metric-note', metric.note));
    list.append(item);
  }
  return list;
}

function chapterColumns(slide) {
  const table = el('table', 'chapter-columns');
  const body = el('tbody');
  for (const column of slide.columns) {
    const row = el('tr');
    const heading = el('th', null, column.heading || '');
    heading.scope = 'row';
    row.append(heading, el('td', null, column.text || ''));
    body.append(row);
  }
  table.append(body);
  return table;
}

function chapterFlow(slide) {
  const list = el('ol', 'chapter-flow');
  slide.flow.forEach((step, index) => {
    const item = el('li', 'flow-step');
    item.append(el('span', 'flow-number', String(index + 1).padStart(2, '0')));
    item.append(el('strong', 'flow-title', step.title || ''));
    if (step.body) item.append(el('p', 'flow-body', step.body));
    list.append(item);
  });
  return list;
}

function chapterTerms(slide) {
  const list = el('dl', 'chapter-terms');
  for (const term of slide.terms) {
    const item = el('div', 'term');
    item.append(el('dt', null, term.term || ''), el('dd', null, term.meaning || ''));
    list.append(item);
  }
  return list;
}

function chapterSources(slide) {
  const list = el('ul', 'chapter-sources');
  for (const source of slide.sources) {
    if (!/^https?:\/\//i.test(source.url || '')) continue;
    const item = el('li');
    const link = el('a', null, source.label || source.url);
    link.href = source.url;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    item.append(link);
    list.append(item);
  }
  return list.children.length ? list : null;
}

function renderChapter(slide, index) {
  const id = String(index + 1);
  const section = el('section', 'publication-chapter');
  section.id = id;
  const headingId = `chapter-${id}-title`;
  section.setAttribute('aria-labelledby', headingId);

  const parts = splitLabel(slide, index);
  const meta = el('p', 'chapter-meta');
  meta.append(el('span', 'chapter-number', parts.number), el('span', 'chapter-label', parts.label));
  section.append(meta);

  const heading = el('h2', null, slide.title || '');
  heading.id = headingId;
  section.append(heading);

  const content = el('div', 'chapter-content');
  const text = el('div', 'chapter-text');
  if (slide.body) text.append(el('p', 'chapter-lead', slide.body));
  if (Array.isArray(slide.paragraphs)) {
    for (const paragraph of slide.paragraphs) {
      if (paragraph) text.append(el('p', 'chapter-paragraph', paragraph));
    }
  }
  if (Array.isArray(slide.items) && slide.items.length) {
    const items = el('ul', 'chapter-items');
    for (const item of slide.items) items.append(el('li', null, item));
    text.append(items);
  }
  content.append(text);

  if (slide.image) content.append(chapterFigure(slide, content));
  if (Array.isArray(slide.metrics) && slide.metrics.length) content.append(chapterMetrics(slide));
  if (Array.isArray(slide.columns) && slide.columns.length) content.append(chapterColumns(slide));
  if (Array.isArray(slide.flow) && slide.flow.length) content.append(chapterFlow(slide));
  if (Array.isArray(slide.terms) && slide.terms.length) content.append(chapterTerms(slide));
  if (Array.isArray(slide.sources) && slide.sources.length) {
    const sources = chapterSources(slide);
    if (sources) content.append(sources);
  }

  section.append(content);
  return { section, label: `${parts.number} ${parts.label.split(" / ").pop()}` };
}

function setActive(id) {
  const numeric = Number(id);
  if (!Number.isFinite(numeric)) return;
  activeChapter = numeric;
  for (const link of navEl.querySelectorAll('a')) {
    const isActive = link.dataset.target === String(numeric);
    link.classList.toggle('active', isActive);
    if (isActive) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}

function setupObserver() {
  if (!('IntersectionObserver' in window)) return;
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) setActive(entry.target.id);
    }
  }, { rootMargin: '-72px 0px -60% 0px', threshold: 0 });
  for (const node of chapterNodes) observer.observe(node);
}

function scrollForHash() {
  const match = window.location.hash.match(/^#(\d+)$/);
  if (!match) return;
  const target = document.getElementById(match[1]);
  if (target) window.requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
}

function render(data) {
  chaptersEl.replaceChildren();
  navEl.replaceChildren();
  chapterNodes = [];

  data.slides.forEach((slide, index) => {
    const result = renderChapter(slide, index);
    chaptersEl.append(result.section);
    chapterNodes.push(result.section);

    const link = el('a', null, result.label);
    link.href = `#${index + 1}`;
    link.dataset.target = String(index + 1);
    link.addEventListener('click', () => {
      if (mobileQuery.matches && disclosure) disclosure.open = false;
    });
    navEl.append(link);
  });

  setActive('1');
  setupObserver();
  scrollForHash();
}

async function sharePage() {
  const url = `${window.location.origin}${window.location.pathname}#${activeChapter}`;
  try {
    if (navigator.share) {
      await navigator.share({ title: deck ? deck.title : document.title, url });
    } else if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(url);
      showToast('リンクをコピーしました');
    } else {
      throw new Error('clipboard unavailable');
    }
  } catch (error) {
    if (error && error.name === 'AbortError') return;
    showToast('共有できませんでした。URLをコピーしてください。');
  }
}

if (shareButton) shareButton.addEventListener('click', sharePage);
if (printButton) printButton.addEventListener('click', () => window.print());

if (disclosure) {
  disclosure.open = !mobileQuery.matches;
  const onViewportChange = event => { disclosure.open = !event.matches; };
  if (mobileQuery.addEventListener) mobileQuery.addEventListener('change', onViewportChange);
  else if (mobileQuery.addListener) mobileQuery.addListener(onViewportChange);
}

window.addEventListener('hashchange', scrollForHash);

window.addEventListener('keydown', event => {
  const target = event.target;
  if (target && (/^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName) || target.isContentEditable)) return;
  if (event.metaKey || event.ctrlKey || event.altKey) return;
  const forward = event.key === 'ArrowRight';
  const backward = event.key === 'ArrowLeft';
  if (!forward && !backward) return;
  if (!chapterNodes.length) return;
  event.preventDefault();
  const next = Math.min(chapterNodes.length, Math.max(1, activeChapter + (forward ? 1 : -1)));
  const section = document.getElementById(String(next));
  if (section) section.scrollIntoView({ block: 'start' });
});

fetch('deck.json', { cache: 'no-store' })
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    if (!data || !Array.isArray(data.slides) || !data.slides.length) throw new Error('No slides');
    deck = data;
    titleEl.textContent = data.title || '資料';
    if (subtitleEl) subtitleEl.textContent = data.subtitle || '';
    document.title = `${data.title || '資料'} | Share Hub`;
    render(data);
  })
  .catch(() => {
    titleEl.textContent = '資料を読み込めませんでした';
    const message = el('p', 'publication-error', '資料を読み込めませんでした。ページを再読み込みしてください。');
    message.setAttribute('role', 'alert');
    chaptersEl.replaceChildren(message);
  });
