"""SmokeTrail scene builder.

Generates the inline SVG for the panoramic world (pannable camera) and the
close-up "lens" illustrations. World units: 100 units ~ 1 m near the smoker;
ground surface at y = 540, water table at y = 660. Coordinates used here are
mirrored in assets/js/app.js (camera boxes and labels).
"""
import math
import random

GROUND = 540
WT = 660  # water table


def st(**kw):
    """style attribute from css var names: st(fill='grass') -> style="fill:var(--grass)"."""
    parts = []
    for k, v in kw.items():
        k = k.replace('_', '-')
        if isinstance(v, str) and v.startswith('#') is False and not v.startswith('url') and v not in ('none', 'round', 'non-scaling-stroke') and not v[0].isdigit():
            parts.append(f"{k}:var(--{v})")
        else:
            parts.append(f"{k}:{v}")
    return 'style="' + ';'.join(parts) + '"'


def f(x):
    return (f"{x:.1f}").rstrip('0').rstrip('.')


def person(x, y0=GROUND, h=175, pose='stand', facing=1, cls='', smoking=False):
    r = 0.072 * h
    hy = y0 - h + r
    ys = y0 - 0.80 * h
    yh = y0 - 0.47 * h
    sw, hw = 0.12 * h, 0.095 * h
    lw = 0.085 * h
    aw = 0.07 * h
    out = [f'<g class="person {cls}">']
    out.append(f'<circle cx="{f(x)}" cy="{f(hy)}" r="{f(r)}" {st(fill="fig")}/>')
    out.append(
        f'<path d="M{f(x-sw)} {f(ys+6)} Q{f(x-sw)} {f(ys)} {f(x-sw+6)} {f(ys)} L{f(x+sw-6)} {f(ys)} '
        f'Q{f(x+sw)} {f(ys)} {f(x+sw)} {f(ys+6)} L{f(x+hw)} {f(yh)} L{f(x-hw)} {f(yh)} Z" {st(fill="fig")}/>')
    leg = st(stroke='fig', fill='none', stroke_linecap='round') .replace('"', '')
    lst = f'style="stroke:var(--fig);fill:none;stroke-linecap:round;stroke-width:{f(lw)}"'
    ast = f'style="stroke:var(--fig);fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-width:{f(aw)}"'
    if pose == 'walk':
        out.append(f'<path d="M{f(x-4)} {f(yh+4)} L{f(x-17*facing)} {f(y0-lw/2)}" {lst}/>')
        out.append(f'<path d="M{f(x+4)} {f(yh+4)} L{f(x+16*facing)} {f(y0-lw/2)}" {lst}/>')
        out.append(f'<path d="M{f(x-sw-3)} {f(ys+9)} L{f(x-sw-14*facing)} {f(yh+2)}" {ast}/>')
        out.append(f'<path d="M{f(x+sw+3)} {f(ys+9)} L{f(x+sw+12*facing)} {f(yh)}" {ast}/>')
    else:
        out.append(f'<path d="M{f(x-0.045*h)} {f(yh+4)} L{f(x-0.05*h)} {f(y0-lw/2)}" {lst}/>')
        out.append(f'<path d="M{f(x+0.045*h)} {f(yh+4)} L{f(x+0.05*h)} {f(y0-lw/2)}" {lst}/>')
        out.append(f'<path d="M{f(x-facing*(sw+3))} {f(ys+9)} L{f(x-facing*(sw+6))} {f(yh+2)}" {ast}/>')
        if smoking:
            # bent arm, hand in front of the chest
            ex, ey = x + facing * (sw + 9), ys + 46
            hx, hyy = x + facing * (sw + 22), ys + 22
            out.append(f'<path d="M{f(x+facing*(sw+3))} {f(ys+9)} L{f(ex)} {f(ey)} L{f(hx)} {f(hyy)}" {ast}/>')
        else:
            out.append(f'<path d="M{f(x+facing*(sw+3))} {f(ys+9)} L{f(x+facing*(sw+6))} {f(yh+2)}" {ast}/>')
    out.append('</g>')
    return '\n'.join(out)


def mulberry(seed):
    rnd = random.Random(seed)
    return rnd


def puffs(cx, cy, n, seed, dx, dy, s, t, r, o=0.6, s0=0.35, cls='puff', fill='smoke', grad=None):
    rnd = mulberry(seed)
    out = [f'<g transform="translate({f(cx)} {f(cy)})">']
    for i in range(n):
        ddx = rnd.uniform(*dx)
        ddy = rnd.uniform(*dy)
        ss = rnd.uniform(*s)
        tt = rnd.uniform(*t)
        d = -rnd.uniform(0, tt)
        fl = f'fill:url(#{grad})' if grad else f'fill:var(--{fill})'
        out.append(
            f'<circle class="{cls}" r="{f(r)}" data-dx="{f(ddx)}" data-dy="{f(ddy)}" data-s="{f(ss)}" '
            f'style="{fl};--dx:{f(ddx)}px;--dy:{f(ddy)}px;--s:{f(ss)};--s0:{s0};--t:{tt:.2f}s;--d:{d:.2f}s;--o:{o}"/>')
    out.append('</g>')
    return '\n'.join(out)


def rain(x0, x1, ytop, ybot, n, seed, cls=''):
    rnd = mulberry(seed)
    out = [f'<g class="rain {cls}">']
    for i in range(n):
        x = rnd.uniform(x0, x1)
        y = ytop + rnd.uniform(0, 40)
        tt = rnd.uniform(0.85, 1.25)
        d = -rnd.uniform(0, tt)
        out.append(
            f'<line class="drop" x1="{f(x)}" y1="{f(y)}" x2="{f(x-3)}" y2="{f(y+16)}" '
            f'style="stroke:var(--raindrop);stroke-width:1.6;stroke-linecap:round;--fy:{f(ybot-y-16)}px;--t:{tt:.2f}s;--d:{d:.2f}s"/>')
    out.append('</g>')
    return '\n'.join(out)


