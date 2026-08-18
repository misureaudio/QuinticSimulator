# Targeted A6 sextic finder (fast prefilter + confirm).
# A6 (order 360, degree 6, solvable=False) lies in A6 => square discriminant.
# Its degree-6 action contains 5-cycles (5,1) and double 3-cycles (3,3), but no
# 6-cycles, no single 4-cycles, no transpositions. Distinguishing from the
# transitive A5 (order 60): A5 has single 3-cycles (3,1,1,1) but NOT (3,3).
# Prefilter: irreducible + square disc + a (5,1) pattern + a (3,3) pattern.
from math import isqrt
R.<x> = QQ[]
P = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59]

def is_square(n):
    n=int(n)
    if n<0: return False
    r=isqrt(n); return r*r==n

def frob(f,p):
    fp=f.change_ring(GF(p))
    if fp==0: return None
    try: fac=fp.factor()
    except Exception: return None
    degs=[]; ok=True
    for c,e in fac:
        if e>1: ok=False; break
        degs.append(int(c.degree()))
    return tuple(sorted(degs,reverse=True)) if ok else None

def ggroup(f):
    g=f.galois_group()
    if isinstance(g,tuple): g=g[0]
    return g

pool=[]
for a in range(-4,5):
    for b in range(-4,5):
        for c in range(-4,5):
            for d in range(-4,5):
                for e in range(-4,5):
                    pool.append(x^6 + a*x^4 + b*x^3 + c*x^2 + d*x + e)
for a in range(-8,9):
    for b in range(-8,9):
        for c in range(-8,9):
            pool.append(x^6 + a*x^3 + b*x + c)

seen=set(); hits=[]; checked=0
for f in pool:
    if f in seen: continue
    seen.add(f)
    if not f.is_irreducible(): continue
    if not is_square(f.discriminant()): continue
    # need a (5,1) and a (3,3)
    has5=has33=False
    for p in P:
        c=frob(f,p)
        if c is None: continue
        if c==(5,1): has5=True
        if c==(3,3): has33=True
        if has5 and has33: break
    if not (has5 and has33): continue
    checked+=1
    g=ggroup(f)
    sd=str(g.structure_description())
    if sd=="A6":
        hits.append((f,g))
        print("A6 HIT: %s  disc=%d" % (f, int(f.discriminant())), flush=True)
        if len(hits)>=3: break

print()
print("prefilter candidates checked:", checked, "  A6 hits:", len(hits))
if hits:
    f,g=hits[0]
    print()
    print("=== A6 representative: %s ===" % f)
    print("   order=%d solvable=%s disc=%d" % (g.order(), g.is_solvable(), int(f.discriminant())))
    print("   Frobenius patterns:")
    for p in P:
        c=frob(f,p)
        if c: print("     mod %2d: %s" % (p,c))
print("DONE")
