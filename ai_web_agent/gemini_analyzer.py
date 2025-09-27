"""
Gemini API integration for decision making and analysis.
"""

import json
import logging
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from .models import UIElement, WebAction, ActionResult, ExecutionPlan, PlanStep, PageAnalysis


logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Handles all interactions with Gemini API for web agent decision making."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-pro"):
        """
        Initialize Gemini analyzer.
        
        Args:
            api_key: Google AI API key
            model_name: Gemini model to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
    async def create_execution_plan(self, user_goal: str) -> ExecutionPlan:
        """
        Generate a high-level execution plan for the user's goal.
        
        Args:
            user_goal: The user's objective
            
        Returns:
            ExecutionPlan with ordered steps
        """
        prompt = f"""
        Create a high-level execution plan to achieve this goal: "{user_goal}"
        
        Break down the goal into logical, sequential steps that a web automation agent could execute.
        Each step should be specific and actionable.
        
        Return the response as a JSON object with this structure:
        {{
            "goal": "{user_goal}",
            "steps": [
                {{
                    "step_number": 1,
                    "description": "Brief description",
                    "goal": "Specific objective for this step"
                }},
                ...
            ]
        }}
        
        Make sure steps are in logical order and each step has a clear, measurable outcome.
        """
        
        try:
            response = await self._generate_content(prompt)
            plan_data = self._extract_json_from_response(response)
            
            steps = [PlanStep(**step) for step in plan_data.get("steps", [])]
            return ExecutionPlan(
                goal=plan_data.get("goal", user_goal),
                steps=steps
            )
        except Exception as e:
            logger.error(f"Failed to create execution plan: {e}")
            # Fallback to simple single-step plan
            return ExecutionPlan(
                goal=user_goal,
                steps=[PlanStep(
                    step_number=1,
                    description=f"Complete the goal: {user_goal}",
                    goal=user_goal
                )]
            )
    
    async def analyze_html_structure(self, html_content: str, current_url: str) -> PageAnalysis:
        """
        Analyze HTML content and extract interactive elements.
        
        Args:
            html_content: Raw HTML of the page
            current_url: Current page URL
            
        Returns:
            PageAnalysis with structured UI elements
        """
        prompt = f"""
        Analyze this HTML content and extract all interactive elements.
        URL: {current_url}
        
        HTML:
        {html_content[:10000]}  # Limit HTML size to avoid token limits
        
        Return a JSON object with this structure:
        {{
            "url": "{current_url}",
            "title": "page title",
            "interactive_elements": [
                {{
                    "agent_id": "unique_short_id",
                    "element_type": "button|input|a|select|etc",
                    "description": "what this element does",
                    "text_content": "visible text",
                    "attributes": {{"key": "value"}},
                    "selector": "css_selector"
                }}
            ]
        }}
        
        Focus on elements that users can interact with: buttons, links, form inputs, dropdowns, etc.
        Create descriptive agent_ids like "login_button", "search_input", "nav_menu", etc.
        Include important attributes like id, class, name, href, etc.
        """
        
        try:
            response = await self._generate_content(prompt)
            analysis_data = self._extract_json_from_response(response)
            
            elements = []
            for elem_data in analysis_data.get("interactive_elements", []):
                elements.append(UIElement(**elem_data))
            
            return PageAnalysis(
                url=analysis_data.get("url", current_url),
                title=analysis_data.get("title", "Unknown"),
                interactive_elements=elements
            )
        except Exception as e:
            logger.error(f"Failed to analyze HTML: {e}")
            return PageAnalysis(
                url=current_url,
                title="Analysis Failed",
                interactive_elements=[]
            )
    
    async def decide_next_action(
        self,
        current_goal: str,
        context_data: Dict[str, Any],
        ui_elements: List[UIElement]
    ) -> WebAction:
        """
        Decide the next best action to take.
        
        Args:
            current_goal: Current step goal
            context_data: Agent's memory/context
            ui_elements: Available interactive elements
            
        Returns:
            WebAction to execute
        """
        elements_json = [elem.model_dump() for elem in ui_elements]
        
        prompt = f"""
        My current goal is: "{current_goal}"
        
        My memory/context from previous steps:
        {json.dumps(context_data, indent=2)}
        
        Available UI elements on current page:
        {json.dumps(elements_json, indent=2)}
        
        What is the single best action to take next? 
        
        Valid actions are: goto, click, type, select, scroll, hover, wait_for_element, handle_popup
        
        Return response as JSON:
        {{
            "action": "action_type",
            "parameters": {{
                "element_id": "agent_id_if_needed",
                "text": "text_to_type_if_needed",
                "url": "url_if_goto",
                "selector": "css_selector_if_specific_targeting_needed"
            }},
            "expected_outcome": "Detailed description of what should happen after this action"
        }}
        
        Choose the most logical action that progresses toward the goal.
        Be specific about expected outcomes (what text should appear, which page to navigate to, etc.).
        """
        
        try:
            response = await self._generate_content(prompt)
            action_data = self._extract_json_from_response(response)
            
            return WebAction(
                action=action_data.get("action"),
                parameters=action_data.get("parameters", {}),
                expected_outcome=action_data.get("expected_outcome", "Action should succeed")
            )
        except Exception as e:
            logger.error(f"Failed to decide next action: {e}")
            # Fallback action
            return WebAction(
                action="screenshot",
                parameters={},
                expected_outcome="Take screenshot to analyze current state"
            )
    
    async def verify_action_result(
        self,
        expected_outcome: str,
        new_page_content: str,
        action_executed: WebAction
    ) -> ActionResult:
        """
        Verify if the executed action achieved the expected outcome.
        
        Args:
            expected_outcome: What was expected to happen
            new_page_content: Current page content after action
            action_executed: The action that was performed
            
        Returns:
            ActionResult with success status and reason
        """
        prompt = f"""
        I executed this action: {action_executed.action} with parameters {action_executed.parameters}
        
        Expected outcome: "{expected_outcome}"
        
        Current page content (first 5000 chars):
        {new_page_content[:5000]}
        
        Did the action succeed? Analyze the page content to determine if the expected outcome was achieved.
        
        Return JSON response:
        {{
            "success": true/false,
            "reason": "Detailed explanation of why it succeeded or failed"
        }}
        
        Be thorough in your analysis. Check for expected text, URL changes, new elements, etc.
        """
        
        try:
            response = await self._generate_content(prompt)
            result_data = self._extract_json_from_response(response)
            
            return ActionResult(
                success=result_data.get("success", False),
                reason=result_data.get("reason", "Verification failed")
            )
        except Exception as e:
            logger.error(f"Failed to verify action result: {e}")
            return ActionResult(
                success=False,
                reason=f"Verification error: {str(e)}"
            )
    
    async def reorient_after_failure(
        self,
        original_goal: str,
        failed_step: str,
        current_page_title: str,
        current_ui_elements: List[UIElement]
    ) -> WebAction:
        """
        Generate recovery action when agent is lost or confused.
        
        Args:
            original_goal: User's original objective
            failed_step: The step that failed
            current_page_title: Title of current page
            current_ui_elements: Available UI elements
            
        Returns:
            WebAction for recovery
        """
        elements_json = [elem.model_dump() for elem in current_ui_elements]
        
        prompt = f"""
        I'm lost and need to reorient myself.
        
        Original goal: "{original_goal}"
        Failed step: "{failed_step}"
        Current page title: "{current_page_title}"
        
        Available UI elements:
        {json.dumps(elements_json, indent=2)}
        
        How can I get back on track to achieve the original goal?
        What action should I take from this current state?
        
        Return JSON response:
        {{
            "action": "action_type",
            "parameters": {{...}},
            "expected_outcome": "How this helps get back on track"
        }}
        
        Think step by step about how to recover and continue toward the goal.
        """
        
        try:
            response = await self._generate_content(prompt)
            action_data = self._extract_json_from_response(response)
            
            return WebAction(
                action=action_data.get("action"),
                parameters=action_data.get("parameters", {}),
                expected_outcome=action_data.get("expected_outcome", "Recovery action")
            )
        except Exception as e:
            logger.error(f"Failed to generate recovery action: {e}")
            return WebAction(
                action="goto",
                parameters={"url": "https://www.google.com"},
                expected_outcome="Navigate to Google to start fresh"
            )
    
    async def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini API."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON object from Gemini response."""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            logger.debug(f"Response text: {response_text}")
            raise ValueError(f"Invalid JSON response: {e}")