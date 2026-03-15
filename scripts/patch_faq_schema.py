#!/usr/bin/env python3
"""
Add FAQPage JSON-LD schema to technique pages that lack it.
Also adds twitter:card meta where missing.
"""
import os, re, json

# FAQ templates per category/keyword
FAQ_TEMPLATES = {
    # submission techniques
    "choke": [
        ("How do you finish a {name}?", "Ensure the blade of your forearm (or wrist) is pressing on the carotid arteries — not the windpipe. Squeeze with the bicep and forearm simultaneously while extending your hips."),
        ("Is the {name} legal in BJJ competitions?", "Yes, {name} is legal at all belt levels in most BJJ competitions including IBJJF. Always check the specific ruleset for your event."),
        ("How long does it take to master the {name}?", "Most practitioners can achieve a functional {name} within 6-12 months of consistent training. Mastery — knowing all defenses, entries, and variations — typically takes 2-3 years."),
    ],
    "armbar": [
        ("What is the most common mistake with the {name}?", "The most common mistake is bridging too early before the arm is properly extended. Squeeze your knees, control the wrist, then apply hip pressure."),
        ("Is the {name} legal in all BJJ competitions?", "Yes, the armbar is legal at all belt levels in IBJJF and most other organizations."),
        ("How do you defend against an {name}?", "Clasp your hands together immediately when they try to isolate your arm. Keep your elbow bent and your thumb pointing up. Stack and free your arm before they can extend."),
    ],
    "guard": [
        ("How do you enter {name}?", "The most common entry to {name} is from closed guard or by pulling guard from standing. Focus on grip establishment before committing to the position."),
        ("What are the main attacks from {name}?", "{name} offers sweeps, back takes, and submission setups depending on your opponent's posture and weight distribution."),
        ("How do you pass the {name}?", "The key to passing {name} is breaking the grips first, then using knee cuts, torreando, or leg drag passes to get past the guard."),
    ],
    "sweep": [
        ("When is the best time to attempt a {name}?", "The {name} works best when your opponent's weight is forward or they post in the direction of the sweep. Timing the hip bump with their forward lean dramatically increases success rate."),
        ("What if the {name} fails?", "If the sweep is blocked, immediately look to switch to a submission — triangle choke or armbar — as your opponent's defensive posture often creates openings."),
        ("How much strength does the {name} require?", "The {name} relies primarily on leverage and timing rather than strength. A lighter practitioner can successfully sweep a heavier opponent with proper mechanics."),
    ],
    "takedown": [
        ("Is the {name} effective in BJJ competition?", "Yes, the {name} scores 2 points in most BJJ rulesets and puts you in a dominant ground position to work from. It's a high-value investment."),
        ("How do you defend against the {name}?", "Maintaining good posture, keeping your head up, and sprawling quickly are the primary defenses against {name}."),
        ("Can beginners learn the {name}?", "Yes — the {name} is considered a fundamental technique that beginners should prioritize in their first year of training."),
    ],
    "escape": [
        ("How do you practice the {name}?", "Drill the {name} movement pattern first without resistance, then in controlled positional sparring. Start slow with a cooperative partner before adding resistance."),
        ("What is the key detail in the {name}?", "Timing and framing are everything in the {name}. You must create space before the movement — attempting to escape without a frame first rarely works."),
        ("When should you attempt the {name}?", "Attempt the {name} immediately when you find yourself in the bad position. The longer you wait, the more settled your opponent's weight becomes and the harder it gets to escape."),
    ],
    "lock": [
        ("How dangerous is the {name}?", "The {name} can cause serious injury if applied without control. Always tap early in training, and apply slowly in drilling. It attacks a vulnerable joint."),
        ("Is the {name} legal in BJJ?", "Legality depends on the competition ruleset and belt level. Check your specific organization's rules before competing. Higher belts generally have access to more leg/foot locks."),
        ("How do you defend against the {name}?", "The best defense is positional — avoid getting into leg entanglements against someone with better leg lock skills. If caught, tap early rather than trying to power through."),
    ],
    "default": [
        ("How long does it take to learn {name}?", "Most practitioners can develop a functional {name} within 6 months to 1 year of consistent training. Mastery of all variations and counters takes several years."),
        ("Is {name} good for beginners?", "{name} is worth learning at any level, but it is most effectively drilled once you have a foundation of basic positions and movements."),
        ("What are the best drills for {name}?", "Positional drilling is the fastest way to improve {name}. Practice with a resisting partner in isolated scenarios — start from the beginning of the technique and work through to completion."),
    ],
}

def get_faq_template(slug, content):
    """Pick appropriate FAQ template based on slug/content keywords."""
    slug_lower = slug.lower()
    if any(w in slug_lower for w in ['choke','strangle','mata']):
        return FAQ_TEMPLATES['choke']
    if 'armbar' in slug_lower or 'arm-bar' in slug_lower:
        return FAQ_TEMPLATES['armbar']
    if 'guard' in slug_lower:
        return FAQ_TEMPLATES['guard']
    if 'sweep' in slug_lower:
        return FAQ_TEMPLATES['sweep']
    if any(w in slug_lower for w in ['takedown','throw','nage','goshi','drag']):
        return FAQ_TEMPLATES['takedown']
    if any(w in slug_lower for w in ['escape','roll','shrimp']):
        return FAQ_TEMPLATES['escape']
    if any(w in slug_lower for w in ['lock','hook','bar']):
        return FAQ_TEMPLATES['lock']
    return FAQ_TEMPLATES['default']

def make_faq_schema(slug, name, faqs):
    items = []
    for q_tmpl, a_tmpl in faqs:
        q = q_tmpl.format(name=name)
        a = a_tmpl.format(name=name)
        items.append({
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}
        })
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>'

TWITTER_CARD = '<meta name="twitter:card" content="summary_large_image">\n'

fixed_faq = 0
fixed_twitter = 0

for lang in ['en', 'ja', 'pt']:
    for fname in sorted(os.listdir(lang)):
        if not fname.endswith('.html'):
            continue
        path = f'{lang}/{fname}'
        with open(path) as f:
            content = f.read()

        changed = False
        slug = fname.replace('.html', '')

        # Extract page name from title tag
        title_match = re.search(r'<title>([^<|]+)', content)
        name = title_match.group(1).strip() if title_match else slug.replace('-', ' ').title()

        # Add FAQPage schema if missing
        if 'FAQPage' not in content and 'Article' in content:
            faqs = get_faq_template(slug, content)
            schema_html = make_faq_schema(slug, name, faqs)
            # Insert before </head>
            content = content.replace('</head>', f'{schema_html}\n</head>', 1)
            fixed_faq += 1
            changed = True

        # Add twitter:card if missing
        if 'twitter:card' not in content and 'og:title' in content:
            content = content.replace(
                '<meta name="twitter:card"', '<!-- already -->', 1  # no-op guard
            )
            # Insert after og:title meta
            og_match = re.search(r'<meta property="og:title"[^\n]+\n', content)
            if og_match:
                content = content[:og_match.end()] + TWITTER_CARD + content[og_match.end():]
                fixed_twitter += 1
                changed = True

        if changed:
            with open(path, 'w') as f:
                f.write(content)

print(f"Added FAQPage schema to: {fixed_faq} pages")
print(f"Added twitter:card to:   {fixed_twitter} pages")
