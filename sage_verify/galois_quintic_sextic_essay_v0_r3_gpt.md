# Galois quintic sextic v0 review 3

Yes. **The essay is broadly mathematically competent and gets the central Galois-theoretic picture right, but it is not yet reliable enough for publication to an expert audience.** I would rate it around **7/10 for mathematical accuracy**: the core theory and most of the concrete examples are good, while several fairly technical claims are either wrong, overstated, or insufficiently qualified.

I also independently checked the listed polynomial examples computationally; the advertised Galois groups and discriminants are consistent with the polynomials. Sage's current documentation also confirms that the degree-5/6 transitive-group framework and the specific examples such as $x^5-2\mapsto 5T3$ and a generic quintic $\mapsto S_{5}$ are standard. ([Documentazione SageMath][1])

## What is solid

The following parts are essentially correct.

**1. The opening distinction between “over (\mathbb C)” and “over (\mathbb Q)” is exactly the right one.** The essay correctly explains that the interesting object is
$$
\operatorname{Gal}(L/\mathbb Q)\le S_{n}
$$
acting on the complex roots, not a Galois group “over $\mathbb C$.” The only wording I would change is “the only extension of $\mathbb C$ is $\mathbb C$ itself” to “the only **algebraic** extension of $\mathbb C$ is $\mathbb C$ itself.”

**2. The solvability criterion is stated correctly for the intended setting.** Over characteristic (0), solvability by radicals is equivalent to solvability of the Galois group. The discussion of the appearance of $A_{5}$ and ($S_{5}$) in degree (5) is sound.

**3. The quintic classification is correct.** The five transitive subgroups of ($S_{5}$) and their orders,
$$
C_{5},\ D_{10},\ F_{20},\ A_{5},\ S_{5},
$$
with the split (3) solvable / (2) nonsolvable, are right. The discriminant and Frobenius-cycle discussion is also basically correct. An independent transitive-subgroup table confirms the same structure and cycle types. ([Department of Mathematics][2])

**4. The sextic classification is basically correct.** There are sixteen transitive subgroups of $S_{6}$, with twelve solvable and four nonsolvable. The phenomenon of the two non-equivalent transitive (S_4) representations is an excellent point for a computer-algebra audience. The listed orders and the basic structural identifications are consistent with the standard transitive-group tables. ([Department of Mathematics][2])

**5. The concrete polynomial examples are, for the most part, genuinely good.** I independently checked the discriminants and Galois groups of the quintic and sextic examples computationally. In particular:

* $x^5-5$ gives $F_{20}$,
* $x^5-5x-5$ gives $S_{5}$,
* the proposed $A_{5}$ quintic has square discriminant and Galois group $A_{5}$,
* the listed sextic examples give the stated $C_{6},S_{3},D_{12},C_{3}\times S_{3},\ldots,A_{6},S_{6}$ groups.

That is a substantial strength of the essay.

**6. The Frobenius-factorization principle is right.** For an unramified prime, the factor degrees modulo (p) give the cycle structure of a Frobenius element. The warning that a finite sample of primes is not automatically a proof of the complete group is also conceptually important.

**7. The essay is commendably honest about incomplete sextic examples.** It does not pretend to have produced representatives for all sixteen groups when it only has nine. That is good scholarly practice.

---

## The important problems

## 1. There is a definite algebra error: Out(A5)=1

This sentence is wrong:

> “the $A_{5}$ case has no such component, since ($\operatorname{Out}A_{5}=1$).”

In fact
$$
\operatorname{Aut}A_{5}\cong S_{5},\qquad \operatorname{Inn}A_{5}\cong A_{5},
$$
so
$$
\operatorname{Out}A_{5}\cong C_{2}.
$$

This is not merely a notation issue. It should be corrected because it occurs in a sophisticated discussion of the exceptional outer automorphism of $S_{6}$, where an expert reader is likely to notice it immediately.

This is probably the clearest “hard error” in the essay.

---

## 2. The statement that a cyclic quintic is “a Kummer extension of a quadratic field” is wrong

The essay says:

> “A cyclic quintic is a Kummer extension of a quadratic field.”

That is not the correct Kummer description.

For a cyclic extension of degree (5), the natural Kummer base is a field containing the fifth roots of unity, namely something involving
$$
\mathbb Q(\zeta_5),
$$
which has degree (4) over $\mathbb Q$, not (2).

There is a quadratic subfield
$$
\mathbb Q(\sqrt5)\subset \mathbb Q(\zeta_5),
$$
but $\mathbb Q(\sqrt5)$ does **not** contain $\zeta_5$, so it is not the appropriate Kummer base merely by virtue of being the quadratic subfield.

I would replace that sentence with something along the lines of:

> A cyclic quintic becomes a Kummer extension after adjoining the fifth roots of unity; the relevant cyclotomic extension is $\mathbb Q(\zeta_5)/\mathbb Q$.

That would be mathematically clean.

---

## 3. The Bring–Jerrard section contains a serious overstatement about square roots

The essay claims:

