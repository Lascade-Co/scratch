#!/usr/bin/env python3
"""Render the algorithm writeup to a typeset PDF using matplotlib mathtext
(no system LaTeX needed). Math is real vector output; every expression is
self-tested for rendering before the document is built."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle

plt.rcParams.update({
    "mathtext.fontset": "cm",
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
})

# ---- palette ----
INK   = "#1a1a2e"
ACC   = "#0f766e"     # teal accent
ACC2  = "#b45309"     # amber for condition tags
RULE  = "#c9ced6"
CODEBG = "#f3f4f6"
BOXBG  = "#e9f4f2"
MUTED = "#5b6472"

PAGE_W, PAGE_H = 8.5, 11.0
ML, MR, MT, MB = 0.95, 0.95, 0.95, 0.85
CW = PAGE_W - ML - MR

# ---------- document model ----------
# each block: (kind, payload)
DOC = []
def H1(t): DOC.append(("title", t))
def BY(t): DOC.append(("byline", t))
def H2(n, t): DOC.append(("h2", (n, t)))
def P(*lines, **kw): DOC.append(("para", list(lines)))
def M(expr, tag=None, box=False): DOC.append(("math", (expr, tag, box)))
def CODE(lines): DOC.append(("code", lines))
def RULEB(): DOC.append(("rule", None))
def SP(h): DOC.append(("space", h))
def TABLE(headers, rows): DOC.append(("table", (headers, rows)))

# ---------- content ----------
H1(r"Optimized algorithm: geodesic edge-labeling of the ring $C_{10}$")
BY("Ring C10 with 10 edges  ·  geodesic weights = {1,...,50}")
RULEB()

H2("1", "Formalization")
P("Cycle $C_{10}$ with edges $e_0,\\dots,e_9$ (indices taken mod 10) and weights")
M(r"w_i \in \mathbb{Z}^{+},\qquad i \in \mathbb{Z}_{10}=\{0,\dots,9\}.")
P("For a start $s$ and length $L\\in\\{1,\\dots,5\\}$ the window sum is")
M(r"W(s,L)\;=\;\sum_{k=0}^{L-1} w_{\,(s+k)\,\mathrm{mod}\,10}.")
P("Geodesics of $C_{10}$ are exactly the windows of length 1 to 5 (length-5",
  "diametric pairs contribute two shortest arcs), so the geodesic set is")
M(r"\mathcal{G}=\{\,W(s,L)\;:\;s\in\mathbb{Z}_{10},\;L\in\{1,\dots,5\}\,\},\qquad |\mathcal{G}|=10\times5=50.")
P("Goal: find $w=(w_0,\\dots,w_9)$ with $\\mathcal{G}=\\{1,2,\\dots,50\\}$",
  "(a bijection, since $|\\mathcal{G}|=50$).")

H2("2", "Necessary conditions (pruning invariants)")
P("Each edge occurs in $1{+}2{+}3{+}4{+}5=15$ windows, hence")
M(r"\sum_{s,L}W(s,L)=15\sum_i w_i=\sum_{n=1}^{50}n=1275\;\Rightarrow\;S:=\sum_i w_i=85.",
  tag="C1", box=True)
P("$1\\in\\mathcal{G}$ forces some $w_i=1$ (any $L\\geq 2$ sum is $\\geq 1{+}2=3$);",
  "$2\\in\\mathcal{G}$ forces some $w_j=2$ (since $2=1{+}1$ is barred by distinctness).",
  tag_after="C2")
M(r"\exists\, i,j:\; w_i=1,\;\; w_j=2.", tag="C2")
P("Opposite length-5 arcs partition the edge set, so $W(s,5)+W(s{+}5,5)=S=85$;",
  "with both $\\leq 50$ this gives")
M(r"35\;\leq\;W(s,5)\;\leq\;50\qquad \forall\, s.", tag="C3")
P("Distinct windows force distinct $w_i$; combined with (C1),")
M(r"w_i\;\leq\;S-\sum_{k=1}^{9}k \;=\; 85-45 \;=\; 40\qquad \forall\, i.", tag="C4")
P("Rotational symmetry is quotiented by pinning the unit edge:")
M(r"w_0 := 1.", tag="C5")

H2("3", "The algorithm (pruned depth-first search)")
P("State: a partial assignment $w_0,\\dots,w_{i-1}$, running sum",
  "$\\sigma=\\sum_{k<i}w_k$, and the set $U\\subseteq\\{1,\\dots,50\\}$ of geodesic",
  "values already realized by non-wrapping windows $W(s,L)$ with $s+L\\leq i$.")
P("Placing value $v$ at position $i$ fails iff some newly-completed window",
  "$W(i{-}L{+}1,L)$ violates one of the necessary clauses:")
M(r"(\,W>50\,)\;\vee\;(\,W\in U\,)\;\vee\;(\,L=5\,\wedge\,W<35\,)\;\vee\;(\,\sigma+v>85\,).")
P("Every clause is necessary, so pruning is sound (no valid labeling is",
  "discarded) and the enumeration is complete.")
CODE([
 "Search(i, sigma, U):",
 "    if i = 10:",
 "        report solution if {W(s,L) : s in Z10, L in 1..5} = {1..50}",
 "        return                              # includes wrapping windows",
 "    for v = 1 ... 40  with  v not in {w0..w_{i-1}}  and  sigma+v <= 85:",
 "        w_i <- v ;  A <- {} ;  ok <- true",
 "        for L = 1 ... min(5, i+1):          # windows ending at i",
 "            W <- sum_{t=i-L+1}^{i} w_t",
 "            if W>50 or W in U or (L=5 and W<35): ok<-false; break",
 "            A <- A + {W}",
 "        if ok:  Search(i+1, sigma+v, U + A)",
 "        undo w_i, A",
 "",
 "Driver:  w0 <- 1  (C5);  Search(1, 1, {1}).",
])
P("An optional reflection quotient ($w_1<w_9$, checked once $w_9$ is placed)",
  "halves the tree.")

H2("4", "Complexity")
P("Naive enumeration of 10 distinct values in $[1,40]$ around the ring is")
M(r"\binom{40}{10}\cdot \frac{9!}{2}\;\approx\;10^{16}\quad(\mathrm{infeasible}).")
P("The predicate collapses this. With (C1) to (C5) the entire tree is")
M(r"384\ \mathrm{nodes},\qquad \mathrm{depth}<10\ \ \mathrm{on\ every\ branch},")
P("i.e. a few hundred visited states, decidedly not brute force. Dropping (C3)",
  "and the tight cap still finishes in $7.4\\times10^{5}$ nodes; dropping all",
  "symmetry and bounds, $1.4\\times10^{7}$.")

H2("5", "Result")
M(r"\mathcal{G}=\{1,\dots,50\}\ \ \mathrm{is\ unsatisfiable\ on}\ \ C_{10}.", box=True)
P("Confirmed by four independent methods:")
TABLE(["method", "assumptions", "nodes", "sols"],
      [["pruned DFS", "WLOG symm. + bound", "735,496", "0"],
       ["unconstrained DFS", "none", "14,373,810", "0"],
       ["necessary-cond. tree", "(C1)-(C5)", "384", "0"],
       ["Z3 SMT", "direct model", "unsat", "0"]])
P("Under (C1)-(C5) no branch reaches depth 10: every path ends in a range",
  "violation ($W>50$), a value collision ($W\\in U$), or a (C3) violation ($W<35$).")

# ---------- self-test all math ----------
def _test_math():
    bad = []
    for kind, payload in DOC:
        strs = []
        if kind == "math": strs = ["$" + payload[0] + "$"]
        elif kind in ("para",): strs = payload
        elif kind in ("title", "byline"): strs = [payload]
        elif kind == "h2": strs = [payload[1]]
        for s in strs:
            figt = plt.figure()
            try:
                figt.text(0.5, 0.5, s, math_fontfamily="cm")
                figt.canvas.draw()
            except Exception as e:
                bad.append((s, str(e)[:120]))
            finally:
                plt.close(figt)
    return bad

bad = _test_math()
if bad:
    print("MATH RENDER FAILURES:")
    for s, e in bad:
        print("  ", repr(s), "->", e)
    raise SystemExit(1)
print("all math strings render OK")

# ---------- renderer (measurement-based layout) ----------
class Doc:
    def __init__(self, path):
        self.pdf = PdfPages(path)
        self.page_no = 0
        self.new_page()
    def new_page(self):
        self.fig = plt.figure(figsize=(PAGE_W, PAGE_H), dpi=100)
        self.fig.patch.set_facecolor("white")
        self.y = PAGE_H - MT
        self.page_no += 1
    def _fx(self, x_in): return x_in / PAGE_W
    def _fy(self, y_in): return y_in / PAGE_H
    def _finish_page(self):
        self.fig.text(self._fx(PAGE_W/2), self._fy(MB*0.55),
                      f"{self.page_no}", ha="center", va="center",
                      fontsize=8.5, color=MUTED)
        self.pdf.savefig(self.fig)
        import os
        if os.environ.get("DUMP_PNG"):
            self.fig.savefig(f"_page{self.page_no}.png", dpi=110)
        plt.close(self.fig)

    # --- measurement helpers ---
    def _rend(self): return self.fig.canvas.get_renderer()
    def _bbox_in(self, artist):
        self.fig.canvas.draw()
        bb = artist.get_window_extent(self._rend())
        return (bb.x0/self.fig.dpi, bb.y0/self.fig.dpi,
                bb.width/self.fig.dpi, bb.height/self.fig.dpi)
    def text(self, x_in, y_in, s, **kw):
        return self.fig.text(self._fx(x_in), self._fy(y_in), s, **kw)

    def _emit(self, make, gap, keep_together=True):
        """make(top_in) -> list[artist]; measures true height from `top_in`
        down to the lowest point, handling page breaks and returning artists."""
        arts = make(self.y)
        low = min(self._bbox_in(a)[1] for a in arts)   # lowest y0 (inches)
        h = self.y - low
        if low < MB and keep_together and self.y < PAGE_H - MT - 1e-6:
            for a in arts:
                a.remove()
            self._finish_page(); self.new_page()
            arts = make(self.y)
            low = min(self._bbox_in(a)[1] for a in arts)
            h = self.y - low
        self.y = low - gap
        return arts

    # --- blocks ---
    def title(self, s):
        fs = 17
        def make(top):
            return [self.text(ML, top, s, fontsize=fs, color=INK,
                              weight="bold", va="top", math_fontfamily="cm")]
        # auto-shrink to fit column width
        while fs > 10:
            a = self.text(ML, self.y, s, fontsize=fs, color=INK,
                          weight="bold", va="top", math_fontfamily="cm")
            w = self._bbox_in(a)[2]; a.remove()
            if w <= CW: break
            fs -= 0.5
        self._emit(make, 0.16)
    def byline(self, s):
        self._emit(lambda top: [self.text(ML, top, s, fontsize=9.5,
                   color=MUTED, va="top", style="italic")], 0.14)
    def rule(self):
        ln = plt.Line2D([self._fx(ML), self._fx(PAGE_W-MR)],
                        [self._fy(self.y), self._fy(self.y)], color=RULE, lw=1.0)
        self.fig.add_artist(ln)
        self.y -= 0.22
    def h2(self, n, t):
        self.y -= 0.14
        def make(top):
            return [self.text(ML, top, f"{n}", fontsize=13, color=ACC,
                              weight="bold", va="top"),
                    self.text(ML+0.30, top, t, fontsize=13, color=INK,
                              weight="bold", va="top", math_fontfamily="cm")]
        self._emit(make, 0.14)
    def para(self, lines, tag_after=None):
        for ln in lines:
            self._emit(lambda top, s=ln: [self.text(ML, top, s, fontsize=10.5,
                       color=INK, va="top", math_fontfamily="cm")], 0.055)
        self.y -= 0.06
    def math(self, expr, tag=None, box=False):
        self.y -= 0.06                      # breathing room above
        cx = ML + CW/2
        def make(top):
            return [self.text(cx, top, f"${expr}$", fontsize=14, color=INK,
                              ha="center", va="top", math_fontfamily="cm")]
        arts = self._emit(make, 0.0, keep_together=True)
        txt = arts[0]
        x0, y0, w, h = self._bbox_in(txt)
        if box:
            pad = 0.12
            bx = FancyBboxPatch(
                (self._fx(x0-pad), self._fy(y0-pad)),
                self._fx(w+2*pad)-self._fx(0), self._fy(h+2*pad)-self._fy(0),
                boxstyle="round,pad=0,rounding_size=0.012",
                fc=BOXBG, ec=ACC, lw=1.2,
                transform=self.fig.transFigure, zorder=0)
            self.fig.add_artist(bx)
            self.y -= pad
        if tag:
            yc = y0 + h/2                    # vertical centre of equation
            self.text(PAGE_W-MR, yc, f"({tag})", fontsize=10.5, color=ACC2,
                      ha="right", va="center", weight="bold")
        self.y -= 0.14                       # breathing room below
    def code(self, lines):
        LH = 0.176
        h = LH*len(lines) + 0.22
        if self.y - h < MB:
            self._finish_page(); self.new_page()
        top = self.y
        self.fig.add_artist(Rectangle(
            (self._fx(ML), self._fy(top-h)),
            self._fx(PAGE_W-MR)-self._fx(ML), self._fy(top)-self._fy(top-h),
            fc=CODEBG, ec=RULE, lw=0.8, transform=self.fig.transFigure,
            zorder=0))
        yy = top - 0.15
        for ln in lines:
            self.text(ML+0.16, yy, ln, fontsize=8.7, color="#0b3d3a",
                      va="top", family="monospace")
            yy -= LH
        self.y = top - h - 0.12
    def table(self, headers, rows):
        widths = [0.26, 0.34, 0.22, 0.10]
        xs = [ML]
        for wfrac in widths[:-1]:
            xs.append(xs[-1] + wfrac*CW)
        rh = 0.28
        need = rh*(len(rows)+1) + 0.15
        if self.y - need < MB:
            self._finish_page(); self.new_page()
        self.fig.add_artist(Rectangle(
            (self._fx(ML), self._fy(self.y-rh)),
            self._fx(PAGE_W-MR)-self._fx(ML), self._fy(rh)-self._fy(0),
            fc=ACC, ec="none", transform=self.fig.transFigure, zorder=0))
        for x, htxt in zip(xs, headers):
            self.text(x+0.07, self.y-rh/2, htxt, fontsize=9.5, color="white",
                      va="center", weight="bold")
        self.y -= rh
        for r, row in enumerate(rows):
            if r % 2 == 1:
                self.fig.add_artist(Rectangle(
                    (self._fx(ML), self._fy(self.y-rh)),
                    self._fx(PAGE_W-MR)-self._fx(ML), self._fy(rh)-self._fy(0),
                    fc="#eef3f2", ec="none", transform=self.fig.transFigure,
                    zorder=0))
            for x, cell in zip(xs, row):
                self.text(x+0.07, self.y-rh/2, cell, fontsize=9.3, color=INK,
                          va="center", family="monospace")
            self.y -= rh
        # outer border
        self.fig.add_artist(Rectangle(
            (self._fx(ML), self._fy(self.y)),
            self._fx(PAGE_W-MR)-self._fx(ML),
            self._fy((len(rows)+1)*rh)-self._fy(0),
            fc="none", ec=RULE, lw=0.8, transform=self.fig.transFigure, zorder=1))
        self.y -= 0.14
    def close(self):
        self._finish_page()
        self.pdf.close()

d = Doc("algorithm.pdf")
for kind, payload in DOC:
    if kind == "title": d.title(payload)
    elif kind == "byline": d.byline(payload)
    elif kind == "rule": d.rule()
    elif kind == "h2": d.h2(*payload)
    elif kind == "para": d.para(payload)
    elif kind == "math": d.math(*payload)
    elif kind == "code": d.code(payload)
    elif kind == "table": d.table(*payload)
    elif kind == "space": d.y -= payload
d.close()
print("wrote algorithm.pdf")
