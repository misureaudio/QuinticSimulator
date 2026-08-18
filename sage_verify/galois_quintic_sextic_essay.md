# Galois Theory and the Solution of Quintic and Sextic Polynomials over the Complex Field

**An exposition for readers in algebra, group and field theory, and in computer algebra**

---

## Abstract

We give a self-contained account of what Galois theory determines about the
solubility of quintic and sextic polynomial equations, and what modern computer
algebra can and cannot compute from it. Working over the rationals with roots
realized in $\mathbb{C}$, we recall the fundamental correspondence and the
criterion that a separable equation is solvable by radicals if and only if its
Galois group is a solvable group. We then carry out the classification that the
criterion reduces the problem to: the five transitive subgroups of $S_5$ and the
sixteen of $S_6$, with their orders and solvability, each entry verified by an
independent computation in GAP. We exhibit, for every transitive type we could
isolate with small integer coefficients, a concrete polynomial whose Galois
group we compute, together with its discriminant and the cycle types of its
Frobenius conjugates at a set of primes. The computational side is developed
with the precision a computer-algebra reader expects: irreducibility by
modular reduction and the Lenstra–Lenstra–Lovász lattice basis reduction,
factorization over finite fields, the extraction of Frobenius cycle structure
from the Dedekind factorization pattern, and the use of resolvent polynomials
to descend through the subgroup lattice. We close with applications —
constructibility, the identification and solution of solvable quintics, and the
role of Galois groups in cryptography and complexity — and a candid discussion
of the limits of the method, including the subtle point that a Bring–Jerrard
reduction changes the base field and hence the relevant Galois group. Every
computed quantity in the paper was produced by an executable script; the
accompanying log records the exact inputs and outputs.

---

## 1. Introduction and the meaning of "over the complex field"

Let $f(x)\in\mathbb{Q}[x]$ be a separable polynomial of degree $n$ with
distinct roots $\alpha_1,\dots,\alpha_n\in\mathbb{C}$. The phrase "solving the
equation over the complex field" needs a word of caution, because it can be
read in two ways, and only one of them is interesting.

Over $\mathbb{C}$ itself, Galois theory is vacuous: $\mathbb{C}$ is
algebraically closed, so $f$ splits completely there and the only **algebraic**
extension of $\mathbb{C}$ is $\mathbb{C}$ itself. There is no non-trivial Galois
group to study *over* $\mathbb{C}$. What is interesting is the Galois group over
the **base field** — ordinarily $\mathbb{Q}$ — acting on the $n$ complex roots.
Concretely, if $L=\mathbb{Q}(\alpha_1,\dots,\alpha_n)\subseteq\mathbb{C}$ is
the splitting field of $f$ over $\mathbb{Q}$, then

$$G=\operatorname{Gal}(L/\mathbb{Q})$$

is a finite group of field automorphisms of $L$. Each $\sigma\in G$ permutes the
roots, and the map $\sigma\mapsto(\alpha_1,\dots,\alpha_n)\mapsto
(\sigma(\alpha_1),\dots,\sigma(\alpha_n))$ embeds $G$ faithfully and
transitively into the symmetric group $S_n$. Thus the problem of "solving $f$
over $\mathbb{C}$" is, in the language of Galois, the problem of understanding
the transitive permutation group $G\le S_n$ that the complex roots carry.

This reframing is the whole point of the theory. The question "can the roots be
written by radicals?" — a question that looks analytic — is converted into the
purely group-theoretic question "is $G$ a solvable group?" The next section
states the bridge precisely; the rest of the paper is the classification and
computation that the bridge makes possible.

We take the audience to be comfortable with the definitions of field extension,
splitting field, and the fundamental theorem of Galois theory, and we move
quickly to the content that is specific to degrees five and six.

---

## 2. The bridge: solvability by radicals and solvable groups

Let $f\in\mathbb{Q}[x]$ be separable of degree $n$, with splitting field $L$
over $\mathbb{Q}$ and Galois group $G=\operatorname{Gal}(L/\mathbb{Q})$, viewed
as a transitive subgroup of $S_n$.

**The fundamental correspondence.** For each subgroup $H\le G$ there is a
subfield $L^{H}=\{x\in L: h(x)=x\ \forall h\in H\}$, and the assignments
$H\mapsto L^{H}$ and $K\mapsto\operatorname{Gal}(L/K)$ are inclusion-reversing
bijections between the subgroups of $G$ and the intermediate fields
$\mathbb{Q}\subseteq K\subseteq L$. Moreover $[L^{H}:\mathbb{Q}]=[G:H]$.

**The radical criterion.** Over a field of characteristic $0$:

> *The roots of $f$ can be expressed by radicals over $\mathbb{Q}$ if and only
> if $G$ is a solvable group.*

Here "solvable" means that $G$ possesses a subnormal series
$1=H_0\triangleleft H_1\triangleleft\cdots\triangleleft H_r=G$ whose quotients
$H_{i+1}/H_i$ are cyclic (equivalently, abelian). The forward direction
(radical expression $\Rightarrow$ solvable $G$) is the content of Abel's and
Galois's work; the reverse direction (solvable $G$ $\Rightarrow$ radical
expression) is the deeper, constructive half and is the one that makes the
criterion *useful*: it says that to solve $f$ it suffices to exhibit a tower of
cyclic extensions, each of which can be unwound by the appropriate root of a
norm.

For degrees $n\le 4$ every transitive subgroup of $S_n$ is solvable, which is
why the quadratic, cubic, and quartic formulas exist. The first degree at which
a non-solvable transitive group appears is $n=5$: $A_5$ (order $60$) is simple
and non-abelian, so it is not solvable, and $S_5$ (order $120$) has $A_5$ as a
composition factor. This single observation is the seed of the Abel–Ruffini
theorem, and it is why degrees five and six are the first where the question
"is it solvable by radicals?" has a non-trivial answer.

We record the precise statement of the classical impossibility result.

**Theorem (Abel–Ruffini, Galois form).** *The general equation of degree $n\ge
5$ is not solvable by radicals. Equivalently, the Galois group of the general
polynomial $x^n+a_{n-1}x^{n-1}+\cdots+a_0$ over the rational function field
$\mathbb{Q}(a_0,\dots,a_{n-1})$ is the full symmetric group $S_n$, which is not
solvable for $n\ge 5$.*

The content for the reader is not the group-theoretic fact that $S_n$ is not
solvable for $n\ge 5$ — that is a one-line exercise once $A_5$ is known to be
simple — but the assertion that the *generic* Galois group is the full
symmetric group. For $n=5$ this says: a "typical" quintic has Galois group $S_5$
and is not solvable by radicals; the solvable quintics are the exceptional,
structurally constrained ones.

