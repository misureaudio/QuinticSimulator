"""quintic_sim — a Quintic Solver Simulator.

Walks a degree-5 polynomial with rational coefficients through the full
decision tree of QuinticMethods_v1.md: factorization, Galois-group
classification, and the matching solution path (radicals / exact
algebraic numbers / numerics), with a step-by-step trace.

Public API:
    simulate(coeffs, use_sage=False) -> Report
"""

from .pipeline import simulate
from .report import Report, StepTrace
from .errors import PipelineError

__version__ = "0.1.0"
__all__ = ["simulate", "Report", "StepTrace", "PipelineError"]
