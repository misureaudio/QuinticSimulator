# Bring-Jerrard / Tschirnhaus with CORRECT Newton power sums.
# Depressed quintic t^5 + p t^3 + q t^2 + r t + s  (e1=0, e2=p, e3=-q, e4=r, e5=-s).
# Correct Newton: for k<=n,  Pk = sum_{j=1}^{k-1} (-1)^(j-1) e_j P_{k-j} + (-1)^(k-1) k e_k
P = PolynomialRing(QQ, 'p,q,r,s')
p, q, r, s = P.gens()
e1, e2, e3, e4, e5 = 0, p, -q, r, -s
e = [e1, e2, e3, e4, e5]
Pk = {0: 5}
for k in range(1, 12):
    if k <= 5:
        acc = sum(((-1)^(j-1)) * e[j-1] * Pk[k-j] for j in range(1, k))
        acc += ((-1)^(k-1)) * k * e[k-1]
        Pk[k] = acc
    else:
        Pk[k] = sum(((-1)^(j-1)) * e[j-1] * Pk[k-j] for j in range(1, 6))
print("CORRECT power sums:")
for k in range(1, 8):
    print("  P%d =" % k, Pk[k])
print()

# numeric sanity check at p=1,q=2,r=3,s=4
subs = {p:1, q:2, r:3, s:4}
T.<t> = PolynomialRing(QQ)
poly = t^5 + 1*t^3 + 2*t^2 + 3*t + 4
roots = poly.change_ring(CDF).roots(multiplicities=False)
print("numeric check at p=1,q=2,r=3,s=4:")
for k in range(1, 8):
    num = complex(sum(z^k for z in roots))
    sym = complex(Pk[k].subs(subs))
    print("  P%d: numeric=%.6f  sym=%.6f  match=%s" % (k, num.real, sym.real, abs(num-sym)<1e-6))
print()

# ---------- Stage 2: quadratic Tschirnhaus  y = x^2 + u x + v ----------
R2 = PolynomialRing(P, 'u,v')
u, v = R2.gens()
# beta = x^2 + u x + v ;  Q1 = sum beta, Q2 = sum beta^2
# Q1 = P2 + u P1 + 5 v
# Q2 = P4 + 2u P3 + (u^2+2v) P2 + 2uv P1 + 5 v^2
Q1 = Pk[2] + u*Pk[1] + 5*v
Q2 = Pk[4] + 2*u*Pk[3] + (u^2 + 2*v)*Pk[2] + 2*u*v*Pk[1] + 5*v^2
v_sol = ( -Pk[2] / 5 )          # Q1 = 0 => v
Q2_sub = Q2.subs({v: v_sol})
print("Stage 2 (quadratic Tschirnhaus):")
print("  v =", v_sol)
print("  Q2 after v : degree in u =", Q2_sub.degree(u))
print()

# ---------- Stage 3 (naive): cubic Tschirnhaus  z = x^3 + u x^2 + v x + w ----------
R3 = PolynomialRing(P, 'u,v,w')
u, v, w = R3.gens()
A.<a> = PolynomialRing(R3)
def beta_power_sum(k):
    expr = (a^3 + u*a^2 + v*a + w)^k
    total = 0
    for m in range(0, 3*k+1):
        cm = expr.coefficient(m)
        if cm != 0:
            total += cm * Pk[m]
    return total
Q1c = beta_power_sum(1)   # = P3 + u P2 + v P1 + 5 w
Q2c = beta_power_sum(2)
Q3c = beta_power_sum(3)
w_sol = ( -(Pk[3] + u*Pk[2] + v*Pk[1]) / 5 )   # Q1c = 0 => w
E2 = Q2c.subs({w: w_sol})
E3 = Q3c.subs({w: w_sol})
print("Stage 3 (naive cubic Tschirnhaus):")
print("  w =", w_sol)
print("  E2 degree in (u,v):", max(E2.degree(u), E2.degree(v)))
print("  E3 degree in (u,v):", max(E3.degree(u), E3.degree(v)))
res = E2.resultant(E3, v)
print("  resultant in v: degree in u =", res.degree(u))
print()
print("CONCLUSION: with CORRECT power sums, the naive cubic Tschirnhaus")
print("parameter equation has degree %d in the leading parameter." % res.degree(u))
print("DONE")
