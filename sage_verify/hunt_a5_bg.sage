# Background A5 quintic search: filter irreducible + square discriminant,
# then compute galois_group() on survivors (far fewer than all), keep A5.
from math import isqrt
import itertools, sys
R.<x> = QQ[]

def is_square(n):
    n = int(n)
    if n < 0: return False
    r = isqrt(n); return r*r == n

def ggroup(f):
    g = f.galois_group()
    if isinstance(g, tuple): g = g[0]
    return g

def frob_cycle(f, p):
    fp = f.change_ring(GF(p))
    if fp == 0: return None
    try: fac = fp.factor()
    except Exception: return None
    degs=[]; ok=True
    for c,e in fac:
        if e>1: ok=False; break
        degs.append(int(c.degree()))
    return tuple(sorted(degs, reverse=True)) if ok else None

BOX = 5
hits = []
n_checked = 0
for (a4,a3,a2,a1,a0) in itertools.product(range(-BOX,BOX+1), repeat=5):
    f = x^5 + a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0
    if not f.is_irreducible():
        continue
    if not is_square(f.discriminant()):
        continue
    n_checked += 1
    g = ggroup(f)
    sd = str(g.structure_description())
    if sd == "A5":
        p3 = None
        for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
            if frob_cycle(f,p) == (3,1,1,1):
                p3 = p; break
        hits.append((f, int(f.discriminant()), p3))
        print("A5 HIT: %s  disc=%d  3-cycle@p=%s" % (f, int(f.discriminant()), p3), flush=True)
    if n_checked % 50 == 0:
        print("progress: %d square-disc irreducibles checked, %d A5 so far" % (n_checked, len(hits)), flush=True)

print()
print("TOTAL square-disc irreducibles checked:", n_checked)
print("TOTAL A5 found:", len(hits))
if hits:
    f,d,p3 = hits[0]
    print()
    print("=== FULL DETAIL: %s ===" % f)
    g = ggroup(f)
    print("order:", g.order(), " solvable:", g.is_solvable(), " sd:", g.structure_description())
    print("disc:", d)
    print("Frobenius patterns:")
    for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
        c = frob_cycle(f,p)
        if c: print("  mod %2d: %s" % (p, c))
print("DONE", flush=True)
