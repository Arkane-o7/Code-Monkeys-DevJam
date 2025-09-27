"""
Simple test script to verify the agent can be imported and initialized.
"""

import os
import asyncio
from ai_web_agent import WebAgent


def test_import_and_basic_initialization():
    """Test that the agent can be imported and basic initialization works."""
    print("🧪 Testing AI Web Agent import and initialization...")
    
    # Set a dummy API key for testing
    os.environ["GEMINI_API_KEY"] = "test_key_dummy"
    
    try:
        # Test basic initialization
        agent = WebAgent(headless=True)
        print("✅ Agent initialization successful")
        
        # Test that we can access the components
        assert agent.analyzer is not None
        assert agent.web_engine is not None
        print("✅ Agent components initialized")
        
        # Test context initialization
        from ai_web_agent.models import TaskContext
        context = TaskContext(
            original_goal="Test goal",
            current_step="Test step"
        )
        print("✅ TaskContext creation successful")
        
        print("🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_gemini_analyzer_structure():
    """Test the GeminiAnalyzer structure without making API calls."""
    print("\n🧪 Testing GeminiAnalyzer structure...")
    
    try:
        from ai_web_agent.gemini_analyzer import GeminiAnalyzer
        
        # Create analyzer with dummy key
        analyzer = GeminiAnalyzer("dummy_key")
        
        # Test that methods exist
        assert hasattr(analyzer, 'create_execution_plan')
        assert hasattr(analyzer, 'analyze_html_structure')
        assert hasattr(analyzer, 'decide_next_action')
        assert hasattr(analyzer, 'verify_action_result')
        assert hasattr(analyzer, 'reorient_after_failure')
        
        print("✅ GeminiAnalyzer structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ GeminiAnalyzer test failed: {e}")
        return False


async def test_web_engine_structure():
    """Test the WebAutomationEngine structure without starting browser."""
    print("\n🧪 Testing WebAutomationEngine structure...")
    
    try:
        from ai_web_agent.web_engine import WebAutomationEngine
        
        # Create engine
        engine = WebAutomationEngine(headless=True)
        
        # Test that methods exist
        assert hasattr(engine, 'start')
        assert hasattr(engine, 'cleanup')
        assert hasattr(engine, 'execute_action')
        assert hasattr(engine, 'get_page_content')
        
        print("✅ WebAutomationEngine structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ WebAutomationEngine test failed: {e}")
        return False


def test_models():
    """Test the data models."""
    print("\n🧪 Testing data models...")
    
    try:
        from ai_web_agent.models import (
            WebAction, ActionResult, UIElement, 
            PageAnalysis, ExecutionPlan, PlanStep, ActionType
        )
        
        # Test WebAction
        action = WebAction(
            action=ActionType.CLICK,
            parameters={"element_id": "test"},
            expected_outcome="Test outcome"
        )
        assert action.action == "click"  # Should be serialized to string
        
        # Test UIElement
        element = UIElement(
            agent_id="test_btn",
            element_type="button",
            description="Test button"
        )
        assert element.agent_id == "test_btn"
        
        # Test ExecutionPlan
        steps = [PlanStep(step_number=1, description="Step 1", goal="Goal 1")]
        plan = ExecutionPlan(goal="Test goal", steps=steps)
        assert not plan.is_complete
        
        print("✅ Data models working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Running AI Web Agent Structure Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_import_and_basic_initialization())
    results.append(await test_gemini_analyzer_structure())
    results.append(await test_web_engine_structure())
    results.append(test_models())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All structure tests passed! The AI Web Agent is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Set GEMINI_API_KEY environment variable")
        print("   2. Ensure Playwright browsers are installed: playwright install chromium")
        print("   3. Try: ai-web-agent --goal 'Search for Python tutorials on Google'")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)