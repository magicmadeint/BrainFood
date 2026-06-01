"""
DEPRECATED: This file is kept for backward compatibility.

Please import from the top level instead:

    from brainfood.agent import BrainFoodAgent
"""

import warnings

warnings.warn(
    "brainfood.agent.brainfood_agent is deprecated. "
    "Use 'from brainfood.agent import BrainFoodAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

from brainfood.agent import BrainFoodAgent  # re-export the canonical version
