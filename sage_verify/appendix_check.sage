# Verify the exact example printed in Appendix A.1
R.<x> = QQ[]
f = x^5 - 5*x - 5
G = f.galois_group()
if isinstance(G, tuple): G = G[0]
print("order:", G.order())
print("is_solvable:", G.is_solvable())
print("structure_description:", G.structure_description())
print("discriminant:", f.discriminant())
# show a (3,2) Frobenius pattern
for p in [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47]:
    if f.discriminant() % p == 0: continue
    fs = f.change_ring(GF(p)).factor()
    if any(e>1 for _,e in fs): continue
    t = tuple(sorted([P.degree() for P,_ in fs], reverse=True))
    if t == (3,2):
        print("found (3,2) at p =", p)
        break
print("DONE")
