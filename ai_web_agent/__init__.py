"""
Enhanced Autonomous AI Web Agent

An intelligent web automation agent that can understand user goals,
decompose tasks, and execute them through web interactions using
the Observe-Decide-Act-Verify loop.
"""

__version__ = "1.0.0"

from .agent import WebAgent
from .models import TaskContext, WebAction, ActionResult

__all__ = ["WebAgent", "TaskContext", "WebAction", "ActionResult"]