> “every quintic can be transformed into Bring–Jerrard form by a Tschirnhaus transformation whose coefficients are expressible by square roots only.”

This is much too strong, and in the ordinary formulation it is false.

The Bring–Jerrard reduction uses nontrivial Tschirnhaus transformations. The coefficient determination is not simply a tower of quadratic radicals in the general case. In fact, the classical difficulty of the Tschirnhaus method is precisely that the equations for transformation parameters can themselves be difficult. One standard treatment explicitly notes that the naive cubic Tschirnhaus route leads to a sextic parameter equation that is not generally solvable by radicals. ([ResearchGate][3])

The essay appears to be conflating several different statements:

* one can reduce the general quintic to Bring–Jerrard form;
* some preliminary Tschirnhaus steps can be done with relatively low-degree radical operations;
* the resulting transformation parameters have some explicit algebraic constructions;
* the reduction is *not* itself a radical solution of the general quintic.

Those need to be kept distinct.

The later source material actually supports the existence of a sequence involving a quadratic transformation followed by a quartic Tschirnhaus transformation, rather than the blanket “square roots only” claim. ([UCLan - University of Central Lancashire][4])

---

## 4. The “resolvent root iff subgroup” statement needs correction

The essay says, roughly, that for a candidate subgroup (H),

> “(H) is a subgroup of (G) exactly when the resolvent has a root in the base field.”

That is too casual and, literally stated, wrong.

For a resolvent built from a (G)-set such as (G/H), the presence of a rational root is connected to **containment of (G) in a conjugate of a stabilizer**, not simply to the abstract statement $H\le G$. One has to keep track of which group is acting, which resolvent invariant is chosen, and whether one is talking about $G\subseteq H^g$ or $H^g\subseteq G$.

For an expert audience this distinction matters. The section should formulate the resolvent criterion using the subgroup lattice and fixed fields rather than the abbreviated “(H) is a subgroup exactly when…” wording.

---

## 5. There is a logical gap concerning finite Frobenius samples

The essay correctly says that observing cycle types at finitely many primes gives only a subset of the possible Frobenius classes. But later it says things like:

> “if the observed cycle types are contained in ({...}), the group is the transitive $A_{5}$.”

That conclusion does **not** follow from containment of a finite observed set.

An $A_{6}$ group can easily produce an initial sample consisting only of cycle types also occurring in the embedded $A_{5}$. To distinguish them, one needs either:

* an actually complete cycle-type set, or
* a resolvent/subfield certificate, or
* another rigorous group-identification invariant.

The essay itself knows this—the caveat in §6 is good—but the concrete wording in §4 slips past its own caveat.

---

## 6. The treatment of polynomial irreducibility and LLL is too simplistic

The sentence

> “The LLL step is what makes the whole process polynomial-time…”

is too sweeping.

LLL is indeed central in polynomial factorization over $\mathbb Q$, and the paper's computational narrative is reasonable, but the relationship between modular factorization, Hensel lifting, coefficient bounds, lattice reduction, and the overall complexity of Galois-group algorithms is considerably more nuanced.

For an expert audience, I would say something more like:

> Polynomial factorization over $\mathbb Q$ can be performed in polynomial time using modular factorization, lifting, coefficient bounds, and lattice-reduction techniques such as LLL.

That avoids implying that “the LLL step” single-handedly establishes the complexity claim.

---

## 7. The fixed-degree complexity claim is plausible, but the exposition overstates what has been demonstrated

The essay says:

> “For fixed degree (n), the entire pipeline runs in time polynomial in the bit-size of the coefficients…”

As a high-level computational-complexity statement, this is defensible in the fixed-degree setting, but the essay has not actually established it from the specific Sage workflow described.

In particular, the described practical method of “sample small primes until the cycle types identify the group” is not itself a deterministic polynomial-time proof. The essay properly acknowledges the sampling issue, but then moves too quickly from that observation to the full complexity statement.

There are also distinctions between:

* factorization complexity,
* discriminant computation,
* resolvent construction,
* exact Galois-group determination,
* randomized vs deterministic algorithms,
* fixed (n) vs variable (n).

An expert CS/computer-algebra audience will expect those distinctions.

---

## 8. The Sage API appendix is too version-specific and somewhat misleading

The appendix says that in Sage 10.9:

> `G.transitive_label()` does not exist

and contrasts this with the Galois-group object.

This is potentially true for the **particular object returned by the polynomial API in the tested environment**, but it should not be presented as a universal Sage statement.

Current Sage documentation does have `transitive_label()` on the relevant Galois-group object, and also `transitive_number()`. ([Documentazione SageMath][1])

More importantly, Sage's current documentation shows that `NumberField(...).galois_group()` can produce an object explicitly reporting labels such as `5T3` and `6T2`. ([Documentazione SageMath][1])

So the defensible statement is:

> “The exact method set depends on the Sage object returned and the Sage version; in the tested Sage 10.9 workflow, the raw permutation-group object did not expose the expected transitive-label method, whereas the number-field Galois-group API does.”

That is much stronger technically.

---

## 9. The cryptography paragraph is the weakest “application”

This part is substantially more speculative than the rest:

