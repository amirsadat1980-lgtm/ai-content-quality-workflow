"""AI Content Quality Workflow — evaluate and auto-revise written content
against structured, configurable quality criteria.
"""

from .criteria import QualityCriteria
from .workflow import evaluate, run_workflow

__all__ = ["QualityCriteria", "evaluate", "run_workflow"]

__version__ = "0.1.0"
