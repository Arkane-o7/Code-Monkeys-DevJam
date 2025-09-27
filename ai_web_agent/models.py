"""
Data models for the AI Web Agent.
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class ActionType(str, Enum):
    """Available web automation actions."""
    GOTO = "goto"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    SCROLL = "scroll"
    HOVER = "hover"
    WAIT_FOR_ELEMENT = "wait_for_element"
    HANDLE_POPUP = "handle_popup"
    SCREENSHOT = "screenshot"


class UIElement(BaseModel):
    """Represents an interactive UI element."""
    agent_id: str = Field(description="Unique identifier for the agent")
    element_type: str = Field(description="HTML tag name (e.g., 'button', 'input')")
    description: str = Field(description="Human-readable description of the element's purpose")
    text_content: Optional[str] = Field(default=None, description="Text content of the element")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="HTML attributes")
    selector: Optional[str] = Field(default=None, description="CSS selector for the element")


class WebAction(BaseModel):
    """Represents a web action to be executed."""
    action: ActionType = Field(description="Type of action to perform")
    parameters: Dict[str, Any] = Field(description="Action-specific parameters")
    expected_outcome: str = Field(description="Expected result after action execution")
    
    model_config = {"use_enum_values": True}


class ActionResult(BaseModel):
    """Result of executing a web action."""
    success: bool = Field(description="Whether the action succeeded")
    reason: str = Field(description="Explanation of success/failure")
    new_url: Optional[str] = Field(default=None, description="New URL if navigation occurred")
    screenshot_path: Optional[str] = Field(default=None, description="Path to screenshot if taken")


class TaskContext(BaseModel):
    """Maintains the agent's memory throughout task execution."""
    original_goal: str = Field(description="The user's original objective")
    current_step: str = Field(description="Current step being executed")
    completed_steps: List[str] = Field(default_factory=list, description="Successfully completed steps")
    failed_steps: List[str] = Field(default_factory=list, description="Steps that failed")
    memory: Dict[str, Any] = Field(default_factory=dict, description="Persistent data storage")
    retry_count: int = Field(default=0, description="Number of retries for current step")
    max_retries: int = Field(default=3, description="Maximum retries before escalating")


class PageAnalysis(BaseModel):
    """Analysis of current webpage state."""
    url: str = Field(description="Current page URL")
    title: str = Field(description="Page title")
    interactive_elements: List[UIElement] = Field(description="All interactive elements")
    form_elements: List[UIElement] = Field(default_factory=list, description="Form input elements")
    navigation_elements: List[UIElement] = Field(default_factory=list, description="Navigation links/buttons")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Auto-categorize elements after initialization
        self.form_elements = [e for e in self.interactive_elements if e.element_type in ["input", "textarea", "select"]]
        self.navigation_elements = [e for e in self.interactive_elements if e.element_type in ["a", "nav"] or "nav" in e.agent_id.lower()]


class PlanStep(BaseModel):
    """A single step in the high-level execution plan."""
    step_number: int = Field(description="Step sequence number")
    description: str = Field(description="Human-readable step description")
    goal: str = Field(description="Specific objective for this step")
    completed: bool = Field(default=False, description="Whether step is completed")


class ExecutionPlan(BaseModel):
    """High-level plan for achieving user's goal."""
    goal: str = Field(description="Overall goal")
    steps: List[PlanStep] = Field(description="Ordered list of steps")
    current_step_index: int = Field(default=0, description="Index of current step")
    
    @property
    def current_step(self) -> Optional[PlanStep]:
        """Get the current step being executed."""
        if self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def mark_step_complete(self) -> None:
        """Mark current step as completed and advance to next."""
        if self.current_step:
            self.current_step.completed = True
            self.current_step_index += 1
    
    @property
    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return self.current_step_index >= len(self.steps)