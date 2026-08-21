"""quintic_sim_gfx — a Quintic Solver Simulator (with an optional GUI).

Walks a degree-5 polynomial with rational coefficients through the full
decision tree of QuinticMethods_v1.md: factorization, Galois-group
classification, and the matching solution path (radicals / exact
algebraic numbers / numerics), with a step-by-step trace.

Public API (lazily imported so that importing this package — or the
``gui`` subpackage — never loads sympy/numpy):
    simulate(coeffs, use_sage=False) -> Report
"""

from importlib import import_module

__version__ = "0.1.0"
__all__ = ["simulate", "Report", "StepTrace", "PipelineError"]

# name -> (submodule, attribute)
_LAZY = {
    "simulate": (".pipeline", "simulate"),
    "Report": (".report", "Report"),
    "StepTrace": (".report", "StepTrace"),
    "PipelineError": (".errors", "PipelineError"),
}


def __getattr__(name):
    if name in _LAZY:
        mod_name, attr = _LAZY[name]
        return getattr(import_module(mod_name, __name__), attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(list(globals()) + list(_LAZY))