def cloud(cx, cy, w, cls='', stages=None):
    ds = f' data-stages="{stages}"' if stages else ''
    k = w / 520
    blobs = [(-170, 18, 90, 46), (-80, -8, 110, 70), (40, -24, 120, 78), (150, 6, 100, 56), (0, 26, 230, 44)]
    out = [f'<g class="cloud {cls}"{ds}>']
    out.append(f'<ellipse cx="{f(cx)}" cy="{f(cy+44*k)}" rx="{f(240*k)}" ry="{f(26*k)}" {st(fill="cloud-shade")}/>')
    for bx, by, rx, ry in blobs:
        out.append(f'<ellipse cx="{f(cx+bx*k)}" cy="{f(cy+by*k)}" rx="{f(rx*k)}" ry="{f(ry*k)}" {st(fill="cloud")}/>')
    out.append('</g>')
    return '\n'.join(out)


def tree(x, h=120, r=46):
    return (f'<g class="tree"><rect x="{f(x-5)}" y="{f(GROUND-h*0.55)}" width="10" height="{f(h*0.55)}" rx="3" {st(fill="wood")}/>'
            f'<circle cx="{f(x)}" cy="{f(GROUND-h*0.62)}" r="{f(r)}" {st(fill="plant")}/>'
            f'<circle cx="{f(x-r*0.55)}" cy="{f(GROUND-h*0.52)}" r="{f(r*0.7)}" {st(fill="plant")}/>'
            f'<circle cx="{f(x+r*0.5)}" cy="{f(GROUND-h*0.75)}" r="{f(r*0.65)}" {st(fill="plant-2")} opacity=".7"/></g>')


def mountains(seed, y_base, y_lo, y_hi, step, x0=-6000, x1=10000, var='hill'):
    rnd = mulberry(seed)
    pts = [f"M{x0} {GROUND}", f"L{x0} {y_base}"]
    x = x0
    up = True
    while x < x1:
        x += rnd.uniform(step * 0.6, step * 1.4)
        y = rnd.uniform(y_lo, y_lo + (y_hi - y_lo) * 0.45) if up else rnd.uniform(y_lo + (y_hi - y_lo) * 0.55, y_hi)
        up = not up
        pts.append(f"L{f(x)} {f(y)}")
    pts.append(f"L{x1} {GROUND} Z")
    return f'<path d="{" ".join(pts)}" {st(fill=var)}/>'


def catmull(points, closed=False):
    p = points
    d = f"M{f(p[0][0])} {f(p[0][1])}"
    for i in range(len(p) - 1):
        p0 = p[i - 1] if i > 0 else p[i]
        p1, p2 = p[i], p[i + 1]
        p3 = p[i + 2] if i + 2 < len(p) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d


SMOKER_X = 260
TIP = (318.5, 415.5)
MOUTH = (272, 382)