---

## 3. The quintic: five transitive subgroups of $S_5$

Because $G$ is transitive, the problem for a quintic is to identify which of
the transitive subgroups of $S_5$ it is. There are exactly five, and we give the
complete list with the data that a computer-algebra system reports.

**Table 1. Transitive subgroups of $S_5$ (verified in GAP, `enumerate2.g`).**

| label | order | solvable | structure |
|-------|-------|----------|-----------|
| $5T_1$ | $5$   | yes | $C_5$ |
| $5T_2$ | $10$  | yes | $D_{10}$ (dihedral) |
| $5T_3$ | $20$  | yes | $C_5:C_4$ (Frobenius group $F_{20}=\operatorname{AGL}(1,5)$) |
| $5T_4$ | $60$  | **no** | $A_5$ |
| $5T_5$ | $120$ | **no** | $S_5$ |

The immediate corollary is the classical characterization, due in its
computable form to Young and Dickson:

> *An irreducible quintic over $\mathbb{Q}$ is solvable by radicals if and only
> if its Galois group is $C_5$, $D_{10}$, or $F_{20}$ — that is, if and only if
> it is contained in the Frobenius group $F_{20}$ of order $20$.*

The three solvable cases have distinct, easily detected signatures, which is
what makes them *computable*:

- **$C_5$ (cyclic).** The Galois group has order $5$ and is abelian. The
  discriminant is a square in $\mathbb{Q}$ (so $G\subseteq A_5$) and there is no
  element of order $2$ or $4$. A cyclic quintic is not a Kummer extension of a
  quadratic field: the natural Kummer base for a cyclic extension of degree $5$
  must contain the fifth roots of unity, and that field is
  $\mathbb{Q}(\zeta_5)$, of degree $4$ over $\mathbb{Q}$ (its unique quadratic
  subfield is $\mathbb{Q}(\sqrt{5})$, which does *not* contain $\zeta_5$). The
  correct statement is that, after adjoining $\zeta_5$, the compositum
  $L(\zeta_5)/\mathbb{Q}(\zeta_5)$ is a Kummer extension of degree $5$
  (cyclic of order $5$ over a field containing $\mu_5$).
- **$D_{10}$ (dihedral).** Order $10$, $G\subseteq A_5$ (square discriminant),
  and $G$ contains a reflection — a double transposition — but no element of
  order $4$.
- **$F_{20}$ (Frobenius).** Order $20$, $G\not\subseteq A_5$ (non-square
  discriminant), and $G$ contains an element of order $4$ (a $4$-cycle). This is
  the largest solvable transitive subgroup of $S_5$.

The two non-solvable cases, $A_5$ and $S_5$, are separated by the discriminant:
$G\subseteq A_5$ (hence $G=A_5$, since $A_5$ is the only transitive subgroup of
$A_5$ containing a $3$-cycle) exactly when the discriminant is a square in
$\mathbb{Q}$; $G=S_5$ when it is not. The discriminant test is the single most
useful invariant for quintics, and it is cheap to compute.

**The $A_5$/$S_5$ discriminator via Frobenius elements.** A further refinement,
which is how the identification is actually carried out computationally, uses
the Frobenius conjugates. For a prime $p$ not dividing the discriminant of $f$,
reduce $f$ modulo $p$ and factor it over $\mathbb{F}_p$ into irreducibles of
degrees $d_1,\dots,d_k$. The multiset $\{d_1,\dots,d_k\}$ is the cycle
structure of a Frobenius conjugate of $G$ in $S_5$ (Dedekind's theorem on the
decomposition of primes). By sampling enough primes one collects the cycle
types that occur in $G$, and the identification of $G$ is then a finite
matching problem against Table 1. For example, a $3$-cycle appearing among the
Frobenius conjugates forces $G$ to contain a $3$-cycle; combined with a square
discriminant ($G\subseteq A_5$) this forces $G=A_5$, because neither $C_5$ nor
$D_{10}$ contains a $3$-cycle.

---

## 4. The sextic: sixteen transitive subgroups of $S_6$

The sextic is where the problem becomes genuinely richer. There are sixteen
transitive subgroups of $S_6$, and the list contains phenomena that have no
quintic analogue: two *distinct* embeddings of $S_4$ into $S_6$, a non-solvable
subgroup of order $60$ that is $A_5$ acting on six points (not on five), and
the full $S_6$ together with $A_6$.

**Table 2. Transitive subgroups of $S_6$ (verified in GAP, `enumerate2.g`).**

| label | order | solvable | structure |
|-------|-------|----------|-----------|
| $6T_1$  | $6$   | yes | $C_6$ |
| $6T_2$  | $6$   | yes | $S_3$ |
| $6T_3$  | $12$  | yes | $D_{12}$ |
| $6T_4$  | $12$  | yes | $A_4$ |
| $6T_5$  | $18$  | yes | $C_3\times S_3$ |
| $6T_6$  | $24$  | yes | $C_2\times A_4$ |
| $6T_7$  | $24$  | yes | $S_4$ (natural action on $6=\binom{4}{2}$) |
| $6T_8$  | $24$  | yes | $S_4$ (distinct transitive embedding) |
| $6T_9$  | $36$  | yes | $S_3\times S_3$ |
| $6T_{10}$| $36$ | yes | $(C_3\times C_3):C_4$ |
| $6T_{11}$| $48$ | yes | $C_2\times S_4$ |
| $6T_{12}$| $60$ | **no** | $A_5$ (on six points) |
| $6T_{13}$| $72$ | yes | $(S_3\times S_3):C_2$ |
| $6T_{14}$| $120$| **no** | $S_5$ (on six points) |
| $6T_{15}$| $360$| **no** | $A_6$ |
| $6T_{16}$| $720$| **no** | $S_6$ |

The solvable/non-solvable split is $12$ to $4$. The four non-solvable groups are
$A_5$, $S_5$, $A_6$, and $S_6$ — and note that the first two act on **six**
points, not on five, so a sextic with Galois group $A_5$ is not "a quintic in
disguise" but a genuinely different permutation representation.

Two features of Table 2 deserve emphasis for the computer-algebra reader:

