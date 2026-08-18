# Fast A5 quintic finder.
# Fact: for an irreducible quintic, the transitive subgroups of S5 lying in A5
# are C5, D5, A5. Only A5 contains a 3-cycle. Hence:
#   irreducible  AND  square discriminant  AND  a 3-cycle Frobenius conjugate
#   =>  G = A5   (exactly).
# We use this fast path to search, then confirm the winner with galois_group().
from math import isqrt
import itertools
R.<x> = QQ[]
GOODP = [2,3,5,7,11,13,17,19,23,29,31,37,41]

def is_square(n):
    n = int(n)
    if n < 0: return False
    r = isqrt(n); return r*r == n

def has_3cycle(f):
    for p in GOODP:
        fp = f.change_ring(GF(p))
        if fp == 0: continue
        try: fac = fp.factor()
        except Exception: continue
        degs = []
        ok = True
        for c, e in fac:
            if e > 1: ok = False; break
            degs.append(int(c.degree()))
        if ok and tuple(sorted(degs, reverse=True)) == (3,1,1,1):
            return p
    return None

def ggroup(f):
    g = f.galois_group()
    if isinstance(g, tuple): g = g[0]
    return g

print("=== search general quintics |coef|<=3 for A5 (fast path) ===")
hits = []
for (a4,a3,a2,a1,a0) in itertools.product(range(-3,4), repeat=5):
    f = x^5 + a4*x^4 + a3*x^3 + a2*x^2 + a1*x + a0
    if not f.is_irreducible():
        continue
    if not is_square(f.discriminant()):
        continue
    p3 = has_3cycle(f)
    if p3 is not None:
        hits.append((f, int(f.discriminant()), p3))
print("fast-path A5 candidates:", len(hits))
for f, d, p3 in hits[:8]:
    print("  cand: %s  disc=%d  3-cycle@p=%d" % (f, d, p3))

if hits:
    f = hits[0][0]
    g = ggroup(f)
    print()
    print("=== CONFIRMATION via galois_group for %s ===" % f)
    print("order:", g.order(), " solvable:", g.is_solvable(),
          " sd:", g.structure_description())
    print("disc:", f.discriminant(), " (square:", is_square(f.discriminant()), ")")
    print("Frobenius patterns:")
    for p in GOODP:
        fp = f.change_ring(GF(p))
        if fp == 0: continue
        try: fac = fp.factor()
        except Exception: continue
        degs=[]; ok=True
        for c,e in fac:
            if e>1: ok=False; break
            degs.append(int(c.degree()))
        if ok:
            print("  mod %2d: %s" % (p, tuple(sorted(degs, reverse=True))))
print("DONE")
