R.<x> = QQ[]
f = x^5 - 2*x + 2
g = f.galois_group()
if isinstance(g, tuple): g = g[0]

# probe methods
for m in ["structure_description","describe","cycle_type","is_solvable","order"]:
    print(m, "exists:", hasattr(g, m))

print()
print("order:", g.order(), " solvable:", g.is_solvable())
try:
    print("structure_description:", g.structure_description())
except Exception as e:
    print("structure_description failed:", e)
# try permutation group
try:
    P = g.permutation_group()
    print("perm group order:", P.order())
    print("perm group cycle type sample:", P.gens()[0])
except Exception as e:
    print("permutation_group failed:", e)

print()
print("discriminant:", f.discriminant())
for p in [2,3,5,7,11,13]:
    fp = f.change_ring(GF(p))
    if fp == 0:
        print("mod %d: zero poly (p divides content)" % p); continue
    fac = fp.factor()
    degs = tuple(sorted([int(e) for c,e in fac]))
    print("mod %d: %s   degrees=%s" % (p, fac, degs))
print("DONE")
