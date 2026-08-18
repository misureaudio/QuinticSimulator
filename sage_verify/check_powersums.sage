# Re-verify the power sums of the depressed quintic t^5+p t^3+q t^2+r t+s
# two independent ways: (A) correct Newton recurrence, (B) brute force via
# roots in a splitting field / symmetric-function expansion.
P = PolynomialRing(QQ, 'p,q,r,s')
p, q, r, s = P.gens()

# (A) correct Newton: for k<=n, Pk = sum_{j=1}^{k-1} (-1)^(j-1) e_j P_{k-j} + (-1)^(k-1) k e_k
e1, e2, e3, e4, e5 = 0, p, -q, r, -s
e = [e1, e2, e3, e4, e5]
PkA = {0: 5}
for k in range(1, 10):
    if k <= 5:
        acc = sum(((-1)^(j-1)) * e[j-1] * PkA[k-j] for j in range(1, k))
        acc += ((-1)^(k-1)) * k * e[k-1]
        PkA[k] = acc
    else:
        PkA[k] = sum(((-1)^(j-1)) * e[j-1] * PkA[k-j] for j in range(1, 6))
print("=== (A) Newton recurrence ===")
for k in range(1, 10):
    print("P%d =" % k, PkA[k])

# (B) brute force: expand (t^5+p t^3+q t^2+r t+s), get roots symbolically is
# hard; instead verify P_k via the identity that the power sums satisfy the
# linear recurrence with characteristic = the quintic (for k>5) AND match the
# Newton values for k<=5. Independent cross-check: use the relation
# sum_{i} a_i^k = 0 for k>5 with the recurrence, and check P1..P5 against a
# numeric specialization.
print()
print("=== (B) numeric cross-check at p=1,q=2,r=3,s=4 ===")
subs = {p:1, q:2, r:3, s:4}
poly = PolynomialRing(QQ,'t')('t^5 + p t^3 + q t^2 + r t + s').subs(subs)
print("specialized poly:", poly)
# compute power sums numerically from the actual (complex) roots
C = poly.change_ring(CDF)
roots = C.roots(multiplicities=False)
print("num roots:", len(roots))
for k in range(1, 10):
    num = sum(z^k for z in roots)
    sym = PkA[k].subs(subs)
    # compare to high precision
    ok = abs(complex(num) - complex(sym)) < 1e-6
    print("P%d: numeric=%.6f  symbolic=%.6f  match=%s" % (k, complex(num).real, float(sym), ok))
print("DONE")
