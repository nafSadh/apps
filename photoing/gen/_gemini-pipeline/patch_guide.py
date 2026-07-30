import re

with open('build_deep_curated_guide.py', 'r', encoding='utf-8') as f:
    script = f.read()

# Fix 1: Stop LOC from returning 'notdigitized' by pre-filtering
script = script.replace("if image_url and link:", "if image_url and link and 'notdigitized' not in image_url and 'static' not in image_url:")

# Fix 2: Remove dark mode inline styles from Masterclass block
script = script.replace('style="background:#1a1a1a; padding: 20px; margin-bottom: 30px; border-radius: 8px; color: #fff;"', 'class="annotation-case-study" style="padding: 1.5rem; margin-bottom: 2.5rem; border: 1px solid var(--line); border-radius: 12px; background: var(--paper-hi);"')
script = script.replace('color: #FFD700;', 'color: var(--street);')
script = script.replace('color:#ccc;', 'color: var(--ink-soft);')
script = script.replace('color:#00FFCC;', 'color: var(--fuji);')
script = script.replace('background: #2a2a2a; border-left: 4px solid #FF3366;', 'background: var(--paper); border-left: 4px solid var(--street); color: var(--ink);')
script = script.replace('color:#aaa;', 'color: var(--dim);')

# Fix 3: Fix SVGs and original mapping
script = script.replace(''''drills': {
        'orig': 'images/img_009.jpg',
        'svg': \'''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><line x1="0" y1="50" x2="100" y2="50" stroke="#00FFCC" stroke-width="1"/><text x="50" y="48" fill="#00FFCC" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">HORIZON LINE DRILL</text></svg>\'''
    },''', ''''drills': {
        'orig': 'images/img_010.jpg',
        'svg': \'''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><line x1="0" y1="42" x2="100" y2="42" stroke="#b8422a" stroke-width="0.5"/><text x="50" y="40" fill="#b8422a" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">HORIZON LINE ALIGNMENT</text></svg>\'''
    },''')

script = script.replace(''''ethics': {
        'orig': 'images/img_010.jpg',
        'svg': \'''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><polygon points="50,10 90,90 10,90" stroke="#FF3366" stroke-width="0.5" fill="none"/><text x="50" y="85" fill="#FF3366" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">SUBJECT DIGNITY TRIANGLE</text></svg>\'''
    }''', ''''ethics': {
        'orig': 'images/img_009.jpg',
        'svg': \'''<svg class="overlay" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:10;"><polygon points="45,30 75,90 15,90" stroke="#b8422a" stroke-width="0.5" fill="none"/><text x="45" y="88" fill="#b8422a" font-family="monospace" font-size="3" font-weight="bold" text-anchor="middle">SUBJECT DIGNITY TRIANGLE</text></svg>\'''
    }''')

# Fix 4: Restore .fig-row layout instead of inline grid
script = script.replace('''    # Render the 9 standard figures in a grid
    new_main += '    <div class="gallery-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px;">\\n'
    for img in items:
        c_filt = 'style="filter: grayscale(100%); width: 100%; border-radius: 4px;" ' if img['bw_filter'] else 'style="width: 100%; border-radius: 4px;" '
        new_main += f\'''      <figure style="margin:0;">
        <img src="{img['url']}" alt="{img['title']}" {c_filt}loading="lazy">
        <figcaption style="font-size: 0.85em; margin-top: 8px;"><b>{img['title']}</b><br>
          <b>{img['badge']}</b> — {img['desc']}<br>
          <span style="color:#666; font-family:monospace;">⚙️ {img['exif']}</span><br>
          <span class="ex"><a href="{img['link']}" target="_blank" rel="noopener">Source Page</a> · {img['domain']}</span></figcaption>
      </figure>\\n\'''
    new_main += '    </div>\\n'
''', '''    # Restore beautiful .fig-row rendering
    for i in range(0, len(items), 2):
        pair = items[i:i+2]
        new_main += '    <div class="fig-row" style="display: flex; gap: 1.5rem; margin-bottom: 2rem;">\\n'
        for img in pair:
            c_filt = 'style="filter: grayscale(100%); width: 100%; border-radius: 8px; object-fit: cover; aspect-ratio: 4/3;" ' if img['bw_filter'] else 'style="width: 100%; border-radius: 8px; object-fit: cover; aspect-ratio: 4/3;" '
            new_main += f\'''      <figure style="flex: 1; min-width: 0;">
        <img src="{img['url']}" alt="{img['title']}" {c_filt}loading="lazy">
        <figcaption style="font-size: 0.85rem; margin-top: 0.8rem; color: var(--dim);"><strong style="color: var(--ink-soft);">{img['title']}</strong><br>
          <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; letter-spacing: 0.05em; text-transform: uppercase;">{img['badge']}</span> — {img['desc']}<br>
          <span style="color: var(--street); font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;">⚙️ {img['exif']}</span><br>
          <span class="ex" style="font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; text-transform: uppercase;"><a href="{img['link']}" target="_blank" rel="noopener" style="color: inherit; text-decoration: none; border-bottom: 1px solid var(--line);">Source Page</a> · {img['domain']}</span></figcaption>
      </figure>\\n\'''
        new_main += '    </div>\\n'
''')

# Fix border colors in the masterclass section
script = script.replace('border: 2px solid #FF3366;', 'border: 2px solid var(--fuji);')
script = script.replace('border: 2px solid #00FFCC;', 'border: 2px solid var(--street);')

with open('build_deep_curated_guide.py', 'w', encoding='utf-8') as f:
    f.write(script)
