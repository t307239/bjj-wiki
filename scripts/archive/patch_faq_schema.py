#!/usr/bin/env python3
"""FAQ schema patch for pages without FAQPage JSON-LD"""
import os, re, glob, json

BASE = os.path.dirname(__file__) + "/.."

def make_faq(slug, lang):
    clean = slug.replace("-", " ").title()
    if lang == "en":
        return [
            {"q": f"What is {clean} in BJJ?", "a": f"{clean} is a key technique in Brazilian Jiu-Jitsu used to control, sweep, or submit an opponent. Practiced at all belt levels, it requires correct body positioning, leverage, and timing to execute effectively."},
            {"q": f"How do I learn {clean}?", "a": f"Start with slow cooperative drilling to build muscle memory for the correct mechanics. Focus on body position, weight distribution, and grip placement before adding resistance. Video study and regular instructor feedback accelerate progress significantly."},
            {"q": f"What belt level is {clean} appropriate for?", "a": f"{clean} can be introduced at white belt, with deeper competition application developing at blue belt and above. Some advanced variations suit intermediate practitioners best. Always train under a qualified instructor."},
        ]
    elif lang == "ja":
        return [
            {"q": f"{clean}とはBJJにおいて何ですか？", "a": f"{clean}はブラジリアン柔術において相手をコントロール・スイープ・サブミットするための重要なテクニックです。正確なボディポジション・レバレッジ・タイミングが求められ、全帯レベルで練習されます。"},
            {"q": f"{clean}はどのように練習しますか？", "a": f"正しいメカニクスの筋肉記憶を築くため、まず協調的なパートナーとのスロードリルから始めます。ボディポジション・体重配分・グリップに集中し、徐々にレジスタンスを上げていきます。映像学習とインストラクターのフィードバックが上達を加速させます。"},
            {"q": f"{clean}はどの帯レベルに適していますか？", "a": f"{clean}は白帯から紹介可能で、競技への本格応用は青帯以上で発展します。高度なバリエーションは中級者向けです。常に有資格インストラクターの指導のもとで練習してください。"},
        ]
    else:
        return [
            {"q": f"O que é {clean} no BJJ?", "a": f"{clean} é uma técnica importante no Brazilian Jiu-Jitsu para controlar, varrer ou finalizar um oponente. Requer posicionamento correto, alavancagem e timing, sendo praticada em todos os níveis de faixa."},
            {"q": f"Como aprender {clean}?", "a": f"Comece com drills cooperativos lentos para construir memória muscular. Foque em posicionamento, distribuição de peso e posição dos grips antes de adicionar resistência. Estudo em vídeo e feedback do instrutor aceleram o progresso."},
            {"q": f"Para qual nível de faixa é adequado {clean}?", "a": f"{clean} pode ser introduzido na faixa branca, com aplicação em competição se desenvolvendo na faixa azul e acima. Sempre treine sob orientação de um instrutor qualificado."},
        ]

def patch_file(path, lang):
    with open(path) as f:
        html = f.read()
    if '"FAQPage"' in html or 'FAQPage' in html:
        return False
    if 'http-equiv="refresh"' in html:
        return False
    slug = os.path.basename(path).replace(".html","")
    faqs = make_faq(slug, lang)
    schema = json.dumps({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in faqs
    ]}, ensure_ascii=False)
    tag = f'<script type="application/ld+json">\n{schema}\n</script>\n'
    if '</head>' in html:
        html = html.replace('</head>', tag + '</head>', 1)
        with open(path,'w') as f: f.write(html)
        return True
    return False

def main():
    patched = skipped = 0
    skip_names = {"index.html","privacy.html","about.html","athletes.html","404.html","already_posted_x.txt"}
    for lang in ["en","ja","pt"]:
        for path in glob.glob(os.path.join(BASE, lang, "*.html")):
            if os.path.basename(path) in skip_names: continue
            if patch_file(path, lang): patched += 1
            else: skipped += 1
    print(f"FAQ schema added: {patched} pages, skipped: {skipped}")

if __name__ == "__main__":
    main()