def world_svg():
    o = []
    o.append('<svg class="world" id="world" aria-hidden="true" focusable="false" data-stage="0">')
    o.append('''<defs>
  <linearGradient id="g-sky" gradientUnits="userSpaceOnUse" x1="0" y1="-120" x2="0" y2="540">
    <stop offset="0" style="stop-color:var(--sky-top)"/><stop offset="1" style="stop-color:var(--sky-bot)"/>
  </linearGradient>
  <radialGradient id="g-puff"><stop offset="0" style="stop-color:var(--smoke);stop-opacity:.75"/><stop offset=".6" style="stop-color:var(--smoke);stop-opacity:.35"/><stop offset="1" style="stop-color:var(--smoke);stop-opacity:0"/></radialGradient>
  <radialGradient id="g-ember"><stop offset="0" stop-color="#fff4b8"/><stop offset=".35" stop-color="#ffb13b"/><stop offset=".7" stop-color="#e2531f" stop-opacity=".7"/><stop offset="1" stop-color="#e2531f" stop-opacity="0"/></radialGradient>
  <linearGradient id="g-leach" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--residue);stop-opacity:.75"/><stop offset="1" style="stop-color:var(--residue);stop-opacity:0"/></linearGradient>
  <radialGradient id="g-ths"><stop offset="0" style="stop-color:var(--residue);stop-opacity:.55"/><stop offset="1" style="stop-color:var(--residue);stop-opacity:0"/></radialGradient>
</defs>''')
    o.append('<g id="cam">')
    # sky, sun, mountains
    o.append(f'<rect x="-6000" y="-6000" width="16000" height="{6000+GROUND+2}" fill="url(#g-sky)"/>')
    o.append(f'<circle cx="3060" cy="96" r="36" {st(fill="sun")}/>')
    o.append(mountains(7, 430, 300, 420, 150, var='hill-far'))
    o.append(mountains(11, 470, 395, 470, 95, var='hill'))
    o.append(cloud(760, 120, 300))
    o.append(cloud(2280, 90, 260))
    # ground layers
    o.append(f'<rect x="-6000" y="{GROUND}" width="16000" height="{WT-GROUND}" {st(fill="soil-1")}/>')
    o.append(f'<rect x="-6000" y="{WT}" width="16000" height="6000" {st(fill="sat")}/>')
    rnd = mulberry(3)
    peb = []
    for i in range(260):
        x = rnd.uniform(-600, 4200)
        y = rnd.uniform(GROUND + 18, 1100)
        peb.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rnd.uniform(1.5, 4.5))}" {st(fill="soil-2")} opacity=".55"/>')
    o.append('<g class="pebbles">' + ''.join(peb) + '</g>')
    o.append(f'<line x1="-6000" y1="{WT}" x2="10000" y2="{WT}" {st(stroke="gw-line")} stroke-width="1.4" stroke-dasharray="8 7" vector-effect="non-scaling-stroke" opacity=".8"/>')
    o.append(f'<rect x="-6000" y="{GROUND}" width="16000" height="12" {st(fill="grass")}/>')
    # groundwater flow
    o.append('<g class="gwflow">')
    for d, op in [("M1500 712 C2200 712 2900 706 3420 668", .75), ("M1700 760 C2400 760 3000 744 3460 672", .55), ("M2200 820 C2800 818 3300 790 3520 690", .4)]:
        o.append(f'<path class="flow slow" d="{d}" fill="none" {st(stroke="gw-line")} stroke-width="2" vector-effect="non-scaling-stroke" opacity="{op}"/>')
    o.append('</g>')
    # lake / stream
    o.append(f'<path d="M3240 {GROUND+6} C3300 {GROUND+10} 3330 652 3460 656 L10000 656 L10000 {GROUND+6} Z" {st(fill="water")}/>')
    o.append(f'<path d="M3280 {GROUND+30} L10000 {GROUND+30}" {st(stroke="water-deep")} stroke-width="1" opacity=".5" fill="none"/>')
    o.append(f'<line x1="3246" y1="{GROUND+6}" x2="10000" y2="{GROUND+6}" {st(stroke="gw-line")} stroke-width="1.5" vector-effect="non-scaling-stroke" opacity=".7"/>')
    fish = []
    for (fx, fy, sw, k) in [(3420, 600, 80, 1), (3520, 625, -70, .8), (3600, 590, 60, .9)]:
        fish.append(f'<g class="fish" style="--sw:{sw}px"><path d="M{fx} {fy} q{12*k} {-8*k} {24*k} 0 q{-12*k} {8*k} {-24*k} 0 Z M{fx} {fy} l{-8*k} {-6*k} l0 {12*k} Z" {st(fill="water-deep")}/></g>')
    o.append('<g data-stages="10">' + ''.join(fish) + '</g>')
    # trees
    o.append(tree(1270, 130, 44))
    o.append(tree(1880, 150, 50))
    o.append(tree(3190, 120, 40))
    # ---------- house (thirdhand smoke) ----------
    hx0, hx1, hy0 = 1960, 2440, 330
    o.append('<g class="house">')
    o.append(f'<polygon points="1935,{hy0+4} 2200,248 2465,{hy0+4}" {st(fill="roof")}/>')
    o.append(f'<rect x="{hx0}" y="{hy0}" width="{hx1-hx0}" height="{GROUND-hy0}" {st(fill="wall")}/>')
    o.append(f'<rect x="{hx0+14}" y="{hy0+14}" width="{hx1-hx0-28}" height="{GROUND-hy0-14}" {st(fill="interior")}/>')
    o.append(f'<rect x="{hx0+14}" y="{GROUND-8}" width="{hx1-hx0-28}" height="8" {st(fill="wood")}/>')
    o.append(f'<rect x="2000" y="372" width="74" height="62" {st(fill="glass", stroke="frame")} stroke-width="3"/>'
             f'<line x1="2037" y1="372" x2="2037" y2="434" {st(stroke="frame")} stroke-width="2"/><line x1="2000" y1="403" x2="2074" y2="403" {st(stroke="frame")} stroke-width="2"/>')
    o.append(f'<path d="M2080 362 L2100 362 Q2094 392 2101 420 Q2095 452 2102 492 L2080 492 Z" {st(fill="curtain")}/>')
    o.append(f'<rect x="2160" y="382" width="52" height="38" {st(fill="none", stroke="frame")} stroke-width="3"/><rect x="2166" y="388" width="40" height="26" {st(fill="glass")} opacity=".6"/>')
    # sofa
    o.append(f'<rect x="2130" y="462" width="140" height="36" rx="8" {st(fill="sofa")}/><rect x="2122" y="490" width="156" height="30" rx="8" {st(fill="sofa")}/>'
             f'<rect x="2114" y="470" width="20" height="52" rx="7" {st(fill="sofa")}/><rect x="2266" y="470" width="20" height="52" rx="7" {st(fill="sofa")}/>'
             f'<rect x="2126" y="520" width="6" height="12" {st(fill="wood")}/><rect x="2268" y="520" width="6" height="12" {st(fill="wood")}/>')
    o.append(f'<rect x="2140" y="529" width="210" height="4" rx="2" {st(fill="rug")}/>')
    # table + ashtray
    o.append(f'<rect x="2300" y="500" width="72" height="7" rx="2" {st(fill="wood")}/><rect x="2306" y="507" width="4" height="25" {st(fill="wood")}/><rect x="2362" y="507" width="4" height="25" {st(fill="wood")}/>'
             f'<ellipse cx="2336" cy="497" rx="11" ry="3.5" {st(fill="metal")}/><rect x="2330" y="492" width="9" height="2.4" {st(fill="filter")}/>')
    # lamp
    o.append(f'<line x1="2405" y1="420" x2="2405" y2="532" {st(stroke="metal")} stroke-width="3"/><polygon points="2390,421 2420,421 2414,398 2396,398" {st(fill="lamp")}/>'
             f'<rect x="2396" y="529" width="18" height="4" rx="2" {st(fill="metal")}/>')
    # child on the floor
    o.append(f'<g class="child"><circle cx="2228" cy="503" r="8" {st(fill="fig")}/><path d="M2221 513 L2235 513 L2236 528 L2220 528 Z" {st(fill="fig")}/>'
             f'<path d="M2232 527 L2250 529" style="stroke:var(--fig);stroke-width:6;stroke-linecap:round;fill:none"/>'
             f'<path d="M2234 516 L2244 524" style="stroke:var(--fig);stroke-width:5;stroke-linecap:round;fill:none"/>'
             f'<rect x="2252" y="520" width="9" height="9" rx="1.5" {st(fill="rain")}/></g>')
    # cat
    o.append(f'<g class="cat"><ellipse cx="2380" cy="524" rx="16" ry="7.5" {st(fill="fig")}/><circle cx="2398" cy="516" r="6" {st(fill="fig")}/>'
             f'<path d="M2394 511 l2 -7 l3 6 Z M2400 511 l3 -7 l2 7 Z" {st(fill="fig")}/>'
             f'<path d="M2365 522 q-14 -2 -12 -16" style="stroke:var(--fig);stroke-width:3.5;stroke-linecap:round;fill:none"/></g>')
    # residue (THS)
    rnd = mulberry(21)
    sp = []
    for i in range(70):
        x = rnd.uniform(hx0 + 18, hx1 - 18)
        y = rnd.uniform(hy0 + 18, GROUND - 10)
        sp.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rnd.uniform(1.2, 2.8))}" {st(fill="residue")} opacity=".85"/>')
    o.append(f'<g data-stages="7"><rect x="{hx0+14}" y="{hy0+14}" width="{hx1-hx0-28}" height="{GROUND-hy0-22}" {st(fill="residue")} opacity=".16"/>' + ''.join(sp)
             + puffs(2200, 468, 10, 31, (-30, 30), (-80, -50), (1.5, 2.5), (5, 8), 5, o=.55, grad='g-ths')
             + puffs(2092, 430, 6, 32, (-10, 30), (-70, -40), (1.5, 2.4), (5, 8), 5, o=.55, grad='g-ths')
             + puffs(2228, 500, 5, 33, (-10, 10), (-50, -30), (1.2, 2), (4, 7), 4, o=.5, grad='g-ths')
             + '</g>')
    o.append('</g>')
    # ---------- street, drain, pipe ----------
    o.append(f'<rect x="2440" y="{GROUND-2}" width="420" height="12" {st(fill="pave")}/>')
    o.append(f'<line x1="2440" y1="{GROUND-2}" x2="2860" y2="{GROUND-2}" {st(stroke="metal")} stroke-width="1" opacity=".5"/>')
    o.append(f'<rect x="2754" y="{GROUND+10}" width="16" height="78" {st(fill="pipe")}/>')
    o.append(f'<path d="M2762 625 L3310 625 Q3326 625 3340 612" {st(stroke="pipe")} stroke-width="9" fill="none" stroke-linecap="round"/>')
    o.append(f'<path class="flow" d="M2762 560 L2762 625 L3310 625 Q3326 625 3340 612" {st(stroke="residue")} stroke-width="2.4" fill="none" data-stages="8 10"/>')
    o.append(f'<rect x="2740" y="{GROUND-4}" width="44" height="7" rx="1.5" {st(fill="metal")}/>' + ''.join(
        f'<line x1="{2745+i*7}" y1="{GROUND-3}" x2="{2745+i*7}" y2="{GROUND+2}" {st(stroke="pave")} stroke-width="1.6"/>' for i in range(5)))
    # street butt
    o.append(f'<g class="butt"><g transform="rotate(-8 2632 {GROUND-5})"><rect x="2622" y="{GROUND-7}" width="11" height="4.5" rx="1" {st(fill="filter")}/>'
             f'<rect x="2633" y="{GROUND-7}" width="6" height="4.5" {st(fill="paper")}/><rect x="2639" y="{GROUND-7}" width="2.5" height="4.5" {st(fill="ash")}/></g></g>')
    o.append(f'<g data-stages="8"><circle class="pulse" cx="2632" cy="{GROUND-5}" r="14" fill="none" {st(stroke="ember")} stroke-width="2" vector-effect="non-scaling-stroke"/></g>')
    o.append(f'<path class="flow" d="M2600 {GROUND-3} L2745 {GROUND-3}" {st(stroke="rain")} stroke-width="2.5" fill="none" data-stages="8"/>')
    o.append(f'<path class="flow" d="M2641 {GROUND-3} L2745 {GROUND-3}" {st(stroke="residue")} stroke-width="1.6" fill="none" data-stages="8" opacity=".9"/>')
    # ---------- garden ----------
    g = ['<g class="garden">']
    rnd = mulberry(5)
    for i in range(60):
        x = rnd.uniform(2870, 3230)
        hgt = rnd.uniform(5, 12)
        g.append(f'<path d="M{f(x)} {GROUND+2} l{f(rnd.uniform(-3,3))} {f(-hgt)}" {st(stroke="plant-2")} stroke-width="1.6" stroke-linecap="round"/>')
    # basil
    def herb(x, hgt, leaf, sd):
        r = mulberry(sd)
        parts = [f'<path d="M{x} {GROUND} L{x} {GROUND-hgt}" {st(stroke="plant")} stroke-width="3" stroke-linecap="round"/>']
        y = GROUND - 12
        side = 1
        while y > GROUND - hgt:
            parts.append(f'<ellipse cx="{f(x+side*leaf*0.8)}" cy="{f(y)}" rx="{f(leaf)}" ry="{f(leaf*0.5)}" transform="rotate({-25*side} {f(x+side*leaf*0.8)} {f(y)})" {st(fill="plant-2")}/>')
            y -= leaf * 0.9
            side *= -1
        parts.append(f'<ellipse cx="{x}" cy="{f(GROUND-hgt-4)}" rx="{f(leaf*0.7)}" ry="{f(leaf*0.5)}" {st(fill="plant-2")}/>')
        # roots
        for k in range(5):
            ex = x + r.uniform(-22, 22)
            ey = GROUND + r.uniform(30, 58)
            parts.append(f'<path d="M{x} {GROUND+2} Q{f((x+ex)/2 + r.uniform(-8,8))} {f(GROUND+20)} {f(ex)} {f(ey)}" {st(stroke="wood")} stroke-width="1.4" fill="none" opacity=".9"/>')
        return ''.join(parts)
    g.append(herb(2962, 74, 11, 1))
    g.append(herb(3072, 56, 8, 2))
    for cx in (3130, 3150, 3172, 3196, 3214):
        cy = GROUND - 9 - (cx % 3) * 2
        g.append(f'<path d="M{cx} {GROUND} L{cx} {cy}" {st(stroke="plant")} stroke-width="1.4"/>' + ''.join(
            f'<circle cx="{f(cx+4.5*math.cos(a))}" cy="{f(cy+4.5*math.sin(a))}" r="4" {st(fill="plant-2")}/>' for a in (-math.pi/2, math.pi/6, 5*math.pi/6)))
    # leachate plume + garden butt
    g.append(f'<path d="M3006 {GROUND+4} C3000 580 2990 610 3002 650 C3012 676 3048 678 3056 650 C3064 616 3036 584 3024 {GROUND+4} Z" fill="url(#g-leach)" data-stages="9 10"/>')
    rnd = mulberry(9)
    lds = []
    for i in range(8):
        tt = rnd.uniform(3, 5)
        lds.append(f'<circle class="drop" cx="{f(3012+rnd.uniform(-6,8))}" cy="{GROUND+6}" r="1.8" style="fill:var(--residue);--fy:{f(rnd.uniform(70,110))}px;--t:{tt:.2f}s;--d:{-rnd.uniform(0,tt):.2f}s"/>')
    g.append('<g data-stages="9">' + ''.join(lds) + '</g>')
    g.append(f'<g transform="rotate(12 3012 {GROUND-2})"><rect x="3002" y="{GROUND-4}" width="11" height="4.5" rx="1" {st(fill="filter")}/><rect x="3013" y="{GROUND-4}" width="6" height="4.5" {st(fill="paper")}/></g>')
    # uptake dots in basil stem
    ups = []
    for i in range(5):
        tt = 4.5
        ups.append(f'<circle class="drop" cx="2962" cy="{GROUND+40}" r="2.2" style="fill:var(--residue);--fy:-{GROUND+40-(GROUND-66)}px;--t:{tt}s;--d:{-i*tt/5:.2f}s"/>')
    g.append('<g data-stages="9">' + ''.join(ups) + '</g>')
    g.append('</g>')
    o.append('\n'.join(g))
    # ---------- people ----------
    o.append(person(SMOKER_X, smoking=True, cls='smoker'))
    # cigarette in the smoker's hand
    o.append(f'<g class="cig" transform="rotate(-14 {TIP[0]-12} {TIP[1]+3})"><rect x="{TIP[0]-15}" y="{TIP[1]+1}" width="5" height="2.6" {st(fill="filter")}/>'
             f'<rect x="{TIP[0]-10}" y="{TIP[1]+1}" width="9.5" height="2.6" {st(fill="paper")}/></g>')
    o.append(f'<circle class="glow" cx="{TIP[0]}" cy="{TIP[1]}" r="7" fill="url(#g-ember)"/>')
    o.append(person(560, facing=-1, cls='bystander'))
    o.append(person(1760, pose='walk', cls='walker'))
    # particles stuck on the walker (stage 6)
    rnd = mulberry(14)
    dots = []
    for i in range(34):
        # hair cap and coat/torso area
        if i < 9:
            a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
            x, y = 1760 + 13 * math.cos(a), 377.6 + 13 * math.sin(a)
        else:
            x, y = 1760 + rnd.uniform(-19, 19), rnd.uniform(404, 452)
        dots.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rnd.uniform(1.3, 2.4))}" {st(fill="residue")}/>')
    o.append('<g data-stages="6">' + ''.join(dots) + puffs(1760, 420, 8, 41, (-20, 30), (-60, -30), (1.4, 2.2), (5, 8), 4, o=.55, grad='g-ths') + '</g>')
    o.append(f'<g data-stages="11"><circle class="pulse" cx="560" cy="380" r="26" fill="none" {st(stroke="ember")} stroke-width="2" vector-effect="non-scaling-stroke"/></g>')
    o.append(f'<g data-stages="11"><circle class="pulse" cx="1760" cy="380" r="26" fill="none" {st(stroke="ember")} stroke-width="2" vector-effect="non-scaling-stroke"/></g>')
    o.append(f'<g data-stages="11"><circle class="pulse" cx="2228" cy="505" r="20" fill="none" {st(stroke="ember")} stroke-width="2" vector-effect="non-scaling-stroke"/></g>')
    o.append(f'<g data-stages="11"><circle class="pulse" cx="2384" cy="520" r="20" fill="none" {st(stroke="ember")} stroke-width="2" vector-effect="non-scaling-stroke"/></g>')
    # ---------- lungs inside the smoker (stage 2) ----------
    lx, ly = SMOKER_X, 418
    o.append(f'<g data-stages="2"><path d="M{lx-2} {ly-12} C{lx-10} {ly-14} {lx-17} {ly-6} {lx-17} {ly+8} C{lx-17} {ly+20} {lx-12} {ly+24} {lx-6} {ly+23} C{lx-2} {ly+22} {lx-2} {ly+14} {lx-2} {ly+8} Z" {st(fill="lung")}/>'
             f'<path d="M{lx+2} {ly-12} C{lx+10} {ly-14} {lx+17} {ly-6} {lx+17} {ly+8} C{lx+17} {ly+20} {lx+12} {ly+24} {lx+6} {ly+23} C{lx+2} {ly+22} {lx+2} {ly+14} {lx+2} {ly+8} Z" {st(fill="lung")}/>'
             f'<path d="M{lx} {ly-30} L{lx} {ly-10} M{lx} {ly-10} L{lx-8} {ly} M{lx} {ly-10} L{lx+8} {ly}" {st(stroke="lung")} stroke-width="3" fill="none" stroke-linecap="round"/></g>')
    # ---------- smoke ----------
    o.append('<g class="smoke">')
    # sidestream at the tip
    o.append(puffs(TIP[0], TIP[1] - 2, 16, 51, (4, 36), (-70, -130), (2.2, 3.6), (4.5, 7), 2.4, o=.65, s0=.4, grad='g-puff'))
    # exhaled mainstream
    o.append(puffs(MOUTH[0] + 3, MOUTH[1], 12, 52, (40, 120), (-30, 6), (3.5, 5.5), (5, 7.5), 3, o=.6, grad='g-puff'))
    # dispersing plume
    o.append(puffs(330, 380, 34, 53, (420, 1150), (-190, 30), (3.2, 6.5), (16, 24), 16, o=.42, grad='g-puff'))
    o.append('</g>')
    # wind arrows (stage 4)
    wa = []
    for (x, y, L) in [(430, 300, 220), (640, 250, 260), (900, 330, 240), (520, 470, 200)]:
        wa.append(f'<path class="flow" d="M{x} {y} q{L/2} -14 {L} 0" fill="none" {st(stroke="fig")} stroke-width="1.6" vector-effect="non-scaling-stroke" opacity=".45"/>'
                  f'<path d="M{x+L-10} {y-7} L{x+L} {y} L{x+L-11} {y+5}" fill="none" {st(stroke="fig")} stroke-width="1.6" vector-effect="non-scaling-stroke" opacity=".55"/>')
    o.append('<g data-stages="3 4">' + ''.join(wa) + '</g>')
    # distance ruler (stage 4)
    ru = [f'<line x1="{SMOKER_X}" y1="{GROUND-1}" x2="1160" y2="{GROUND-1}" {st(stroke="fig")} stroke-width="2" vector-effect="non-scaling-stroke"/>']
    for m in range(0, 10):
        x = SMOKER_X + m * 100
        big = m in (0, 1, 3, 6, 9)
        ru.append(f'<line x1="{x}" y1="{GROUND-(9 if big else 4)}" x2="{x}" y2="{GROUND+(9 if big else 4)}" {st(stroke="fig")} stroke-width="{2 if big else 1.2}" vector-effect="non-scaling-stroke"/>')
    o.append('<g data-stages="4">' + ''.join(ru) + '</g>')
    # rain clouds
    o.append(cloud(1600, 170, 560))
    o.append('<g data-stages="5">' + rain(1360, 1850, 205, GROUND, 58, 61) + '</g>')
    o.append(cloud(2860, 120, 640, stages="8 9 10"))
    o.append('<g data-stages="8 9 10">' + rain(2520, 3200, 175, GROUND, 80, 62) + '</g>')
    # trail
    trail = [TIP, MOUTH, (480, 352), (800, 330), (1240, 250), (1560, 232), (1700, 300), (1760, 360), (1900, 420), (2100, 440), (2330, 470),
             (2470, 520), (2632, 532), (2840, 528), (2990, 540), (3016, 600), (3060, 664), (3260, 640), (3420, 610)]
    o.append(f'<g data-stages="0 11 12"><path d="{catmull(trail)}" fill="none" {st(stroke="ember")} stroke-width="2.6" stroke-dasharray="7 7" vector-effect="non-scaling-stroke" stroke-linecap="round"/></g>')
    o.append('</g></svg>')
    return '\n'.join(o)


