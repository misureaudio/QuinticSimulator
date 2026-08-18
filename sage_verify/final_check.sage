# Final cross-checks (explicit prime list; no primes_first dependency).
import math
R.<x> = QQ[]
PR = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]

def ggroup(f):
    g = f.galois_group()
    if isinstance(g, tuple): g = g[0]
    return g

def pat_at(f, p):
    if f.discriminant() % p == 0:
        return None
    F = f.change_ring(GF(p))
    fs = F.factor()
    if any(e > 1 for _, e in fs):   # ramified: repeated factor
        return None
    return tuple(sorted([P.degree() for P, _ in fs], reverse=True))

def patterns(f, primes):
    out = []
    for p in primes:
        t = pat_at(f, p)
        if t is not None:
            out.append((p, t))
    return out

print("=== S6 representative x^6-3x^3-3x-3 ===")
f6 = x^6 - 3*x^3 - 3*x - 3
g = ggroup(f6)
print("group:", g.structure_description(), "order", g.order(), "solvable", g.is_solvable())
print("disc:", f6.discriminant(), "is_square:", f6.discriminant() > 0 and math.isqrt(f6.discriminant())**2 == f6.discriminant())
found = None
for p in PR:
    t = pat_at(f6, p)
    if t == (2,1,1,1,1,1):
        found = p; break
print("transposition (2,1,1,1,1,1) first at p =", found)
print("sample patterns:", patterns(f6, PR[:12]))
print("observed cycle-type set:", sorted(set(t for _, t in patterns(f6, PR))))

print()
print("=== A5 quintic x^5-5x^4-5x^3+4x^2+x-5 ===")
f5 = x^5 - 5*x^4 - 5*x^3 + 4*x^2 + x - 5
g5 = ggroup(f5)
print("group:", g5.structure_description(), "order", g5.order(), "solvable", g5.is_solvable())
d5 = f5.discriminant()
print("disc:", d5, "is_square:", d5 > 0 and math.isqrt(d5)**2 == d5)
print("sample patterns:", patterns(f5, PR[:12]))
ps = set(t for _, t in patterns(f5, PR))
print("observed cycle-type set:", sorted(ps))
print("has (3,1,1,1):", (3,1,1,1) in ps)
print("has (2,2,1):", (2,2,1) in ps)
print("has (5,):", (5,) in ps)
print("any odd (transposition (2,1,1,1,1) or (3,2)):", (2,1,1,1,1) in ps or (3,2) in ps)
print("DONE")
