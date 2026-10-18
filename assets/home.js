const list = document.getElementById('deck-list');
const count = document.getElementById('deck-count');
fetch('catalog.json').then(response => response.json()).then(decks => {
  count.textContent = `${decks.length}件`;
  for (const deck of decks) {
    if (!/^[a-z0-9-]+$/.test(deck.slug)) continue;
    const link = document.createElement('a');
    link.className = 'deck-card';
    link.href = `slides/${deck.slug}/`;
    const icon = document.createElement('span');
    icon.className = 'deck-card-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.textContent = '↗';
    const copy = document.createElement('span');
    copy.className = 'deck-card-copy';
    const title = document.createElement('strong');
    title.textContent = deck.title;
    const description = document.createElement('small');
    description.textContent = deck.description;
    const arrow = document.createElement('span');
    arrow.className = 'deck-card-arrow';
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '→';
    copy.append(title, description);
    link.append(icon, copy, arrow);
    list.append(link);
  }
}).catch(() => { count.textContent = '読み込みに失敗しました'; });
