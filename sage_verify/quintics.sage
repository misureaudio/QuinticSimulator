# VERIFIED Galois-group battery for quintics and sextics.
# For each irreducible f: report Galois group (structure_description), order,
# solvability, discriminant, and the Dedekind (Frobenius) cycle-type patterns
# at a set of primes (degree of each irreducible factor = cycle length).
R.<x> = QQ[]
PRIMES = [2,3,5,7,11,13,17,19]

def ggroup(f):
    g = f.galois_group()
    if isinstance(g, tuple):
        g = g[0]
    return g

def frob_cycle(f, p):
    """Return the multiset of degrees of the irreducible factors of f mod p
    (the cycle structure of a Frobenius conjugate), or None if p is bad
    (p | discriminant or f mod p has repeated factor / is zero)."""
    fp = f.change_ring(GF(p))
    if fp == 0:
        return None
    try:
        fac = fp.factor()
    except Exception:
        return None
    degs = []
    for c, e in fac:
        d = c.degree()
        if e > 1:
            return None  # repeated factor => p divides discriminant
        degs.append(int(d))
    return tuple(sorted(degs, reverse=True))

def classify(f, label):
    if not f.is_irreducible():
        return None
    g = ggroup(f)
    out = {
        "label": label,
        "poly": str(f),
        "order": int(g.order()),
        "solv": bool(g.is_solvable()),
        "sd": str(g.structure_description()),
        "disc": int(f.discriminant()),
        "frob": {}
    }
    for p in PRIMES:
        c = frob_cycle(f, p)
        if c is not None:
            out["frob"][p] = c
    return out

def scan(family, tag):
    """family: list of (poly, label). Returns (rows, seen_by_sd)."""
    seen = {}
    rows = []
    for f, lab in family:
        c = classify(f, lab)
        if c is None:
            continue
        key = c["sd"]
        rows.append(c)
        if key not in seen:
            seen[key] = c
    return rows, seen

print("################  QUINTICS  ################")
# Bring-Jerrard family x^5 + a x + b, small a,b
BJ5 = []
for a in range(-5, 6):
    for b in range(-5, 6):
        BJ5.append((x^5 + a*x + b, "BJ5(a=%d,b=%d)" % (a, b)))
# explicit general quintics
GEN5 = [
    x^5 - 4*x^3 - 4*x^2 + 3*x + 1,
    x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1,
    x^5 - x^4 - 4*x^3 + 3*x^2 + 3*x - 1,
    x^5 - 2*x + 2,
    x^5 - 3*x + 1,
    x^5 + 2*x^3 - 3*x + 1,
    x^5 + x^4 - 5*x^3 + 3*x^2 + 4*x - 2,
    x^5 - 5*x + 12,
]
GEN5lab = ["gen%d" % (i+1) for i in range(len(GEN5))]
GEN5 = [(f, l) for f, l in zip(GEN5, GEN5lab)]

all5 = BJ5 + GEN5
rows5, seen5 = scan(all5, "5")
print("Distinct transitive types found among %d irreducible quintics:" % len(rows5))
for sd, c in sorted(seen5.items(), key=lambda kv: kv[1]["order"]):
    print("  %-14s order=%-4d solvable=%-5s  example: %s  poly=%s"
          % (sd, c["order"], c["solv"], c["label"], c["poly"]))
print()
# full detail for one representative of each type
print("Representatives (with Frobenius patterns):")
for sd, c in sorted(seen5.items(), key=lambda kv: kv[1]["order"]):
    print("  %s | order=%d solv=%s | disc=%d" % (sd, c["order"], c["solv"], c["disc"]))
    print("    %s" % c["poly"])
    print("    frob:", c["frob"])
print()
print("DONE5  (irreducibles: %d, distinct types: %d)" % (len(rows5), len(seen5)))
