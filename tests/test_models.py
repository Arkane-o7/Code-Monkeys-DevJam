"""
Tests for AI Web Agent models and utilities.
"""

import pytest
from ai_web_agent.models import (
    TaskContext, WebAction, ActionResult, UIElement, 
    PageAnalysis, PlanStep, ExecutionPlan, ActionType
)


def test_task_context_initialization():
    """Test TaskContext model initialization."""
    context = TaskContext(
        original_goal="Test goal",
        current_step="Test step"
    )
    
    assert context.original_goal == "Test goal"
    assert context.current_step == "Test step"
    assert context.completed_steps == []
    assert context.failed_steps == []
    assert context.memory == {}
    assert context.retry_count == 0
    assert context.max_retries == 3


def test_web_action_creation():
    """Test WebAction model creation."""
    action = WebAction(
        action=ActionType.CLICK,
        parameters={"element_id": "test_button"},
        expected_outcome="Button should be clicked"
    )
    
    assert action.action == ActionType.CLICK
    assert action.parameters["element_id"] == "test_button"
    assert "clicked" in action.expected_outcome


def test_action_result():
    """Test ActionResult model."""
    result = ActionResult(
        success=True,
        reason="Action completed successfully"
    )
    
    assert result.success is True
    assert "successfully" in result.reason
    assert result.new_url is None
    assert result.screenshot_path is None


def test_ui_element():
    """Test UIElement model."""
    element = UIElement(
        agent_id="login_button",
        element_type="button",
        description="Login button for user authentication",
        text_content="Login",
        attributes={"id": "btn-login", "class": "btn btn-primary"}
    )
    
    assert element.agent_id == "login_button"
    assert element.element_type == "button"
    assert element.text_content == "Login"
    assert element.attributes["id"] == "btn-login"


def test_page_analysis():
    """Test PageAnalysis model."""
    elements = [
        UIElement(
            agent_id="search_input",
            element_type="input",
            description="Search input field"
        ),
        UIElement(
            agent_id="search_button",
            element_type="button",
            description="Search button"
        )
    ]
    
    analysis = PageAnalysis(
        url="https://example.com",
        title="Test Page",
        interactive_elements=elements
    )
    
    assert analysis.url == "https://example.com"
    assert analysis.title == "Test Page"
    assert len(analysis.interactive_elements) == 2
    assert len(analysis.form_elements) == 1  # The input element
    assert len(analysis.navigation_elements) == 0


def test_execution_plan():
    """Test ExecutionPlan model and methods."""
    steps = [
        PlanStep(step_number=1, description="Step 1", goal="Goal 1"),
        PlanStep(step_number=2, description="Step 2", goal="Goal 2"),
    ]
    
    plan = ExecutionPlan(
        goal="Complete test",
        steps=steps
    )
    
    # Test current step
    assert plan.current_step.step_number == 1
    assert plan.current_step.description == "Step 1"
    assert not plan.is_complete
    
    # Mark step complete and test progression
    plan.mark_step_complete()
    assert plan.current_step.step_number == 2
    assert steps[0].completed is True
    
    # Complete all steps
    plan.mark_step_complete()
    assert plan.is_complete
    assert plan.current_step is None


def test_action_type_enum():
    """Test ActionType enum values."""
    assert ActionType.GOTO == "goto"
    assert ActionType.CLICK == "click"
    assert ActionType.TYPE == "type"
    assert ActionType.SCREENSHOT == "screenshot"
    
    # Test enum can be used in WebAction
    action = WebAction(
        action=ActionType.HOVER,
        parameters={},
        expected_outcome="Element should be hovered"
    )
    
    assert action.action == "hover"