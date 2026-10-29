'use strict';
const target = document.getElementById('chapters');
const nav = document.getElementById('chapter-nav');
const disclosure = document.getElementById('toc-disclosure');
let slides = [];
let current = 1;
const node = (tag, className, text) => { const e=document.createElement(tag); if(className)e.className=className; if(text!==undefined)e.textContent=String(text); return e; };
function render() {
  const n = Number(location.hash.slice(1));
  current = Number.isInteger(n) && n >= 1 && n <= slides.length ? n : 1;
  const slide=slides[current-1]; if(!slide)return;
  document.body.classList.toggle('viewing-screen',current>1);
  const section=node('section','publication-chapter'); section.id='slide';
  const meta=node('p','chapter-meta'); meta.append(node('span','chapter-number',String(current).padStart(2,'0')),node('span','chapter-label',slide.label));
  section.append(meta,node('h2','',slide.title));
  const content=node('div','chapter-content'), text=node('div','chapter-text');
  text.append(node('p','chapter-lead',slide.body));
  if(slide.paragraphs)for(const p of slide.paragraphs) text.append(node('p','chapter-paragraph',p));
  content.append(text);
  if(slide.image) {
    const figure=node('figure','chapter-figure'), link=node('a','chapter-figure-link'), img=node('img');
    if(slide.image_kind==='panel')figure.classList.add('panel-image');
    link.href=slide.image; link.target='_blank'; link.rel='noopener noreferrer';
    img.src=slide.image; img.alt=slide.image_alt || slide.title; img.width=slide.image_width; img.height=slide.image_height; link.append(img);
    const caption=node('figcaption'); caption.append(node('span','figure-alt',slide.image_alt),node('span','figure-open','画像を開いて拡大')); figure.append(link,caption); content.append(figure);
  }
  if(slide.sources) { const ul=node('ul','chapter-sources'); for(const source of slide.sources){const li=node('li'), a=node('a','',source.label);a.href=source.url;a.target='_blank';a.rel='noopener noreferrer';li.append(a);ul.append(li)} content.append(ul); }
  section.append(content);target.replaceChildren(section);
  for(const id of ['counter','counter-bottom'])document.getElementById(id).textContent=`${current} / ${slides.length}`;
  for(const id of ['prev','prev-bottom'])document.getElementById(id).disabled=current===1;
  for(const id of ['next','next-bottom'])document.getElementById(id).disabled=current===slides.length;
  for(const a of nav.querySelectorAll('a')) { const selected=Number(a.dataset.num)===current; a.classList.toggle('active',selected); if(selected)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current'); }
}
function go(delta){const hash=Number(location.hash.slice(1));const base=Number.isInteger(hash)&&hash>=1&&hash<=slides.length?hash:current;const n=Math.max(1,Math.min(slides.length,base+delta));if(n!==base)location.hash=String(n)}
for(const id of ['prev','prev-bottom'])document.getElementById(id).addEventListener('click',()=>go(-1));
for(const id of ['next','next-bottom'])document.getElementById(id).addEventListener('click',()=>go(1));
window.addEventListener('hashchange',()=>{render();window.scrollTo({top:0,behavior:'auto'})});
window.addEventListener('keydown',e=>{if(e.ctrlKey||e.metaKey||e.altKey||/^(INPUT|SELECT|TEXTAREA)$/.test(e.target.tagName))return;if(e.key==='ArrowRight'){e.preventDefault();go(1)}else if(e.key==='ArrowLeft'){e.preventDefault();go(-1)}});
document.getElementById('share-button').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);document.getElementById('toast').textContent='リンクをコピーしました';document.getElementById('toast').classList.add('visible');setTimeout(()=>document.getElementById('toast').classList.remove('visible'),2000)}catch{document.getElementById('toast').textContent='ブラウザのURLをコピーしてください';document.getElementById('toast').classList.add('visible');setTimeout(()=>document.getElementById('toast').classList.remove('visible'),2000)}});
fetch('deck.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(data=>{slides=data.slides;if(!slides.length)throw Error('empty');document.getElementById('deck-subtitle').textContent=data.subtitle;slides.forEach((slide,i)=>{const a=node('a','',`${String(i+1).padStart(2,'0')} ${slide.title}`);a.href=`#${i+1}`;a.dataset.num=i+1;a.addEventListener('click',()=>{if(matchMedia('(max-width:900px)').matches)disclosure.open=false});nav.append(a)});disclosure.open=!matchMedia('(max-width:900px)').matches;render()}).catch(()=>{target.replaceChildren(node('p','publication-error','資料を読み込めませんでした。ページを再読み込みしてください。'))});
