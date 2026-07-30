import re, shutil, sys

P = '/Users/nafsadh/src/apps/photoing/street-guide.html'
shutil.copy(P, P + '.bak-pair')
lines = open(P).read().split('\n')

FIG_OPEN = '    <figure class="fig-narrow">'
FIG_CLOSE = '    </figure>'

# 1. index every standalone fig-narrow figure as (start,end) line pairs, line-based, no regex spans
figs = []
i = 0
while i < len(lines):
    if lines[i] == FIG_OPEN:
        j = i + 1
        while j < len(lines) and lines[j] != FIG_CLOSE:
            if lines[j].strip().startswith('<figure'):
                sys.exit('nested figure at %d' % j)
            j += 1
        if j >= len(lines):
            sys.exit('unterminated figure at %d' % i)
        body = lines[i:j+1]
        has_anno = any('class="anno"' in b for b in body)
        figs.append({'s': i, 'e': j, 'anno': has_anno})
        i = j + 1
    else:
        i += 1

print('standalone fig-narrow figures:', len(figs),
      '| with annotation overlay:', sum(1 for f in figs if f['anno']))

# 2. group consecutive non-anno figures (only separated by blank lines) into runs
runs, cur = [], []
for k, f in enumerate(figs):
    if f['anno']:
        if cur: runs.append(cur); cur = []
        continue
    if cur:
        between = lines[cur[-1]['e']+1:f['s']]
        if any(b.strip() for b in between):
            runs.append(cur); cur = []
    cur.append(f)
if cur: runs.append(cur)

# 3. build pair groups. odd run -> first figure stays full column, rest paired.
groups = []
for run in runs:
    if len(run) < 2:
        continue
    r = run if len(run) % 2 == 0 else run[1:]
    for a in range(0, len(r), 2):
        groups.append((r[a], r[a+1]))

print('runs:', [len(r) for r in runs])
print('pairs to build:', len(groups))

# 4. rewrite, bottom-up so earlier indices stay valid
out = list(lines)
for a, b in sorted(groups, key=lambda g: -g[0]['s']):
    if b['s'] != a['e'] + 1:
        # blank lines between; collapse them
        pass
    body_a = ['  ' + l if l.strip() else l for l in out[a['s']:a['e']+1]]
    body_b = ['  ' + l if l.strip() else l for l in out[b['s']:b['e']+1]]
    body_a[0] = '      <figure>'
    body_a[-1] = '      </figure>'
    body_b[0] = '      <figure>'
    body_b[-1] = '      </figure>'
    block = ['    <div class="fig-row">'] + body_a + body_b + ['    </div>']
    out[a['s']:b['e']+1] = block

txt = '\n'.join(out)
open(P, 'w').write(txt)

for t in ('figure', 'figcaption', 'section', 'div'):
    o = len(re.findall(r'<%s[ >]' % t, txt)); c = len(re.findall(r'</%s>' % t, txt))
    print(t, o, c, 'OK' if o == c else 'MISMATCH')
print('total <figure:', txt.count('<figure'))
print('fig-narrow left:', txt.count('class="fig-narrow"'))
print('fig-row blocks:', txt.count('class="fig-row"'))
