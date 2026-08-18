# VERIFIED sextic battery: distinct transitive types with representatives,
# orders, solvability, discriminants, and Frobenius patterns.
R.<x> = QQ[]
PRIMES = [2,3,5,7,11,13,17,19]

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

def classify(f, label):
    if not f.is_irreducible():
        return None
    g = ggroup(f)
    out = {"label":label,"poly":str(f),"order":int(g.order()),
           "solv":bool(g.is_solvable()),"sd":str(g.structure_description()),
           "disc":int(f.discriminant()),"frob":{}}
    for p in PRIMES:
        c = frob_cycle(f,p)
        if c is not None:
            out["frob"][p]=c
    return out

def scan(family, tag):
    seen={}; rows=[]
    for f,lab in family:
        c = classify(f,lab)
        if c is None: continue
        rows.append(c)
        if c["sd"] not in seen:
            seen[c["sd"]] = c
    return rows, seen

print("################  SEXTICS  ################")
# Bring-Jerrard sextic family x^6 + a*x^3 + b*x + c  and  x^6 + a*x + b
Fam = []
# x^6 + a*x^3 + b*x + c
for a in range(-3,4):
    for b in range(-3,4):
        for c in range(-3,4):
            Fam.append((x^6 + a*x^3 + b*x + c, "BJ6(a=%d,b=%d,c=%d)"%(a,b,c)))
# x^6 + a*x + b
for a in range(-6,7):
    for b in range(-6,7):
        Fam.append((x^6 + a*x + b, "BJ6b(a=%d,b=%d)"%(a,b)))
# general sextics
GEN6 = [
    x^6 - 5*x^4 + 5*x^2 - 1,
    x^6 - 2*x^5 + 3*x^4 - 3*x^3 + 2*x^2 - x + 1,
    x^6 + x^5 - 5*x^4 - 4*x^3 + 4*x^2 + 3*x - 2,
    x^6 - 3*x^5 + 3*x^4 + 2*x^3 - x^2 - 2*x + 1,
    x^6 - 4*x^5 + 6*x^4 - 4*x^3 + 2*x^2 - x + 1,
    x^6 + 2*x^5 - 3*x^4 + x^3 + 2*x - 5,
    x^6 - 7*x^5 + 14*x^4 - 7*x^3 + 7*x^2 - 2*x + 1,
    x^6 - 6*x^5 + 15*x^4 - 20*x^3 + 15*x^2 - 6*x + 2,
]
GEN6 = [(f,"gen6_%d"%(i+1)) for i,f in enumerate(GEN6)]
Fam = Fam + GEN6

rows, seen = scan(Fam, "6")
print("Distinct transitive types found among %d irreducible sextics:" % len(rows))
for sd,c in sorted(seen.items(), key=lambda kv: kv[1]["order"]):
    print("  %-16s order=%-4d solvable=%-5s  example: %s  poly=%s"
          % (sd, c["order"], c["solv"], c["label"], c["poly"]))
print()
print("Representatives (with Frobenius patterns):")
for sd,c in sorted(seen.items(), key=lambda kv: kv[1]["order"]):
    print("  %s | order=%d solv=%s | disc=%d" % (sd, c["order"], c["solv"], c["disc"]))
    print("    %s" % c["poly"])
    print("    frob:", c["frob"])
print()
print("DONE6  (irreducibles: %d, distinct types: %d)" % (len(rows), len(seen)))
