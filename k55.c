/* K(5,5) geodesic labeling search (fast C).
   Fill a 5x5 grid with distinct positive ints so that the 25 entries plus the
   100 rook-adjacent pairwise sums are exactly {1..125}.
   Modes:  ./k55 det    deterministic exhaustive (if it finishes, it is proof)
           ./k55 rand   randomized-restart finder (200M nodes/restart)         */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define N 5
#define M 125
#define EMAX 117      /* K3: no entry can exceed 117           */
#define SUM 875       /* K1: sum of entries                    */

static char used[M+1];
static int  g[25];
static long long nodes = 0;
static long long cap;           /* per-restart node cap (rand mode) */
static int randomized;

static inline int future_ok(int rem, int esum){
    int need = SUM - esum;
    int lo=0,c=0;
    for(int v=1; v<=M && c<rem; v++) if(!used[v]){ lo+=v; c++; }
    if(c<rem) return 0;
    int hi=0; c=0;
    for(int v=M; v>=1 && c<rem; v--) if(!used[v]){ hi+=v; c++; }
    return need>=lo && need<=hi;
}

/* returns 1=solution found, -1=hit node cap (rand), 0=subtree exhausted */
static int rec(int t, int esum){
    if(((++nodes) & 0x3FFFFFFF)==0){                 /* ~1.07e9 */
        fprintf(stderr,"  nodes=%lld  grid=",nodes);
        for(int i=0;i<25;i++) fprintf(stderr,"%d,",g[i]);
        fprintf(stderr,"\n"); fflush(stderr);
    }
    if(randomized && nodes>cap) return -1;
    if(t==25){
        if(esum!=SUM) return 0;
        for(int v=1; v<=M; v++) if(!used[v]) return 0;
        return 1;
    }
    int i=t/N, k=t%N;
    int lo=1;
    if(i==0 && k>0) lo=g[t-1]+1;          /* row 0 increasing         */
    if(k==0 && i>0) lo=g[(i-1)*N]+1;      /* col 0 increasing         */
    if(t==5){ int x=g[1]+1; if(x>lo) lo=x; }   /* transpose break     */

    int cand[128], nc=0;
    for(int v=lo; v<=EMAX; v++)
        if(!used[v] && esum+v<=SUM) cand[nc++]=v;
    if(randomized)
        for(int j=nc-1;j>0;j--){ int r=rand()%(j+1),tmp=cand[j];cand[j]=cand[r];cand[r]=tmp; }

    int rem=24-t, base=i*N;
    for(int idx=0; idx<nc; idx++){
        int v=cand[idx], adds[16], na=0, ok=1;
        used[v]=1; adds[na++]=v;
        for(int c=0;c<k && ok;c++){ int s=v+g[base+c];
            if(s>M||used[s]) ok=0; else { used[s]=1; adds[na++]=s; } }
        if(ok) for(int r=0;r<i && ok;r++){ int s=v+g[r*N+k];
            if(s>M||used[s]) ok=0; else { used[s]=1; adds[na++]=s; } }
        if(ok && rem){ if(!future_ok(rem, esum+v)) ok=0; }
        if(ok){
            g[t]=v;
            int res=rec(t+1, esum+v);
            if(res!=0){ for(int a=0;a<na;a++) used[adds[a]]=0; return res; }
            g[t]=0;
        }
        for(int a=0;a<na;a++) used[adds[a]]=0;
    }
    return 0;
}

int main(int argc, char**argv){
    randomized = (argc>1 && strcmp(argv[1],"rand")==0);
    if(!randomized){
        cap = 0;
        memset(used,0,sizeof(used)); memset(g,0,sizeof(g)); nodes=0;
        int res=rec(0,0);
        if(res==1){
            printf("SOLUTION FOUND (deterministic):\n");
            for(int r=0;r<N;r++){ for(int c=0;c<N;c++) printf("%4d",g[r*N+c]); printf("\n"); }
        } else {
            printf("EXHAUSTED after %lld nodes: NO SOLUTION EXISTS for K(5,5).\n",nodes);
        }
    } else {
        cap = 200000000LL;
        for(int seed=1; seed<100000; seed++){
            srand(seed);
            memset(used,0,sizeof(used)); memset(g,0,sizeof(g)); nodes=0;
            int res=rec(0,0);
            if(res==1){
                printf("SOLUTION FOUND (rand seed %d):\n",seed);
                for(int r=0;r<N;r++){ for(int c=0;c<N;c++) printf("%4d",g[r*N+c]); printf("\n"); }
                fflush(stdout); return 0;
            }
            printf("seed %d: %s, nodes=%lld\n", seed,
                   (res==0?"EXHAUSTED (no sol in this order)":"cap"), nodes);
            fflush(stdout);
        }
        printf("no solution found across restarts\n");
    }
    return 0;
}
