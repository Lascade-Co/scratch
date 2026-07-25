#!/usr/bin/env python3
"""Randomized-restart backtracking finder for K(5,5).
Same pruning as the exhaustive search, but value order is shuffled and the
search restarts after a node budget, to sample different regions of the tree.
A success prints the grid; this can only prove existence, not non-existence."""
import random

N = 5; S_TARGET = 875; VMAX = 125; EMAX = 117   # entries <= 117 (K3)
RESTART_NODES = 3_000_000

def future_bounds(used, remaining):
    lo=cnt=0; v=1
    while cnt<remaining and v<=VMAX:
        if not used[v]: lo+=v; cnt+=1
        v+=1
    if cnt<remaining: return (1,-1)
    hi=cnt=0; v=VMAX
    while cnt<remaining and v>=1:
        if not used[v]: hi+=v; cnt+=1
        v-=1
    return (lo,hi)

def attempt(seed):
    random.seed(seed)
    g=[0]*25; used=bytearray(VMAX+1); nodes=[0]; best=[0]
    def rec(t,esum):
        nodes[0]+=1
        if nodes[0] > RESTART_NODES: raise TimeoutError
        if t>best[0]: best[0]=t
        if t==25:
            return esum==S_TARGET and all(used[1:VMAX+1])
        i,k=divmod(t,N)
        lo=1
        if i==0 and k>0: lo=g[t-1]+1
        if k==0 and i>0: lo=g[(i-1)*N]+1
        if t==5: lo=max(lo,g[1]+1)
        cands=[v for v in range(lo, EMAX+1) if not used[v] and esum+v<=S_TARGET]
        random.shuffle(cands)
        rem=24-t
        for v in cands:
            adds=[v]; used[v]=1; ok=True
            base=i*N
            for c in range(k):
                s=v+g[base+c]
                if s>VMAX or used[s]: ok=False;break
                used[s]=1; adds.append(s)
            if ok:
                for r in range(i):
                    s=v+g[r*N+k]
                    if s>VMAX or used[s]: ok=False;break
                    used[s]=1; adds.append(s)
            if ok and rem:
                fmin,fmax=future_bounds(used,rem); need=S_TARGET-esum-v
                if fmax<0 or need<fmin or need>fmax: ok=False
            if ok:
                g[t]=v
                if rec(t+1,esum+v):
                    for a in adds: used[a]=0
                    return True
                g[t]=0
            for a in adds: used[a]=0
        return False
    try:
        if rec(0,0):
            return g[:], best[0]
    except TimeoutError:
        pass
    return None, best[0]

if __name__=="__main__":
    best_overall=0
    for seed in range(1,100000):
        sol,depth=attempt(seed)
        if depth>best_overall:
            best_overall=depth
            print(f"seed {seed}: best depth reached = {depth}/25", flush=True)
        if sol:
            print("SOLUTION FOUND:")
            for r in range(N):
                print("  ", sol[r*N:(r+1)*N])
            break
