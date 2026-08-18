# Capped hunt for remaining sextic transitive types: A5, S5, A6, S4.
# Hard cap on galois_group() calls so this always finishes.
R.<x> = QQ[]
WANT = {"S4":None, "A5":None, "S5":None, "A6":None}
CAP = 700

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

def detail(f):
    out = {"poly":str(f),"disc":int(f.discriminant()),"frob":{}}
    for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
        c = frob_cycle(f,p)
        if c: out["frob"][p]=c
    return out

# Moderate pool: x^6 + a x^4 + b x^3 + c x^2 + d x + e with small coeffs,
# plus x^6 + a x^3 + b x + c.
pool = []
for a in range(-3,4):
    for b in range(-3,4):
        for c in range(-3,4):
            for d in range(-3,4):
                for e in range(-3,4):
                    pool.append(x^6 + a*x^4 + b*x^3 + c*x^2 + d*x + e)
for a in range(-6,7):
    for b in range(-6,7):
        for c in range(-6,7):
            pool.append(x^6 + a*x^3 + b*x + c)

seen = set()
checked = 0
for f in pool:
    if checked >= CAP:
        print("CAP reached at %d" % checked, flush=True)
        break
    if f in seen: continue
    seen.add(f)
    if not f.is_irreducible():
        continue
    g = ggroup(f)
    sd = str(g.structure_description())
    checked += 1
    if sd in WANT and WANT[sd] is None:
        WANT[sd] = (f, g)
        print("FOUND %s: %s  (order=%d, solvable=%s)" % (sd, f, g.order(), g.is_solvable()), flush=True)
    if checked % 200 == 0:
        print("  ...checked %d, found: %s" % (checked, [k for k,v in WANT.items() if v]), flush=True)

print()
print("checked %d irreducibles (cap %d)" % (checked, CAP))
print()
for sd in ["S4","A5","S5","A6"]:
    if WANT[sd]:
        f, g = WANT[sd]
        d = detail(f)
        print("=== %s : %s ===" % (sd, f))
        print("   order=%d solvable=%s disc=%d" % (g.order(), g.is_solvable(), d["disc"]))
        print("   frob:", d["frob"])
    else:
        print("=== %s : NOT FOUND (cap reached) ===" % sd)
print("DONE")
