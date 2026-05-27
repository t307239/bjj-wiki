#!/usr/bin/env python3
"""
Add floating bottom-right Beehiiv CTA to all technique pages.
Appears after 30s or on scroll-past 50% — dismissable, non-intrusive.
"""
import os, re

NON_TECHNIQUE = {
    'index.html','skill-tree.html','sparring-simulator.html','news.html',
    'about.html','privacy.html','404.html','athletes.html',
}

FLOATING_CTA_EN = '''
<!-- Floating Newsletter CTA -->
<div id="float-cta" style="position:fixed;bottom:20px;right:20px;max-width:280px;background:#0d2010;border:1px solid #2e7d32;border-radius:14px;padding:16px 18px;box-shadow:0 4px 20px rgba(0,200,83,.15);z-index:999;display:none;animation:slideUp .3s ease">
  <button onclick="document.getElementById('float-cta').style.display='none';localStorage.setItem('cta_dismissed','1')" style="position:absolute;top:8px;right:12px;background:none;border:none;color:#546e7a;font-size:1rem;cursor:pointer;line-height:1">✕</button>
  <div style="font-weight:700;color:#a5d6a7;margin-bottom:6px;font-size:.9rem">📬 Weekly BJJ Tips</div>
  <p style="font-size:.8rem;color:#c8e6c9;margin:0 0 12px">Technique breakdowns & competition insights. Free.</p>
  <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener noreferrer"
     style="display:block;background:#2e7d32;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem;text-align:center"
     onclick="gtag('event','float_cta_click',{lang:'en'})">
    Subscribe Free →
  </a>
</div>
<style>
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
</style>
<script>
(function(){
  if(localStorage.getItem('cta_dismissed')) return;
  var shown = false;
  function show(){
    if(!shown){
      shown=true;
      document.getElementById('float-cta').style.display='block';
    }
  }
  // Show after 30 seconds
  setTimeout(show, 30000);
  // Or when scrolled past 50% of page
  window.addEventListener('scroll',function(){
    var pct = window.scrollY/(document.body.scrollHeight-window.innerHeight);
    if(pct>0.5) show();
  },{passive:true});
})();
</script>
'''

FLOATING_CTA_JA = '''
<!-- Floating Newsletter CTA -->
<div id="float-cta" style="position:fixed;bottom:20px;right:20px;max-width:280px;background:#0d2010;border:1px solid #2e7d32;border-radius:14px;padding:16px 18px;box-shadow:0 4px 20px rgba(0,200,83,.15);z-index:999;display:none;animation:slideUp .3s ease">
  <button onclick="document.getElementById('float-cta').style.display='none';localStorage.setItem('cta_dismissed','1')" style="position:absolute;top:8px;right:12px;background:none;border:none;color:#546e7a;font-size:1rem;cursor:pointer;line-height:1">✕</button>
  <div style="font-weight:700;color:#a5d6a7;margin-bottom:6px;font-size:.9rem">📬 週刊BJJニュースレター</div>
  <p style="font-size:.8rem;color:#c8e6c9;margin:0 0 12px">新技解説・コンペ情報を毎週お届け。無料。</p>
  <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener noreferrer"
     style="display:block;background:#2e7d32;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem;text-align:center"
     onclick="gtag('event','float_cta_click',{lang:'ja'})">
    無料購読する →
  </a>
</div>
<style>@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}</style>
<script>(function(){if(localStorage.getItem('cta_dismissed'))return;var shown=false;function show(){if(!shown){shown=true;document.getElementById('float-cta').style.display='block';}}setTimeout(show,30000);window.addEventListener('scroll',function(){var pct=window.scrollY/(document.body.scrollHeight-window.innerHeight);if(pct>0.5)show();},{passive:true});})();</script>
'''

FLOATING_CTA_PT = '''
<!-- Floating Newsletter CTA -->
<div id="float-cta" style="position:fixed;bottom:20px;right:20px;max-width:280px;background:#0d2010;border:1px solid #2e7d32;border-radius:14px;padding:16px 18px;box-shadow:0 4px 20px rgba(0,200,83,.15);z-index:999;display:none;animation:slideUp .3s ease">
  <button onclick="document.getElementById('float-cta').style.display='none';localStorage.setItem('cta_dismissed','1')" style="position:absolute;top:8px;right:12px;background:none;border:none;color:#546e7a;font-size:1rem;cursor:pointer;line-height:1">✕</button>
  <div style="font-weight:700;color:#a5d6a7;margin-bottom:6px;font-size:.9rem">📬 Newsletter Semanal de BJJ</div>
  <p style="font-size:.8rem;color:#c8e6c9;margin:0 0 12px">Dicas de treino e análises de competição. Grátis.</p>
  <a href="https://bjjwiki.beehiiv.com/subscribe" target="_blank" rel="noopener noreferrer"
     style="display:block;background:#2e7d32;color:#fff;padding:8px 16px;border-radius:8px;text-decoration:none;font-weight:700;font-size:.85rem;text-align:center"
     onclick="gtag('event','float_cta_click',{lang:'pt'})">
    Assinar Grátis →
  </a>
</div>
<style>@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}</style>
<script>(function(){if(localStorage.getItem('cta_dismissed'))return;var shown=false;function show(){if(!shown){shown=true;document.getElementById('float-cta').style.display='block';}}setTimeout(show,30000);window.addEventListener('scroll',function(){var pct=window.scrollY/(document.body.scrollHeight-window.innerHeight);if(pct>0.5)show();},{passive:true});})();</script>
'''

CTA_BY_LANG = {'en': FLOATING_CTA_EN, 'ja': FLOATING_CTA_JA, 'pt': FLOATING_CTA_PT}

fixed = 0
for lang in ['en', 'ja', 'pt']:
    cta = CTA_BY_LANG[lang]
    for fname in sorted(os.listdir(lang)):
        if not fname.endswith('.html'): continue
        if fname in NON_TECHNIQUE: continue
        path = f'{lang}/{fname}'
        with open(path) as f:
            content = f.read()
        if 'float-cta' in content:
            continue
        content = content.replace('</body>', f'{cta}\n</body>', 1)
        with open(path, 'w') as f:
            f.write(content)
        fixed += 1

print(f"Added floating CTA to: {fixed} pages")