> “The structure of that group — and in particular whether it is solvable, and its composition factors — controls the difficulty…”

and

> “it is computed by the same resolvent-and-Frobenius machinery…”

That is not a good description of the role of Galois groups in modern pairing- or isogeny-based cryptography.

There **is** a genuine connection through Galois representations, torsion fields, Frobenius elements, and algebraic-number-theoretic structure. But the essay makes it sound as though the solvability of a permutation Galois group is a central hardness parameter for the cryptographic problems themselves. That is misleading.

I would either remove the paragraph entirely or rewrite it as a modest application:

> Galois representations and Frobenius conjugacy classes play a fundamental role in the arithmetic of elliptic curves and in the algebraic structures underlying several cryptographic constructions. The connection is principally through representations and field extensions rather than through solvability-by-radicals of low-degree polynomials.

That would be much safer.

---

## 10. The constructibility statement is oversimplified

The essay says regular polygons are constructible

> “those with Fermat-prime sides”

The full criterion is that
$$
n=2^k p_1p_2\cdots p_r
$$
where the (p_i) are **distinct Fermat primes**.

So the sentence needs the power-of-two factor and the “distinct” qualification.

---

## 11. “The quintic and sextic are the two smallest degrees at which the theory has genuine content” is rhetoric, not a good mathematical statement

Degree (4) already has rich Galois theory: $V_{4}$,$C_{4}$,$D_{4}$,$A_{4}$,$S_{4}$, resolvent theory, normal-subgroup structure, etc.

What is true—and what the essay presumably means—is:

> Degrees (5) and (6) are the first degrees in which nonsolvable transitive Galois groups occur.

That is a much better closing sentence.

---

## One particularly good feature

Ironically, the essay's strongest methodological point is also where it is most sophisticated:

> abstract group (\neq) permutation representation.

The discussion of the two $S_{4}$'s in degree (6) is exactly the kind of thing that an expert computer-algebra audience appreciates. Sage/GAP documentation likewise treats transitive groups as permutation groups with specific degree and numbering information, rather than merely as abstract isomorphism classes. ([Documentazione SageMath][5])

That is worth retaining.

---

## My assessment by section

| Section                   | Assessment                                                          |
| ------------------------- | ------------------------------------------------------------------- |
| §§1–2 basic Galois theory | **Very good**                                                       |
| §3 quintics               | **Very good**, one Kummer error                                     |
| §4 sextics                | **Good**, but contains the $OutA_{5}$ error and some overstatements |
| §5 computational examples | **Very good**; examples check out                                   |
| §6 algorithms/complexity  | **Good conceptual overview**, too categorical in places             |
| §7 Bring–Jerrard          | **Needs substantial revision**                                      |
| §8 Hermite/Klein          | **Mostly good**, but some historical/technical compression          |
| §9 applications           | **Mixed**; cryptography should be rewritten                         |
| §10 caveats               | **Good instinct**, but some caveats themselves need correction      |
| Appendix A                | **Useful**, but Sage API claims should be version/object-specific   |
| References                | **Adequate but could be substantially improved**                    |

## Bottom line

**Yes, it is reasonably accurate as a research-style draft. No, it is not yet accurate enough to hand to experts as-is.**

The important thing is that the flaws are **not primarily in the central Galois theory or in the computed degree-5/6 classification**. Those parts are surprisingly solid. The problems cluster around:

1. a few specialist algebra errors ($\operatorname{Out}A_{5}$, Kummer theory);
2. an incorrect/overstrong Bring–Jerrard statement;
3. overclaiming what finite Frobenius samples prove;
4. oversimplified algorithmic complexity claims;
5. an overconfident cryptography “application” paragraph.

With those corrected, I would consider the essay potentially quite good for the intended audience.

The most urgent fixes, in order, are **Bring–Jerrard**, **Kummer**, **$\operatorname{Out}A_{5}$**, and the **resolvent/Frobenius logical qualifications**.

[1]: https://doc.sagemath.org/html/en/reference/number_fields/sage/rings/number_field/galois_group.html?utm_source=chatgpt.com "Galois groups of number fields - Algebraic Numbers and Number Fields"
[2]: https://web.ma.utexas.edu/users/ikmartin/files/prelims/transitive_subgroup_tables.pdf?utm_source=chatgpt.com "The column (!) is marked with a (*) if the group is not solvable, and is marked with (□) if it is a subgroup of An."
[3]: https://www.researchgate.net/publication/268992597_Polynomial_transformations_of_Tschirnhaus_Bring_and_Jarrard?utm_source=chatgpt.com "(PDF) Polynomial transformations of Tschirnhaus, Bring and Jarrard"
[4]: https://knowledge.lancashire.ac.uk/12606/1/12606_simo.pdf?utm_source=chatgpt.com "Central Lancashire Online Knowledge (CLoK)"
[5]: https://doc.sagemath.org/html/en/reference/groups/sage/groups/perm_gps/permgroup_named.html?utm_source=chatgpt.com "“Named” Permutation groups (such as the symmetric group, S_n) - Groups"