1. **The two $S_4$'s.** There are two transitive subgroups of $S_6$ isomorphic
   to $S_4$. Both have abstract group $S_4$ and order $24$, so reporting only
   "the group is $S_4$" is an *incomplete* answer in degree $6$: the abstract
   group does not determine the permutation representation. They are separated
   by the point-stabilizer structure and, equivalently, by the cycle-type set
   (both verified in GAP): the natural/edge action $6T_7$ (action of $S_4$ on
   the six $2$-subsets of a $4$-set) has point stabilizer $C_2\times C_2$ and
   cycle types $\{(2,2,1,1),(4,2),(3,3)\}$; the other representation $6T_8$
   (coset action on a cyclic subgroup of order $4$) has point stabilizer $C_4$
   and cycle types $\{(2,2,1,1),(4,1,1,1),(2,2,2),(3,3)\}$. The general lesson
   is that "computing the abstract group" is not the same as "computing the
   permutation representation"; in this case the cycle-type set does the
   separating work.

2. **The $A_5$ and $S_5$ on six points.** These are the transitive degree-$6$
   representations of the two non-solvable degree-$5$ groups. The $A_5$
   ($6T_{12}$, order $60$) has point stabilizer $D_{10}$ (the dihedral group of
   order $10$); it is the action of $A_5$ on the cosets of its index-$6$
   subgroup $D_{10}$, the normalizer of a $5$-cycle. The $S_5$ ($6T_{14}$,
   order $120$) has point stabilizer $F_{20}=C_5:C_4$ (order $20$); it is the
   action of $S_5$ on the cosets of its index-$6$ subgroup $F_{20}$, the
   normalizer of a $5$-cycle. Both are genuinely different permutation
   representations from the familiar degree-$5$ actions, and neither is
   obtained from the quintic case by a simple restriction. The transitive
   $S_5\le S_6$ is the *exotic* $S_5$-subgroup: $S_6$ contains two conjugacy
   classes of $S_5$-subgroups — one intransitive (point stabilizer $S_4$) and
   one transitive (point stabilizer $F_{20}$) — and the exceptional outer
   automorphism of $S_6$ interchanges them. The same phenomenon occurs for
   $A_5$: there are two conjugacy classes of $A_5$-subgroups of $S_6$
   (intransitive, stabilizer $A_4$; transitive, stabilizer $D_{10}$), again
   interchanged by the outer automorphism. (Note that
   $\operatorname{Out}(A_5)\cong C_2$, not trivial:
   $\operatorname{Aut}(A_5)\cong S_5$ with
   $\operatorname{Inn}(A_5)\cong A_5$; the outer automorphism of $S_6$ is a
   separate, $S_6$-specific phenomenon.) A sextic whose Galois group is this
   transitive $S_5$ is not solvable by radicals, because $S_5$ is not solvable.
   The point of recording both is that the sextic classification cannot be
   obtained by "just looking at the quintic case."

As in the quintic, the discriminant gives the first split: $G\subseteq A_6$
exactly when the discriminant is a square in $\mathbb{Q}$, which rules out
$S_5$ (on six points), $S_6$, and any group containing an odd permutation, and
leaves $A_5$, $A_6$, and the solvable groups. Distinguishing $A_5$ from $A_6$
among the square-discriminant sextics then requires cycle-type analysis. Both
contain the $5$-cycle $(5,1)$, the double $3$-cycle $(3,3)$, and the double
transposition $(2,2,1,1)$, and neither contains a $6$-cycle or a transposition.
The separating cycle types are the $4$-cycle-with-transposition $(4,2)$ and the
single $3$-cycle $(3,1,1,1)$: the transitive $A_5$ ($6T_{12}$, point stabilizer
$D_{10}$) contains neither, whereas $A_6$ ($6T_{15}$, point stabilizer $A_5$)
contains both. Two directions of the argument have different logical strength.
The **positive** direction is safe from a finite sample: a single observed
Frobenius conjugate of type $(4,2)$ or $(3,1,1,1)$ forces $G=A_6$, because the
transitive $A_5$ contains neither. The **negative** direction is *not* safe
from a finite sample: if the primes tried happen to return only cycle types in
$\{(2,2,1,1),(5,1),(3,3)\}$, that is consistent with $A_6$ as well as with the
transitive $A_5$ (an $A_6$ group can easily produce an initial sample drawn
entirely from the shared cycle types), so one may not conclude $G$ is the
transitive $A_5$ from containment of a finite observed set. That conclusion
requires either a *complete* cycle-type set (guaranteed, in these two degrees,
by the uniqueness of §6.1) or a resolvent certificate that the fixed field of
the candidate $A_5$ is the base field.

---

## 5. Verified computational examples

This section records concrete polynomials whose Galois groups we computed, with
the discriminant and the Frobenius cycle types at a set of primes. Every number
below is the output of an executable script (SageMath 10.9, `sagemath/
sagemath:latest`; group enumeration in GAP 4.11.1, `gapsystem/gap-docker:
latest`); the inputs and the raw outputs are in the accompanying log. The
Frobenius pattern at a prime $p$ is the tuple of degrees of the irreducible
factors of $f\bmod p$, largest first; primes dividing the discriminant are
skipped because the reduction has repeated factors there.

### 5.1 Quintics — one representative per transitive type

**Table 3. Verified quintic representatives.**

| Galois group | order | polynomial | discriminant | Frobenius patterns (sample primes) |
|--------------|-------|------------|--------------|------------------------------------|
| $C_5$ | $5$   | $x^5+x^4-4x^3-3x^2+3x+1$ | $14641$ | $(5,)$ at $2,3,5,7,13,17,19$ |
| $D_{10}$ | $10$ | $x^5-5x+12$ | $64000000$ (square) | $(5,)$ and $(2,2,1)$ |
| $F_{20}$ | $20$ | $x^5-5$ | $1953125$ | $(4,1)$, $(5,)$, $(2,2,1)$ |
| $A_5$ | $60$ | $x^5-5x^4-5x^3+4x^2+x-5$ | $116057529$ (square) | $(5,)$, $(3,1,1)$, $(2,2,1)$ |
| $S_5$ | $120$| $x^5-5x-5$ | $1153125$ | $(3,2)$, $(5,)$, $(2,2,1)$, $(4,1)$ |

Two observations are worth making. First, the **trinomial family** $x^5+ax+b$
with small $a,b$ produced representatives for $C_5$, $D_{10}$, $F_{20}$, and
$S_5$ but **no** $A_5$ in the box searched; the $A_5$ representative required
searching general quintics, because an $A_5$ quintic must have a square
discriminant, a strong arithmetic constraint that the small trinomial box does
not easily satisfy. Second, the Frobenius patterns in the right column are
exactly the cycle types that the corresponding group contains: the $C_5$ row has
only $5$-cycles, the $S_5$ row has the full menu including the odd $(3,2)$, and
the $A_5$ row has $3$-cycles and double transpositions but no odd permutation —
consistent with its square discriminant.

### 5.2 Sextics — nine of the sixteen transitive types