# ---------------------------------------------------------------- lenses

def zigzag(x0, y0, x1, y1, n, amp):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        if 0 < i < n:
            dx, dy = (y1 - y0), -(x1 - x0)
            L = math.hypot(dx, dy)
            s = amp * (1 if i % 2 else -1)
            x += dx / L * s
            y += dy / L * s
        pts.append(f"{f(x)} {f(y)}")
    return "M" + " L".join(pts)


def lens_svg():
    o = ['<svg viewBox="0 0 400 400" aria-hidden="true" focusable="false">',
         '''<defs>
  <radialGradient id="l-ember"><stop offset="0" stop-color="#fff4b8"/><stop offset=".4" stop-color="#ffb13b"/><stop offset=".75" stop-color="#e2531f"/><stop offset="1" stop-color="#b8361a"/></radialGradient>
  <radialGradient id="l-glow"><stop offset="0" stop-color="#ffb13b" stop-opacity=".9"/><stop offset="1" stop-color="#e2531f" stop-opacity="0"/></radialGradient>
  <radialGradient id="l-puff"><stop offset="0" style="stop-color:var(--smoke);stop-opacity:.8"/><stop offset="1" style="stop-color:var(--smoke);stop-opacity:0"/></radialGradient>
  <marker id="l-arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" style="fill:var(--ember)"/></marker>
  <marker id="l-arr2" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" style="fill:var(--muted)"/></marker>
</defs>''']
    # ---- cigarette
    c = ['<g class="lens-g" data-lens="cig">']
    cy = 215
    c.append(puffs(296, 196, 14, 71, (-10, 40), (-120, -150), (2.4, 3.6), (4, 6.5), 6, o=.7, grad='l-puff'))
    c.append(f'<rect x="50" y="{cy-20}" width="86" height="40" rx="5" {st(fill="filter")}/>')
    rnd = mulberry(4)
    c.append(''.join(f'<circle cx="{f(rnd.uniform(56,132))}" cy="{f(rnd.uniform(cy-16,cy+16))}" r="1.4" {st(fill="residue")} opacity=".45"/>' for _ in range(40)))
    c.append(f'<rect x="136" y="{cy-20}" width="146" height="40" {st(fill="paper", stroke="line")} stroke-width="1"/>')
    c.append(f'<path d="M282 {cy-20} l4 6 l-4 6 l5 6 l-5 6 l4 6 l-4 5 l3 5" {st(stroke="soil")} stroke-width="2.5" fill="none"/>')
    c.append(f'<circle class="glow" cx="300" cy="{cy}" r="44" fill="url(#l-glow)"/>')
    c.append(f'<rect x="284" y="{cy-19}" width="30" height="38" rx="7" fill="url(#l-ember)"/>')
    c.append(f'<path d="M313 {cy-17} L334 {cy-11} L334 {cy+11} L313 {cy+17} Z" {st(fill="ash")} opacity=".95"/>')
    c.append(f'<text x="93" y="{cy+4.5}" text-anchor="middle" class="t-s" opacity=".75">filter</text><text x="209" y="{cy+4.5}" text-anchor="middle" class="t-s" opacity=".75">tobacco rod</text>')
    c.append(f'<path class="flow" d="M282 {cy+28} L60 {cy+28}" {st(stroke="ember")} stroke-width="3" fill="none" marker-end="url(#l-arr)"/>')
    c.append(f'<path d="M352 {cy+44} Q336 {cy+30} 322 {cy+16}" {st(stroke="muted")} stroke-width="2" fill="none" marker-end="url(#l-arr2)"/><text x="350" y="{cy+62}" text-anchor="middle" class="t-m">air</text>')
    c.append(f'<text x="64" y="{cy+58}" class="t-b">Mainstream → mouth</text><text x="64" y="{cy+76}" class="t-m">pulled through during a puff</text>')
    c.append(f'<text x="200" y="{cy+112}" text-anchor="middle" class="t-b">Coal ≈900 °C in a puff</text><text x="200" y="{cy+130}" text-anchor="middle" class="t-m">≈400–800 °C between puffs</text>')
    c.append('<text x="96" y="104" class="t-b">Sidestream</text><text x="96" y="122" class="t-m">rises from the smouldering coal</text>')
    c.append('</g>')
    o += c
    # ---- lungs
    L = ['<g class="lens-g" data-lens="lung">']
    left = "M188 132 C150 122 98 160 94 232 C90 296 114 326 150 322 C178 318 186 290 186 262 Z"
    right = "M212 132 C250 122 302 160 306 232 C310 296 286 326 250 322 C222 318 214 290 214 262 Z"
    L.append(f'<path d="{left}" {st(fill="lung")}/><path d="{right}" {st(fill="lung")}/>')
    L.append(f'<rect x="192" y="50" width="16" height="90" rx="8" {st(fill="lung")}/>')
    br = "M200 136 L172 164 L150 200 M172 164 L160 236 M200 136 L228 164 L250 200 M228 164 L240 236 M150 200 L126 226 M250 200 L274 226"
    L.append(f'<path d="{br}" {st(stroke="ink")} stroke-width="3" fill="none" opacity=".22" stroke-linecap="round"/>')
    rnd = mulberry(8)
    dep = []
    for _ in range(70):
        side = rnd.choice((-1, 1))
        x = 200 + side * rnd.uniform(25, 95)
        y = rnd.uniform(170, 300)
        dep.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rnd.uniform(1.4,2.6))}" {st(fill="residue")} opacity=".8"/>')
    L.append(''.join(dep))
    paths = ["M200 20 L200 136 L172 164 L150 200 L126 226", "M200 20 L200 136 L172 164 L160 236", "M200 20 L200 136 L228 164 L250 200 L274 226", "M200 20 L200 136 L228 164 L240 236"]
    for i in range(12):
        p = paths[i % 4]
        L.append(f'<circle class="mover" r="3.2" style="fill:var(--smoke);offset-path:path(\'{p}\');--t:3.6s;--d:{-i*0.3:.2f}s"/>')
    L.append('<text x="200" y="352" text-anchor="middle" class="t-b">60–80% of particles stay</text><text x="200" y="370" text-anchor="middle" class="t-m">nicotine: 90–100%</text>')
    L.append('</g>')
    o += L
    # ---- particle sizes (to scale: 300 units = 1 um)
    S = ['<g class="lens-g" data-lens="size">']
    S.append('<text x="200" y="86" text-anchor="middle" class="t-b">Particle diameter, to scale</text>')
    for (x, d_um, a, b) in [(86, 0.10, "Fresh sidestream", "≈0.1 µm"), (200, 0.15, "Mainstream", "≈0.15–0.19 µm"), (312, 0.23, "Exhaled", "≈0.23 µm")]:
        r = d_um * 300 / 2
        S.append(f'<circle cx="{x}" cy="190" r="{f(r)}" {st(fill="smoke", stroke="ink")} stroke-width="1" fill-opacity=".75"/>')
        S.append(f'<text x="{x}" y="244" text-anchor="middle" class="t-s" style="font-weight:600">{a}</text><text x="{x}" y="261" text-anchor="middle" class="t-m">{b}</text>')
    S.append(f'<path d="M228 150 Q258 128 290 148" {st(stroke="ember")} stroke-width="2" fill="none" marker-end="url(#l-arr)"/><text x="258" y="122" text-anchor="middle" class="t-s" style="fill:var(--ember);font-weight:600">×1.5</text>')
    S.append(f'<line x1="50" y1="300" x2="350" y2="300" {st(stroke="ink")} stroke-width="2"/><line x1="50" y1="292" x2="50" y2="308" {st(stroke="ink")} stroke-width="2"/><line x1="350" y1="292" x2="350" y2="308" {st(stroke="ink")} stroke-width="2"/>')
    S.append('<text x="200" y="324" text-anchor="middle" class="t-s" style="font-weight:600">1 µm</text><text x="200" y="342" text-anchor="middle" class="t-m">PM2.5 counts particles up to 2.5 µm</text>')
    S.append('</g>')
    o += S
    # ---- raindrop scavenging
    D = ['<g class="lens-g" data-lens="drop">']
    D.append(f'<circle cx="200" cy="175" r="70" {st(fill="raindrop")} opacity=".9"/><ellipse cx="176" cy="148" rx="17" ry="10" {st(fill="gw-line")} opacity=".5"/>')
    lines = []
    for d in (-100, -44, 44, 100):
        s = 1 if d > 0 else -1
        bulge = 200 + s * max(abs(d), 80)
        p = f"M{200+d} 380 C{200+d} 300 {f(bulge)} 255 {f(bulge)} 175 C{f(bulge)} 95 {200+d} 50 {200+d} -20"
        lines.append(p)
        D.append(f'<path d="{p}" {st(stroke="muted")} stroke-width="1.3" fill="none" opacity=".5"/>')
    for i, p in enumerate(lines * 2):
        D.append(f'<circle class="mover" r="4" style="fill:var(--smoke);offset-path:path(\'{p}\');--t:4.2s;--d:{-i*0.55:.2f}s"/>')
    cpath = "M266 382 L236 237"
    D.append(f'<path d="{cpath}" {st(stroke="soil")} stroke-width="1.2" stroke-dasharray="3 4" fill="none" opacity=".7"/>')
    D.append(f'<circle class="mover" r="8" style="fill:var(--soil);offset-path:path(\'{cpath}\');--t:2.8s;--d:0s"/>')
    zp = zigzag(118, 382, 152, 226, 9, 9)
    D.append(f'<circle class="mover" r="2.4" style="fill:var(--ink);offset-path:path(\'{zp}\');--t:3.4s;--d:-1s"/>')
    D.append(f'<circle class="mover" r="2.4" style="fill:var(--ink);offset-path:path(\'{zp}\');--t:3.4s;--d:-2.6s"/>')
    D.append('<text x="200" y="68" text-anchor="middle" class="t-b">0.1–1 µm: slips past</text><text x="200" y="86" text-anchor="middle" class="t-m">follows the air around the drop</text>')
    D.append('<text x="118" y="292" text-anchor="middle" class="t-s" style="font-weight:600">&lt; 0.01 µm</text><text x="118" y="309" text-anchor="middle" class="t-m">diffuses in</text>')
    D.append('<text x="296" y="292" text-anchor="middle" class="t-s" style="font-weight:600">&gt; 2 µm</text><text x="296" y="309" text-anchor="middle" class="t-m">hits the drop</text>')
    D.append('</g>')
    o += D
    # ---- thirdhand chemistry
    T = ['<g class="lens-g" data-lens="ths">']
    T.append(f'<rect x="0" y="262" width="400" height="140" {st(fill="wall")}/><line x1="0" y1="262" x2="400" y2="262" {st(stroke="line")} stroke-width="2"/>')
    rnd = mulberry(17)
    for _ in range(36):
        T.append(f'<circle cx="{f(rnd.uniform(40,360))}" cy="{f(rnd.uniform(252,259))}" r="{f(rnd.uniform(3,4.5))}" {st(fill="residue")}/>')
    for x in (128, 172, 226):
        T.append(f'<circle class="pulse" cx="{x}" cy="250" r="6" {st(fill="ember")}/>')
    for i, x in enumerate((124, 170, 222)):
        p = f"M{x-30} 120 L{x} 244"
        T.append(f'<circle class="mover" r="4.5" style="fill:var(--rain);offset-path:path(\'{p}\');--t:3.2s;--d:{-i*1.05:.2f}s"/>')
    T.append(puffs(300, 246, 9, 81, (-20, 30), (-110, -150), (1.6, 2.6), (4, 6), 5, o=.7, grad='l-puff'))
    for i, x in enumerate((282, 318)):
        p = f"M{x+30} 70 L{x} 236"
        T.append(f'<g class="mover" style="offset-path:path(\'{p}\');--t:3.6s;--d:{-i*1.8:.2f}s"><circle r="3.4" cx="-4" {st(fill="rain")}/><circle r="3.4" cx="3" cy="-3" {st(fill="rain")}/><circle r="3.4" cx="3" cy="4" {st(fill="rain")}/></g>')
    T.append('<text x="70" y="150" class="t-b" style="fill:var(--rain)">+ HONO</text><text x="70" y="168" class="t-m">nitrous acid</text>')
    T.append('<text x="70" y="206" class="t-s" style="fill:var(--ember);font-weight:600">→ NNA, NNK</text>')
    T.append('<text x="330" y="108" text-anchor="end" class="t-b" style="fill:var(--rain)">+ O₃</text><text x="330" y="126" text-anchor="end" class="t-m">→ ultrafine particles</text>')
    T.append('<text x="200" y="296" text-anchor="middle" class="t-b">Nicotine sorbed on surfaces</text><text x="200" y="314" text-anchor="middle" class="t-m">re-emitted for days to months</text>')
    T.append('</g>')
    o += T
    # ---- butt
    B = ['<g class="lens-g" data-lens="butt">']
    B.append(f'<rect x="0" y="282" width="400" height="120" {st(fill="water")} opacity=".7"/><line x1="0" y1="282" x2="400" y2="282" {st(stroke="gw-line")} stroke-width="2" opacity=".8"/>')
    B.append(f'<rect x="72" y="136" width="186" height="50" rx="7" {st(fill="paper", stroke="line")} stroke-width="1"/>')
    for i in range(15):
        y = 140 + i * 3
        B.append(f'<path d="M150 {y} q14 -2 28 0 t28 0 t28 0 t22 0" {st(stroke="muted")} stroke-width=".9" fill="none" opacity=".5"/>')
    B.append(f'<rect x="72" y="136" width="80" height="50" rx="7" {st(fill="filter")}/>')
    rnd = mulberry(6)
    B.append(''.join(f'<circle cx="{f(rnd.uniform(78,148))}" cy="{f(rnd.uniform(140,182))}" r="1.4" {st(fill="residue")} opacity=".45"/>' for _ in range(30)))
    B.append(f'<rect x="196" y="137" width="62" height="48" {st(fill="residue")} opacity=".32"/>')
    B.append(f'<path d="M258 136 L280 140 L286 150 L280 160 L288 170 L280 182 L258 186 Z" {st(fill="soil")}/>')
    rnd = mulberry(10)
    for i in range(9):
        x = rnd.uniform(110, 270)
        tt = rnd.uniform(2.4, 3.6)
        B.append(f'<circle class="drop" cx="{f(x)}" cy="192" r="3" style="fill:var(--residue);--fy:{f(rnd.uniform(96,150))}px;--t:{tt:.2f}s;--d:{-rnd.uniform(0,tt):.2f}s"/>')
    B.append('<text x="200" y="104" text-anchor="middle" class="t-b">12,000–15,000 fibres</text><text x="200" y="122" text-anchor="middle" class="t-m">cellulose acetate, a plastic</text>')
    B.append('<text x="200" y="316" text-anchor="middle" class="t-b">nicotine · metals · PAHs</text><text x="200" y="334" text-anchor="middle" class="t-m">leach into the water</text>')
    B.append('</g>')
    o += B
    o.append('</svg>')
    return '\n'.join(o)


LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M9 25 C9 17 18 17 16 10 C15 6 18 4 21 3" fill="none" '
        'stroke="currentColor" stroke-width="2.4" stroke-linecap="round" opacity=".55"/><circle cx="9" cy="25" r="4.6" style="fill:var(--ember)"/>'
        '<circle cx="9" cy="25" r="2" fill="#ffd27a"/></svg>')

FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#182024"/>'
           '<path d="M10 24 C10 17 18 17 16.5 11 C15.6 7.4 18 5.5 21 4.5" fill="none" stroke="#b9c3c8" stroke-width="2.4" stroke-linecap="round"/>'
           '<circle cx="10" cy="24" r="4.8" fill="#e2531f"/><circle cx="10" cy="24" r="2.1" fill="#ffd27a"/></svg>')
