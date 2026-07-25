#!/usr/bin/env python3
"""Estimate the size of the deterministic K(5,5) backtracking tree.

Knuth (1975) random-probing estimator: take random dives from the root; at a
node with d viable children pick one uniformly and multiply a running weight by
d. The sum of weights over a dive is an unbiased estimator of the total number
of nodes; averaging many dives converges to the true tree size. Also estimates
the number of solution leaves.

Uses the EXACT pruning of the deterministic search (k55.c / search_k55.py):
row0 & col0 increasing, transpose break, entries<=117, pair-sums<=125 distinct,
entry-sum<=875 with future-reachability bound. Optional x00=1 fix.
"""
import random, sys, math

N=5; M=125; EMAX=117; SUM=875
FIX00 = "--fix00" in sys.argv

def future_ok(used, rem, esum):
    need = SUM - esum
    lo=c=0; v=1
    while c<rem and v<=M:
        if not used[v]: lo+=v; c+=1
        v+=1
    if c<rem: return False
    hi=c=0; v=M
    while c<rem and v>=1:
        if not used[v]: hi+=v; c+=1
        v-=1
    return lo<=need<=hi

def viable(g, used, t, esum):
    """list of candidate values that WOULD be expanded at cell t."""
    i,k=divmod(t,N)
    lo=1
    if i==0 and k>0: lo=g[t-1]+1
    if k==0 and i>0: lo=g[(i-1)*N]+1
    if t==5: lo=max(lo,g[1]+1)
    if FIX00 and t==0: return [1]
    out=[]; base=i*N; rem=24-t
    for v in range(lo, EMAX+1):
        if used[v] or esum+v>SUM: continue
        ok=True; adds=[v]; used[v]=1
        for c in range(k):
            s=v+g[base+c]
            if s>M or used[s]: ok=False; break
            used[s]=1; adds.append(s)
        if ok:
            for r in range(i):
                s=v+g[r*N+k]
                if s>M or used[s]: ok=False; break
                used[s]=1; adds.append(s)
        if ok and rem and not future_ok(used, rem, esum+v): ok=False
        for a in adds: used[a]=0
        if ok: out.append(v)
    return out

def dive():
    g=[0]*25; used=bytearray(M+1)
    esum=0; w=1.0; total=0.0; sols=0.0
    t=0
    while True:
        total += w                        # count this node
        if t==25:
            if esum==SUM and all(used[1:M+1]): sols += w
            break
        cs = viable(g, used, t, esum)
        d = len(cs)
        if d==0: break
        v = random.choice(cs)
        # apply v
        i,k=divmod(t,N); base=i*N
        used[v]=1
        for c in range(k): used[v+g[base+c]]=1
        for r in range(i): used[v+g[r*N+k]]=1
        g[t]=v; esum+=v; w*=d; t+=1
    return total, sols

if __name__=="__main__":
    trials = int(sys.argv[sys.argv.index("-n")+1]) if "-n" in sys.argv else 200000
    random.seed(12345)
    s=0.0; s2=0.0; sols=0.0; maxd=0
    for _ in range(trials):
        tot, sl = dive()
        s+=tot; s2+=tot*tot; sols+=sl
    mean=s/trials
    var=max(0.0, s2/trials-mean*mean)
    se=math.sqrt(var/trials)
    print(f"fix00={FIX00}  trials={trials:,}")
    print(f"estimated deterministic tree size ~ {mean:.3e}  nodes  (+/- {se:.1e} SE)")
    print(f"estimated # solution leaves        ~ {sols/trials:.3e}")
    for rate in (3e7, 1e8, 3e8):
        secs = mean/rate
        print(f"  at {rate:.0e} nodes/s  ->  {secs:.3e} s  = {secs/86400:.3e} days"
              f" = {secs/86400/365:.3e} yr")