**Table 4. Verified sextic representatives (nine of sixteen types).**

| Galois group | order | polynomial | discriminant | Frobenius patterns (sample primes) |
|--------------|-------|------------|--------------|------------------------------------|
| $C_6$ | $6$ | $x^6-x^3+1$ | $-19683$ | $(6,)$, $(3,3)$, $(2,2,2)$ |
| $S_3$ | $6$ | $x^6+3$ | $-11337408$ | $(2,2,2)$, $(3,3)$ |
| $D_{12}$ | $12$ | $x^6-3x^3-1$ | $1601613$ | $(6,)$, $(2,2,2)$, $(2,2,1,1)$ |
| $C_3\times S_3$ | $18$ | $x^6-3x^3+3$ | $-177147$ | $(6,)$, $(3,1,1,1)$, $(2,2,2)$ |
| $S_3\times S_3$ | $36$ | $x^6-3x^3-3$ | $60761421$ | $(6,)$, $(2,2,1,1)$ |
| $C_2\times S_4$ | $48$ | $x^6-3x+5$ | $-143521875$ | $(6,)$, $(4,2)$, $(3,3)$ |
| $(S_3\times S_3):C_2$ | $72$ | $x^6-3x+3$ | $-9059283$ | $(6,)$, $(3,2,1)$, $(4,2)$ |
| $A_6$ | $360$ | $x^6-4x^4-x^3-3x^2+4x-1$ | $6235009$ (square) | $(5,1)$, $(4,2)$, $(3,3)$, $(2,2,1,1)$ |
| $S_6$ | $720$ | $x^6-3x^3-3x-3$ | $86383584$ | $(4,2)$, $(3,3)$, $(5,1)$, $(3,2,1)$ |

The $A_6$ row is the one that exercises the distinction made in §4: the
discriminant $6235009$ is a square (so $G\subseteq A_6$), and the Frobenius
patterns include $(5,1)$ and $(3,3)$ — the signature of $A_6$ on six points —
with no $6$-cycle and no transposition anywhere in the sample. The $S_6$ row,
by contrast, has a non-square discriminant and the full range of cycle types.

The seven types we did **not** isolate with small coefficients are $A_4$,
$C_2\times A_4$, $(C_3\times C_3):C_4$, the two $S_4$'s, the $A_5$ on six
points, and the $S_5$ on six points. Their existence and structure are recorded
in Table 2 (verified in GAP); isolating a small-coefficient representative for
each is a search problem that our bounded box did not complete, and we do not
claim it. This is a deliberate statement of the boundary between what was
*verified by direct computation* (Tables 1, 2, 3, 4) and what is asserted from
the classification (the remaining entries of Table 2).

---

## 6. The computer-algebra view: what is actually computed

For the reader who will implement or call these routines, the following is the
pipeline that the examples in §5 were produced by, with the algorithmic content
and its cost stated at each step.

**Step 0 — Square-free and irreducible.** Factor out the square-free part
(cheap, via the derivative). Then test irreducibility over $\mathbb{Q}$. The
standard method reduces $f$ modulo a suitable prime $p$ (one not dividing the
leading coefficient or the discriminant) and tests irreducibility over
$\mathbb{F}_p$; if $f$ is irreducible mod $p$ for such a $p$, it is irreducible
over $\mathbb{Q}$ (the converse — $f$ reducible over $\mathbb{Q}$ but
irreducible mod $p$ for every $p$ tried — is where lifting and bounds enter).
Polynomial factorization over $\mathbb{Q}$ is polynomial-time in the bit-size
of the input, achieved by combining modular factorization, Hensel lifting,
coefficient bounds, and lattice-reduction techniques such as the
Lenstra–Lenstra–Lovász (LLL) algorithm. It is not correct to single out the LLL
step as the sole reason for polynomial-time complexity; rather, LLL is the
component that controls the height of the lifted factors (via a short-vector
argument on the lattice of possible factor coefficients), which is what keeps
the overall process polynomial in the bit-size of the input rather than
exponential in the coefficient height.

**Step 1 — The discriminant.** Compute $\Delta(f)$ and test whether it is a
square in $\mathbb{Q}$. This single test gives the split $G\subseteq A_n$ vs.
$G\not\subseteq A_n$, and for a quintic it already separates the solvable
groups ($C_5,D_{10}$) from $A_5$ (all square) and $F_{20},S_5$ (all non-square
for the latter two, though $F_{20}$ is the solvable non-square case). The
discriminant is computed from the resultant of $f$ and $f'$, or directly from
the Vandermonde determinant; both are standard and polynomial-time.

**Step 2 — Frobenius cycle types.** For a batch of small primes $p\nmid\Delta$,
factor $f\bmod p$ over $\mathbb{F}_p$ and record the multiset of degrees of the
irreducible factors. Each such multiset is the cycle type of a Frobenius
conjugate. Factoring over $\mathbb{F}_p$ is polynomial-time (Cantor–Zassenhaus
and its descendants). The subtlety is *how many* primes are needed: the answer
depends on the gap between the cycle types of the candidate groups, and in the
worst case one may need to sample until the set of observed cycle types
uniquely identifies $G$ among the transitive subgroups not yet excluded by the
discriminant. In practice, for degrees $5$ and $6$, a dozen or so small primes
suffice, as the tables above show.

**Step 3 — Resolvents and the descent.** The step that is *not* automatic from
the cycle types is knowing when the cycle-type set is **complete**: a finite
sample of primes returns a subset of the Frobenius conjugates, and a rare cycle
type (for example the transpositions of an $S_n$) may simply not have appeared
yet. The **resolvent polynomials** supply the certificate that the observed set
is the whole set, and more generally they drive the identification. The
criterion must be stated with the correct direction and the correct acting
group. Let $G=\operatorname{Gal}(L/K)$ act faithfully and transitively on the
roots (so $G$ is a transitive subgroup of $S_n$), and let $H\le S_n$ be a
*candidate* subgroup of the same degree (typically the point stabilizer of one
of the other transitive subgroups). Choose $\theta\in L$ whose stabilizer in
$S_n$ is exactly $H$, and form the resolvent
$$R(T)=\prod_{\bar g\in S_n/H}\bigl(T-g\theta\bigr),$$
the product over a set of distinct $H$-coset representatives (the distinct
values $g\theta$). The coefficients of $R$ lie in $K$. Then
$$G\le H^{\,g}\text{ for some }g\in S_n\quad\Longleftrightarrow\quad
R\text{ has a root in }K\quad\Longleftrightarrow\quad
R\text{ has a linear factor over }K.$$
The equivalence is the content: $R$ has a $K$-root iff some conjugate $g\theta$
lies in $K$, iff $g\theta$ is fixed by all of $G$, iff
$G\le\operatorname{Stab}(g\theta)=gHg^{-1}=H^{g}$. So the test answers the
question *"is the actual Galois group contained in a conjugate of the
candidate $H$?"* — not the abstract question "$H\le G$". This converts the
subgroup-containment question into a factorization question over $K$, each of
which is back to Step 0. The descent proceeds by stepping down the lattice of
transitive subgroups — testing, at each node, whether $G$ falls into a
conjugate of the corresponding stabilizer — and it is this that makes the
method complete: for fixed $n$ the lattice is finite, so the descent
terminates. In degrees $5$ and $6$ the cycle-type sets are unique (§6.1), so
the cycle-type test is in principle already decisive; the resolvent descent is
what turns a finite prime sample into a *proven* identification, and it is the
engine that makes the method work for larger $n$ as well.

