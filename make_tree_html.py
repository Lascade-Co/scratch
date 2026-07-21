#!/usr/bin/env python3
"""Render tree.json as a self-contained, zoomable SVG tree (horizontal layout).
Root at left; depth increases rightward; leaves stacked vertically.
Each node = a partial edge-weight assignment. Leaves are colour-coded by why
the branch was pruned."""
import json

d = json.load(open("tree.json"))
nodes = {n["id"]: n for n in d["nodes"]}
children = {int(k): v for k, v in d["children"].items()}
root = d["root"]

# depth of each node
depth = {}
def set_depth(nid, dp):
    depth[nid] = dp
    for c in children.get(nid, []):
        set_depth(c, dp + 1)
set_depth(root, 0)
maxdepth = max(depth.values())

# assign y by leaf order (post-order leaf sequence), internal = mean of children
ycoord = {}
leaf_counter = [0]
ROW = 20
def layout(nid):
    ch = children.get(nid, [])
    if not ch:
        ycoord[nid] = leaf_counter[0] * ROW
        leaf_counter[0] += 1
        return ycoord[nid]
    ys = [layout(c) for c in ch]
    ycoord[nid] = (ys[0] + ys[-1]) / 2
    return ycoord[nid]
layout(root)

COL = 150
MARGIN = 40
W = MARGIN * 2 + maxdepth * COL + 220
H = MARGIN * 2 + leaf_counter[0] * ROW

def color(note):
    if note.startswith("prune:dup"):
        return "#d9822b"       # orange  - duplicate geodesic value
    if note.startswith("prune:5-win"):
        return "#c0392b"       # red     - length-5 window < 35
    if note.startswith("prune:win"):
        return "#8e44ad"       # purple  - window > 50
    if note == "SOLUTION":
        return "#27ae60"
    if note == "full-but-no-match":
        return "#7f8c8d"
    return "#2c7fb8"           # blue    - internal expand / root

def x(nid):
    return MARGIN + depth[nid] * COL

edges = []
circles = []
labels = []
for nid, n in nodes.items():
    nx, ny = x(nid), ycoord[nid] + MARGIN
    for c in children.get(nid, []):
        cx, cy = x(c), ycoord[c] + MARGIN
        edges.append(f'<path d="M{nx+6},{ny} C{nx+COL/2},{ny} {cx-COL/2},{cy} {cx-6},{cy}" '
                     f'fill="none" stroke="#ccc" stroke-width="1"/>')
    leaf = not children.get(nid)
    r = 6 if not leaf else 5
    circles.append(f'<circle cx="{nx}" cy="{ny}" r="{r}" fill="{color(n["note"])}"/>')
    if n["id"] == root:
        txt = "w0=1 (root)"
    elif n["val"] is not None:
        txt = f'p{n["pos"]}={n["val"]}'
    else:
        txt = n["note"]
    extra = ""
    if leaf and n["note"].startswith("prune"):
        extra = "  [" + n["note"].split(":", 1)[1] + "]"
    labels.append(f'<text x="{nx+9}" y="{ny+3.5}" font-size="10" '
                  f'font-family="monospace" fill="#222">{txt}{extra}</text>')

svg = f'''<svg id="tree" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<rect width="{W}" height="{H}" fill="white"/>
{''.join(edges)}
{''.join(circles)}
{''.join(labels)}
</svg>'''

html = f'''<title>C10 geodesic-labeling search tree</title>
<style>
  body{{margin:0;font-family:system-ui,sans-serif;background:#fafafa;color:#222}}
  header{{padding:14px 18px;border-bottom:1px solid #ddd;background:#fff;position:sticky;top:0;z-index:5}}
  h1{{font-size:16px;margin:0 0 4px}}
  .sub{{font-size:12px;color:#555}}
  .legend{{margin-top:8px;font-size:12px;display:flex;gap:16px;flex-wrap:wrap}}
  .legend span{{display:inline-flex;align-items:center;gap:5px}}
  .dot{{width:11px;height:11px;border-radius:50%;display:inline-block}}
  #wrap{{overflow:auto;height:calc(100vh - 120px);cursor:grab}}
  @media (prefers-color-scheme: dark){{
    body{{background:#111;color:#eee}} header{{background:#181818;border-color:#333}}
    .sub{{color:#aaa}} #tree rect{{fill:#181818}}
    #tree text{{fill:#ddd!important}} #tree path{{stroke:#444!important}}
  }}
</style>
<header>
  <h1>Ring C₁₀ geodesic-labeling — full search tree (necessary-condition pruning)</h1>
  <div class="sub">384 nodes · root fixes w₀=1 · every leaf is a dead end · <b>0 solutions</b>. Each node = "position = value tried". Scroll / drag to pan.</div>
  <div class="legend">
    <span><i class="dot" style="background:#2c7fb8"></i>expand (valid so far)</span>
    <span><i class="dot" style="background:#d9822b"></i>prune: duplicate geodesic value</span>
    <span><i class="dot" style="background:#8e44ad"></i>prune: window &gt; 50</span>
    <span><i class="dot" style="background:#c0392b"></i>prune: length-5 window &lt; 35</span>
  </div>
</header>
<div id="wrap">{svg}</div>
<script>
  const wrap=document.getElementById('wrap');
  let down=false,sx,sy,sl,st;
  wrap.addEventListener('mousedown',e=>{{down=true;sx=e.pageX;sy=e.pageY;sl=wrap.scrollLeft;st=wrap.scrollTop;wrap.style.cursor='grabbing';}});
  window.addEventListener('mouseup',()=>{{down=false;wrap.style.cursor='grab';}});
  window.addEventListener('mousemove',e=>{{if(!down)return;wrap.scrollLeft=sl-(e.pageX-sx);wrap.scrollTop=st-(e.pageY-sy);}});
</script>'''

open("search_tree.html", "w").write(html)
print("wrote search_tree.html  size:", W, "x", H)
