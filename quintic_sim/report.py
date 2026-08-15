"""S7 — report assembly and rendering (Markdown + JSON)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Sequence, Union

from .galois import GroupResult
from .factor import FactorResult
from .normalform import NormalFormResult


@dataclass
class StepTrace:
    stage: str            # S0..S7
    name: str             # human-readable stage name
    detail: str           # what was computed + algorithm used
    duration: float       # wall seconds

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Report:
    input: str
    method: str                                   # radicals | special | reducible
    verified: bool
    reducible: bool
    group: Optional[GroupResult]
    normal_form: NormalFormResult
    factor_result: FactorResult
    roots: List[dict]                             # {expr, numeric, verified, detail}
    warnings: List[str]
    step_traces: List[StepTrace]
    sage: Optional[dict] = None                   # cross-check result (if run)
    special: Optional[dict] = None                # bring_radical / klein (S4b)
    numeric_source: str = "abarth"                # S5 primary method used
    durand_iterations: Optional[int] = None       # S5 educational trace

    # ---------- JSON ----------
    def to_dict(self) -> dict:
        return {
            "input": self.input,
            "method": self.method,
            "verified": self.verified,
            "reducible": self.reducible,
            "group": None if self.group is None else asdict(self.group),
            "normal_form": {
                "depressed": str(self.normal_form.depressed.as_expr()),
                "shift": str(self.normal_form.shift),
                "palindromic": self.normal_form.palindromic,
                "notes": list(self.normal_form.notes),
            },
            "factorization": [
                {"factor": str(f.as_expr()), "multiplicity": m}
                for f, m in self.factor_result.factorization
            ],
            "rational_roots": [str(r) for r in self.factor_result.rational_roots],
            "roots": self.roots,
            "warnings": self.warnings,
            "step_traces": [t.to_dict() for t in self.step_traces],
            "sage": self.sage,
            "special": self.special,
            "numeric_source": self.numeric_source,
            "durand_iterations": self.durand_iterations,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    def write_json(self, path: Union[str, Path]) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")

    # ---------- Markdown ----------
    def to_markdown(self) -> str:
        L: List[str] = []
        L.append("# Quintic Solver Report")
        L.append("")
        L.append(f"**Input:** `{self.input}`  ")
        L.append(f"**Method:** {self.method}  ")
        L.append(f"**All roots verified:** {'✅ yes' if self.verified else '⚠️ no'}  ")
        L.append(f"**Reducible over Q:** {'yes' if self.reducible else 'no'}")
        L.append("")

        if self.normal_form.palindromic and self.normal_form.palindromic_reduction:
            pr = self.normal_form.palindromic_reduction
            L.append("## Normal form (S1)")
            L.append("")
            L.append(f"Depressed quintic: `{self.normal_form.depressed.as_expr()}` "
                     f"(shift x = y + {self.normal_form.shift})")
            L.append("")
            L.append(f"> **Palindromic reduction (corrected):** {pr.note}")
            L.append(f"> t-quadratic: `{pr.t_quadratic.as_expr()}` "
                     f"(t = x + 1/x), t-roots: {list(pr.t_roots)}")
            L.append("")

        if self.group is not None:
            g = self.group
            L.append("## Galois group (S3)")
            L.append("")
            L.append(f"**Group:** {g.name} (order {g.order}, "
                     f"{'⊆' if g.in_A5 else '⊄'} A5, "
                     f"{'solvable' if g.solvable else 'NOT solvable'})")
            L.append(f"**Discriminant:** {g.discriminant} "
                     f"({'square' if g.disc_square else 'not a square'})")
            L.append(f"**Algorithm:** {g.method}")
            if self.sage is not None:
                L.append(f"**Sage cross-check:** {self.sage.get('detail', '')} "
                         f"(status: {self.sage.get('status')})")
            L.append("")

        L.append("## Factorization (S2)")
        L.append("")
        fr = self.factor_result
        if fr.reducible:
            L.append(f"`{self.input}` = " + " · ".join(
                f"`{f.as_expr()}`" + (f"^{m}" if m > 1 else "")
                for f, m in fr.factorization
            ))
        else:
            L.append(f"`{self.input}` is **irreducible over Q** (single "
                     f"factor of degree {fr.factorization[0][0].degree() if fr.factorization else 5}).")
        if fr.rational_roots:
            L.append(f"Rational roots: {list(fr.rational_roots)}")
        for n in fr.notes:
            L.append(f"- {n}")
        L.append("")

        if self.special:
            L.append("## Special-function forms (S4b)")
            L.append("")
            if self.special.get("bring_radical"):
                L.append(f"**Bring radical:** {self.special['bring_radical']}")
            if self.special.get("klein"):
                L.append(f"**Klein icosahedral:** {self.special['klein']}")
            L.append("")

        L.append("## Roots (S4/S5)")
        L.append("")
        L.append("| # | exact | numeric (15 digits) | verified |")
        L.append("|---|-------|---------------------|----------|")
        for i, r in enumerate(self.roots):
            L.append(f"| {i} | `{r['expr']}` | {r['numeric']} | "
                     f"{'✅' if r['verified'] else '⚠️ ' + r['detail']} |")
        L.append("")

        L.append("## Numerical roots (S5)")
        L.append("")
        src = self.numeric_source
        src_txt = (
            "mpmath **Aberth** method (50-digit arbitrary precision)"
            if src == "abarth"
            else "NumPy **companion-matrix** eigenvalues (machine "
                 "precision — Aberth did not converge on multiple roots)"
        )
        L.append(f"Primary method: {src_txt}; cross-checked against the "
                 f"other method; **Durand–Kerner** (Weierstrass) "
                 f"converged in {self.durand_iterations} iterations for "
                 "the simulator trace.")
        L.append("")

        L.append("## Verification (S6)")
        L.append("")
        L.append("Every exact root was validated by (1) a high-precision "
                 "residual check and (2) an independent numeric "
                 "cross-match before being reported. "
                 + ("All roots passed. ✅" if self.verified
                    else "⚠️ Some roots required fallback forms — see warnings."))
        L.append("")

        if self.warnings:
            L.append("## Warnings")
            L.append("")
            for w in self.warnings:
                L.append(f"- ⚠️ {w}")
            L.append("")

        L.append("## Step trace")
        L.append("")
        L.append("| stage | step | detail | time (s) |")
        L.append("|-------|------|--------|----------|")
        for t in self.step_traces:
            detail = t.detail.replace("|", "\\|").replace("\n", " ")
            L.append(f"| {t.stage} | {t.name} | {detail} | {t.duration:.3f} |")
        L.append("")
        return "\n".join(L)