**Step 4 — Group recognition.** The final identification — "this is the group
$5T_3$ / $6T_{11}$" — is a matching of the computed invariants (order, cycle
types, resolvent factorizations) against the known list of transitive subgroups
of $S_n$. For $n=5$ and $n=6$ these lists are Tables 1 and 2, and they are small
enough to hard-code; for larger $n$ one consults a database of transitive groups
(as GAP does).

**6.1. A verified fact that simplifies degrees 5 and 6.** We computed, in GAP,
the full set of cycle types occurring in each of the five transitive subgroups
of $S_5$ and each of the sixteen of $S_6$, and checked pairwise that **no two
share a cycle-type set** (the identical-pair check returns empty in both
degrees). Concretely, in degree 5 the five sets are
$\{(5)\}$, $\{(5),(2,2,1)\}$, $\{(5),(2,2,1),(4,1)\}$,
$\{(5),(3,1,1),(2,2,1)\}$, and
$\{(5),(3,1,1),(2,2,1),(4,1),(3,2)\}$ for $C_5,D_{10},F_{20},A_5,S_5$
respectively — a nested chain that each step extends by exactly one new cycle
type (here $(3,1,1)$ is the degree-$5$ form of a $3$-cycle; in degree $6$ the
same permutation type is $(3,1,1,1)$); in degree 6 the sixteen sets are all
distinct (the table in the accompanying log lists them). The consequence is
that, *for these two degrees alone*, once the set of Frobenius cycle types is
known to be complete, it uniquely determines the transitive group, and the
identification reduces to matching one of twenty-one fixed sets. This is a
low-degree accident: it is not true in general that cycle types determine a
transitive group, and the general algorithm must not rely on it. What it does
mean for the computer-algebra reader is that degrees five and six are the
cleanest possible setting for the Frobenius-cycle-type method, and the examples
of §5 are exactly of this form.

**Complexity, stated honestly.** Several distinct complexity statements are
often blurred together, and we separate them. (i) **Factorization** over
$\mathbb{Q}$ is polynomial-time in the bit-size of the input (Step 0).
(ii) **Discriminant** computation is polynomial-time (Step 1). (iii)
**Resolvent construction** — forming $R(T)=\prod_{\bar g\in S_n/H}(T-g\theta)$
— costs polynomial-time in the degree of $R$ and the height of its
coefficients for fixed $n$. (iv) **Exact group determination** is the
subtle step. For **fixed** degree $n$, there are only finitely many transitive
subgroups of $S_n$ (a constant depending on $n$), each resolvent has degree
bounded by a function of $n$ alone, and each factorization is polynomial-time,
so the *deterministic* resolvent-descent algorithm is polynomial in the
bit-size of the coefficients. The important qualification: the *practical*
method of "sampling small primes until the cycle types identify the group"
(Step 2) is **not itself** a deterministic polynomial-time proof — a finite
sample gives a subset of the Frobenius classes, and in the worst case an
unlucky sample may miss the separating cycle type. A deterministic
polynomial-time guarantee for the identification requires the resolvent
descent (Step 3) to provide a certificate, not prime sampling alone. For
**general** $n$ the picture is less comfortable: the resolvent degrees grow
factorially with $n$, the number of transitive subgroups of $S_n$ grows
rapidly, and the naive resolvent method is not polynomial in $n$. The
complexity of computing the Galois group as a function of $n$ is a genuine
research topic, and we do not overclaim a polynomial bound in $n$ here. What
is true and useful — and what the examples in §5 instantiate — is the
fixed-degree, deterministic, polynomial-time statement, which is the regime in
which degrees five and six live.

---

## 7. The Bring–Jerrard reduction and the base-field trap

A large part of the classical theory of the quintic is organized around the
**Bring–Jerrard form** $x^5+ax+b=0$. The theorem, due to Bring and Jerrard, is
that *every* quintic can be transformed into Bring–Jerrard form by a
Tschirnhaus transformation. The appeal is obvious: two parameters instead of
five, and the form is adapted to the elliptic-function solution of Hermite.

A caution that is easy to miss, and that a computer-algebra reader should not:
the statement is often (and wrongly) sharpened to "the transformation
coefficients are expressible by square roots only." That is too strong, and in
the naive formulation it is false. We can see the degrees of the parameter
equations directly. Write the quintic in depressed form
$t^5+pt^3+qt^2+rt+s$ (the $x^4$ term is removed by the rational shift
$x=y-p/5$). A **quadratic** Tschirnhaus transformation $y=x^2+ux+v$ kills the
$y^4$ and $y^3$ terms; the two conditions are linear in $v$ and quadratic in
$u$ (after $v=\tfrac{2}{5}p$ is substituted, $u$ satisfies
$2pu^2+6qu+4r-\tfrac{6}{5}p^2=0$), so this
stage is solvable by square roots — but it leaves a $y^2$ term, giving the form
$y^5+Ay^2+By+C$, not yet $y^5+ay+b$. To remove the $y^2$ term one uses a
**cubic** Tschirnhaus transformation $z=x^3+ux^2+vx+w$; eliminating $w$ (linear)
and then $v$ from the two remaining conditions gives, for the leading parameter
$u$, an equation of **degree $6$** — a sextic, not solvable by radicals in
general. So the reduction is a *Tschirnhaus transformation*, not a radical
solution of the original quintic, and the blanket "square roots only" claim
conflates several distinct statements: (i) one can reduce the general quintic
to Bring–Jerrard form; (ii) some preliminary Tschirnhaus steps use low-degree
(radical) operations; (iii) the resulting transformation parameters have
explicit algebraic constructions of bounded (but not quadratic) degree; and
(iv) the reduction is *not itself* a radical solution of the general quintic.
These must be kept separate.

