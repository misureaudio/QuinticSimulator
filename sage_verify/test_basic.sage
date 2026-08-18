# Basic Sage sanity test: Galois group computation
R.<x> = QQ[]

def ggroup(f):
    g = f.galois_group()
    if isinstance(g, tuple):
        g = g[0]
    return g

f1 = x^5 - x^4 - 4*x^3 + 3*x^2 + 3*x - 1
print("f1 =", f1)
print("f1 irreducible:", f1.is_irreducible())
G1 = ggroup(f1)
print("f1 galois group order:", G1.order())
print("f1 solvable:", G1.is_solvable())
print()

f2 = x^5 + x^4 - 4*x^3 - 3*x^2 + 3*x + 1
print("f2 =", f2)
print("f2 irreducible:", f2.is_irreducible())
G2 = ggroup(f2)
print("f2 galois group order:", G2.order())
print("f2 solvable:", G2.is_solvable())
print()

f3 = x^5 - 2*x + 2
print("f3 =", f3)
print("f3 irreducible:", f3.is_irreducible())
G3 = ggroup(f3)
print("f3 galois group order:", G3.order())
print("f3 solvable:", G3.is_solvable())
print()

print("DONE")
