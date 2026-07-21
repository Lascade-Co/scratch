#!/usr/bin/env python3
"""Generalize the geodesic-labeling question to a ring C_n.

For C_n let m = floor(n/2). The geodesics are exactly all cyclic windows of
length 1..m (for even n, both antipodal m-arcs count, which is simply all n
windows of length m). So:

    #geodesics        G = n * m
    target value set  {1, ..., G},  target sum = G(G+1)/2
    each edge lies in  c = 1+2+...+m = m(m+1)/2  windows
    => required edge-sum  S = [G(G+1)/2] / c      (must be a positive integer)

Necessary condition (integrality):  c | G(G+1)/2.
"""

def analyze(n):
    m = n // 2
    G = n * m
    tot = G * (G + 1) // 2
    c = m * (m + 1) // 2
    integral = (tot % c == 0)
    S = tot / c
    return m, G, tot, c, integral, S

print(f"{'n':>3} {'m':>2} {'#geo G':>7} {'sum(1..G)':>10} {'cover c':>8} "
      f"{'S=sum/c':>10} {'integer?':>9}")
for n in range(3, 21):
    m, G, tot, c, integral, S = analyze(n)
    print(f"{n:>3} {m:>2} {G:>7} {tot:>10} {c:>8} "
          f"{(str(int(S)) if integral else f'{S:.3f}'):>10} "
          f"{('YES' if integral else 'no'):>9}")

print()
m, G, tot, c, integral, S = analyze(11)
print(f"n=11:  G={G} geodesics, target sum={tot}, coverage c={c} per edge.")
print(f"       S = {tot}/{c} = {tot/c:.4f}  ->  NOT an integer.")
print("       => C_11 is impossible by the integrality (divisibility) condition;")
print("          no search required.")