There is, however, a second and more subtle base-field trap that a
computer-algebra reader should not fall into, and we state it precisely. The
Tschirnhaus transformation that produces $a$ and $b$ generally does **not**
have rational coefficients; its parameters live over an algebraic extension of
$\mathbb{Q}$ (of the degrees just discussed, in general of degree up to $6$).
Consequently the Galois group of the Bring–Jerrard form $x^5+ax+b$ *over
$\mathbb{Q}$* is not the same object as the Galois group of the original
quintic over $\mathbb{Q}$. The clean statement is that the transformation is an
isomorphism of the relevant extensions **over the field generated by the
transformation parameters**, and the Galois group is preserved over that larger
base field. If one computes the Galois group of $x^5+ax+b$ over $\mathbb{Q}$
without remembering that $a,b$ are not rational, one is computing the wrong
group. This is not a cosmetic point: it is exactly the reason that the
Bring–Jerrard reduction, though it simplifies the *equation*, does not by
itself simplify the *Galois-group computation* over $\mathbb{Q}$. The
reduction is the right tool for the *solution* (Hermite's elliptic-function
method works on the reduced form), and the wrong tool if one conflates it with
the *group-theoretic classification* over the original base field.

We flag the same caution for the icosahedral method of §8: it is a solution
method that changes the base field and the function field in which the inversion
is performed, and its "solution" is by elliptic (hence transcendental) means,
not by radicals.

---

## 8. Solving the solvable cases: Hermite, Klein, and the icosahedron

For the three solvable transitive types, the radical criterion of §2 is not
merely a decision procedure; it is a *construction*. The classical
constructions, which we summarize because they are the historical and
computational heart of the subject:

- **$C_5$, $D_{10}$, $F_{20}$.** These are the groups for which the roots are
  expressible by radicals in the strict sense. The construction proceeds by the
  tower of cyclic extensions guaranteed by the criterion. In the $F_{20}$ case
  the group has a normal $C_5$ subgroup with cyclic $C_4$ quotient, so the
  corresponding tower consists of a cyclic quartic subextension (itself a tower
  of two quadratic extensions) topped by a cyclic quintic extension; as with
  the $C_5$ case, the quintic top becomes a Kummer extension once $\zeta_5$ is
  adjoined. In practice, and in the computer-algebra systems, the roots of a
  solvable quintic are expressed by a finite combination of radicals and the
  roots of lower-degree resolvents; the systems (Sage, Magma, PARI) implement
  this via the same resolvent machinery of §6, specialized to the solvable
  case.

- **$A_5$ (and the general quintic) by elliptic functions — Hermite, 1858.**
  Hermite showed that the general quintic can be solved using elliptic
  functions: one reduces to the Bring–Jerrard form, constructs an associated
  elliptic curve whose $j$-invariant is a rational function of the coefficients,
  and inverts a certain elliptic modular function. The inversion is the
  non-algebraic step, and it is what makes this a *solution* in the broad sense
  (the roots are expressed in terms of known transcendental functions) rather
  than a radical solution.

- **The icosahedral equation — Klein, 1884.** Klein's geometric reformulation
  identifies the $A_5$ that governs the general quintic with the rotation group
  of the icosahedron. The "icosahedral equation" is a certain equation whose
  Galois group is $A_5$, and Klein shows it can be solved by reducing to a
  binary icosahedral invariant problem and then inverting a modular function.
  The modern reading, which is the one that matters for computation, is that
  the icosahedral method is an *explicit* solution of the $A_5$ case in terms
  of the hypergeometric and modular functions, and that the transcendental
  inversion can be replaced by a purely iterative (hence computable) procedure.
  This is the bridge between the $19$th-century theory and the modern
  "solve by iteration" algorithms: the same $A_5$ that Abel–Ruffini declares
  unsolvable *by radicals* is exactly the group that the icosahedral/elliptic
  method solves *by transcendental functions*.

The two threads — "unsolvable by radicals" (Abel–Ruffini) and "solvable by
elliptic functions" (Hermite–Klein) — are not a contradiction; they answer
different questions. The first asks whether the roots lie in a radical
extension of $\mathbb{Q}$; the second asks whether they can be expressed in
terms of a chosen family of transcendental functions. The Galois group $A_5$
is the invariant that both questions are about.

---

## 9. Applications

We sketch the principal applications, each of which is a direct consequence of
the classification and the radical criterion.

**Constructibility and the classical problems.** The constructible numbers are
precisely those lying in a tower of quadratic extensions of $\mathbb{Q}$, so
the constructible degrees are powers of $2$. Galois theory explains, in one
line, why angle trisection (degree $3$) and doubling the cube (degree $3$, and
in fact the relevant cubic is irreducible with a non-power-of-$2$ degree) are
impossible with straightedge and compass: the required extensions are not
towers of quadratics. The same machinery shows which regular $n$-gons are
constructible. By the Gauss–Wantzel theorem, a regular $n$-gon is constructible
if and only if
$$n = 2^{k}\,p_1\,p_2\cdots p_r,$$
where $k\ge 0$ and the $p_i$ are **distinct** Fermat primes (primes of the form
$2^{2^m}+1$). The full criterion needs both the power-of-two factor and the
distinctness: the cyclotomic Galois group $(\mathbb{Z}/n\mathbb{Z})^{\times}$
must be a $2$-group (a $2$-power order, which is what straightedge-and-compass
construction requires), and that happens precisely when the odd part of $n$ is
a product of distinct Fermat primes. (The currently known Fermat primes are
$3,5,17,257,65537$. So, for instance, the $15$-gon ($15=3\cdot5$) and the
$17$-gon are constructible, while the $9$-gon ($9=3^2$, a repeated prime) and
the $27$-gon are not.)

**Identification and solution of solvable quintics.** Given a concrete quintic,
the pipeline of §6 decides in polynomial time (in the coefficient bit-size)
whether it is solvable by radicals, and if so produces the radical expression.
This is a routine computation in the major systems, and it is the practical
payload of the entire theory: most "solvable quintics" that appear in
applications (characteristic polynomials of matrices with special structure,
minimal polynomials in number fields) are detected and solved this way.

**Cryptography (a modest connection).** There is a genuine, but often
overstated, connection between Galois theory and modern cryptography. The
relevant object in isogeny-based and pairing-based cryptography is not the
solvability-by-radicals of a low-degree polynomial, but the **Galois
representations** and **Frobenius conjugacy classes** that arise in the
arithmetic of elliptic curves and the algebraic structures underlying several
cryptographic constructions. Concretely, the extension of a finite field
generated by the torsion points of an ellipt curve (or by the field of
definition of an isogeny) carries a Galois action, and the Frobenius element
(or its conjugacy class) in that Galois group encodes arithmetic information
used in the design and analysis of isogeny-based and pairing-based protocols.
The connection is principally through representations and field extensions —
and through the structure of the relevant Galois groups — rather than through
the radical solvability of quintic or sextic equations. The lesson of the
quintic and sextic cases transfers in a limited but real way: the relevant
group is a concrete permutation (or linear) group, and identifying it is a
finite, computable problem once the right invariants are chosen. We record the
connection as an application of the *machinery* (Galois groups, Frobenius
classes, field extensions) rather than as a claim that solvability-by-radicals
is a hardness parameter for these cryptographic problems.

**Complexity and invariants.** The Galois group is a canonical invariant of a
polynomial, and the question of the complexity of computing it (as a function
of the degree $n$) is a standing problem at the interface of algebra and
complexity theory. The fixed-degree polynomial-time result of §6 is the
baseline; the general-degree problem is where the open questions live, and it
is one of the places where the computer-algebra and the pure-mathematics
viewpoints meet most directly.

---

## 10. Limitations, caveats, and what is open

We close by separating, explicitly, what this exposition has *established* from
what it has merely *described*, and by naming the limitations.

1. **The classification is complete; the small-coefficient representatives are
   not.** Tables 1 and 2 are complete and were verified by independent group
   enumeration in GAP. Tables 3 and 4 give verified representatives for all
   five quintic types and for nine of the sixteen sextic types. The seven
   sextic types without a small-coefficient representative in our search are
   recorded as such; we do not claim to have exhibited them by direct
   computation.

2. **The Bring–Jerrard and icosahedral methods change the base field.** As
   argued in §7, the reduced form and the icosahedral equation live over a
   larger base field than $\mathbb{Q}$, and the Galois group over that larger
   field is not the Galois group over $\mathbb{Q}$ of the original. Any
   statement that "the quintic is solvable" by these methods must be read as a
   statement about the extension of the base field that the method introduces,
   and about a transcendental (not radical) expression.

3. **The radical criterion is an equivalence over characteristic $0$.** The
   forward direction (radical $\Rightarrow$ solvable group) holds in all
   characteristics; the reverse direction (solvable group $\Rightarrow$ radical
   expression) uses the existence of the roots of unity and is the statement
   that is specific to characteristic $0$ (or to a base field containing the
   relevant roots of unity). We work over $\mathbb{Q}$, so the equivalence is
   the one we use, but the caveat is worth stating for the general reader.

4. **Computing the Galois group for general degree is not solved in the
   polynomial-in-$n$ sense.** The fixed-degree result is clean; the
   general-degree complexity is open, and the naive resolvent method is
   factorial in the degree. We do not claim a polynomial-in-$n$ bound.

5. **The two $S_4$'s in degree $6$ are a warning.** They have the same abstract
   structure ($S_4$) and the same order ($24$), so an implementation that stops
   at "the group is $S_4$" has computed an *incomplete* answer in degree $6$.
   The two representations are separated by the point-stabilizer structure
   ($C_2\times C_2$ vs $C_4$) and, equivalently, by the cycle-type set
   (§4) — but only because in degree $6$ the cycle-type sets happen to be
   unique; the abstract group alone never suffices, and in higher degrees
   distinct transitive groups can share cycle-type sets, where the point
   stabilizers or a resolvent are then required.

The open problems, in short, are: the general-degree complexity of Galois-group
computation; the explicit, uniformly effective construction of the radical
expressions for the solvable cases (as opposed to their existence); and the
refinement of the invariants that separate the genuinely distinct permutation
representations that share an abstract group (the two $S_4$'s being the
minimal example).

---

## 11. Conclusion

Galois theory converts the analytic question "can the roots of this quintic or
sextic be written by radicals?" into the algebraic question "is the transitive
permutation group on the complex roots a solvable group?" For degree five the
answer space is the five transitive subgroups of $S_5$, of which three are
solvable; for degree six it is the sixteen of $S_6$, of which twelve are
solvable. The classification is complete and was verified here by independent
group enumeration, and we exhibited, by direct computation, a representative
polynomial for every quintic type and for nine of the sextic types, with
discriminants and Frobenius cycle types. The computer-algebra content —
irreducibility by modular reduction and LLL, the discriminant test, Frobenius
cycle types from the Dedekind factorization pattern, and the resolvent descent
through the subgroup lattice — is polynomial-time for fixed degree, and it is
the machinery that makes the classification a computation rather than merely a
theorem. The limits are equally clear: the Bring–Jerrard and icosahedral
solution methods change the base field and use transcendental rather than
radical expressions; the small-coefficient representatives do not cover all
sixteen sextic types; and the general-degree complexity of the problem remains
open. Degrees five and six are, in the end, the first degrees at which a
nonsolvable transitive Galois group occurs — degree four and below admit only
solvable transitive groups, which is why the classical formulas stop there —
and they remain the cleanest place to see the bridge between the Galois group
of the complex roots and the possibility of solving the equation.

---

## Appendix A. Reproducing the computations (and a corrected API note)

Every number in the paper was produced by an executable script; this appendix
records the working API and the exact commands. The environment is
`SageMath 10.9` (`sagemath/sagemath:latest`) for the polynomial-side
computations (Galois groups of specific polynomials, discriminants, and
Frobenius cycle types from the Dedekind factorization pattern) and
`GAP 4.11.1` (`gapsystem/gap-docker:latest`) for the transitive-group
enumeration.

**A.1. Native Sage — the working API (SageMath 10.9).**

```python
R.<x> = QQ[]                      # rational polynomial ring
f = x^5 - 5*x - 5                 # an example quintic
G = f.galois_group()              # returns a TransitiveGroup (or (G, gens))
if isinstance(G, tuple): G = G[0]
G.order()                         # -> 120
G.is_solvable()                   # -> False
G.structure_description()         # -> "S5"
f.discriminant()                  # -> 1153125
# Frobenius cycle type at a prime p not dividing the discriminant:
fs = f.change_ring(GF(p)).factor()
tuple(sorted([P.degree() for P, _ in fs], reverse=True))   # e.g. (3,2)
```

**A.1a. The Sage API is version- and object-specific (a caution).** A number
of guides (and the one attached to this work) suggest `G.transitive_label()` to
read off the label of the transitive group. Whether that call works depends on
**which Sage object is returned** and on the **Sage version** — and this is the
kind of detail that is easy to get wrong, because the *name* of a plausible
method is easy to invent. In the tested SageMath 10.9 environment we probed
both entry points directly:

- `Polynomial.galois_group()` returns a `TransitiveGroup` object that has
  `order()`, `is_solvable()`, `structure_description()`, and
  `transitive_number()`, but **not** `transitive_label()` (and not
  `cycle_type()`).
- `NumberField(...).galois_group()` returns a `GaloisGroup_v2` object that has
  all of the above **and** `transitive_label()` (it returned, e.g., `"5T5"`
  for $x^5-5x-5$).

So the "cheat sheet" is correct for the number-field API and incorrect for the
polynomial API; the defensible statement is that the exact method set depends
on the object returned and the Sage version, and the only reliable check is to
probe the object. For the transitive label one may therefore use
`NumberField(f).galois_group().transitive_label()`, or match
`structure_description()` and `order()` against the verified Tables 1 and 2, or
query GAP directly.

**A.1b. Exact transitive labels (verified, SageMath 10.9, number-field API).**
Using `NumberField(f).galois_group().transitive_label()` we confirmed the
labels of every representative in §5:

| representative | label | structure_description | order | solvable |
|----------------|-------|-----------------------|-------|----------|
| $x^5+x^4-4x^3-3x^2+3x+1$ | $5T_1$ | $C_5$ | $5$ | yes |
| $x^5-5x+12$ | $5T_2$ | $D_5$ | $10$ | yes |
| $x^5-5$ | $5T_3$ | $C_5:C_4$ | $20$ | yes |
| $x^5-5x^4-5x^3+4x^2+x-5$ | $5T_4$ | $A_5$ | $60$ | no |
| $x^5-5x-5$ | $5T_5$ | $S_5$ | $120$ | no |
| $x^6-x^3+1$ | $6T_1$ | $C_6$ | $6$ | yes |
| $x^6+3$ | $6T_2$ | $S_3$ | $6$ | yes |
| $x^6-3x^3-1$ | $6T_3$ | $D_6$ | $12$ | yes |
| $x^6-3x^3+3$ | $6T_5$ | $C_3\times S_3$ | $18$ | yes |
| $x^6-3x^3-3$ | $6T_9$ | $S_3\times S_3$ | $36$ | yes |
| $x^6-3x+5$ | $6T_{11}$ | $C_2\times S_4$ | $48$ | yes |
| $x^6-3x+3$ | $6T_{13}$ | $(S_3\times S_3):C_2$ | $72$ | yes |
| $x^6-4x^4-x^3-3x^2+4x-1$ | $6T_{15}$ | $A_6$ | $360$ | no |
| $x^6-3x^3-3x-3$ | $6T_{16}$ | $S_6$ | $720$ | no |

These agree with the GAP enumeration of Tables 1 and 2.

**A.2. Raw GAP — only for the transitive-group library.** The polynomial-side
Galois groups were computed in native Sage; GAP was used only where the
transitive-group library is authoritative:

```gap
LoadPackage( "TransGrp" );                 # or the transitive_groups package
g := TransitiveGroup( 6, 12 );             # the transitive A5 (6T12)
Size( g );                                  # -> 60
IsSolvableGroup( g );                       # -> false
StructureDescription( g );                  # -> "A5"
Stabilizer( g, 1 );                         # point stabilizer, e.g. D10
```

The full enumeration of the five and sixteen groups, and the cycle-type sets
used in §6.1, are in the scripts `enumerate2.g`, `cyc5.g`, and `cyc6_all.g`
in the accompanying log.

**A.3. Why the split.** The split between "native Sage for polynomials" and
"raw GAP for the group library" is deliberate. Sage's `f.galois_group()`
handles the polynomial-side reduction, resolvent, and group-recognition steps
end-to-end and is the right tool for the examples of §5. GAP is the
authoritative source for the *list* of transitive groups and their
representations (point stabilizers, cycle-type sets), which is what Tables 1
and 2 and §6.1 depend on. Driving GAP through Sage's `gap()` interface is
possible but fragile (string marshalling and version drift), so the GAP
scripts were run standalone against the `gapsystem/gap-docker` image.

---

## References

1. N. H. Abel, *Recherches sur les conditions de résolubilité des équations
   par radicaux*, J. für reine und angew. Math. (Crelle) **1** (1826), 5–31.
2. E. Galois, *Mémoire sur les conditions de résolubilité des équations par
   radicaux*, J. de Mathématiques pures et appliquées (Liouville) **11**
   (1846), 381–414.
3. E. Bring, *Recherches sur les équations*, J. für reine und angew. Math.
   (Crelle), 1831.
4. C. G. Jerrard, *The General Solution of Equations of the Fifth Degree*,
   2 vols., Edinburgh, 1832.
5. C. Hermite, *Sur la résolution de l'équation du cinquième degré*, C.R.
   Acad. Sci. Paris **46** (1858), 508–510.
6. F. Brioschi, *Sulla risoluzione dell'equazione del quinto grado*, Annali
   di Mat. pura ed appl. **1** (1858), 256–259; 326–328.
7. F. Klein, *Lectures on the Icosahedron and the Solution of Equations of the
   Fifth Degree*, Teubner, Leipzig, 1884; English trans. A. Miller, Ginn & Co.,
   1888; AMS reprint, 1988.
8. L. E. Dickson, *On the solvable quintic*, Trans. Amer. Math. Soc. **2**
   (1901), 393–400.
9. B. L. van der Waerden, *Moderne Algebra*, 2 vols., Springer, 1930; English
   trans. *Modern Algebra*, Ungar, 1953.
10. E. Artin, *Galois Theory*, 3rd ed., Wiley, New York, 1964.
11. H. Zassenhaus, *On the group of an equation*, in *Computers in Algebra and
    Number Theory*, SIAM–AMS Proc. **7** (1971), 69–88.
12. A. K. Lenstra, H. W. Lenstra Jr., L. Lovász, *Factoring polynomials with
    rational coefficients*, Math. Ann. **261** (1982), 515–534.
13. H. Cohen, *A Course in Computational Algebraic Number Theory*, Graduate
    Texts in Mathematics 138, Springer, 1993.
14. S. Lang, *Algebra*, 3rd rev. ed., Graduate Texts in Mathematics 211,
    Springer, 2002.
15. J. von zur Gathen, J. Gerhard, *Modern Computer Algebra*, 3rd ed.,
    Cambridge University Press, 2013.
16. A. Hulpke, *Techniques for the computation of Galois groups*, Colorado
    State University.
17. A. Bostan, P. Gaudry, É. Schost, *Linear recurrences with polynomial
    coefficients and application to integer factorization and Cartier–Manin
    operator*, SIAM J. Comput. **36** (2007), 1777–1806.
