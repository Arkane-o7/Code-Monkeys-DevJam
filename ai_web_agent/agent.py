"""
Main WebAgent class that implements the Enhanced Autonomous AI Web Agent.
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any
from colorama import Fore, Style, init
from dotenv import load_dotenv

from .models import TaskContext, ExecutionPlan, ActionResult
from .gemini_analyzer import GeminiAnalyzer
from .web_engine import WebAutomationEngine


# Initialize colorama for colored console output
init()

logger = logging.getLogger(__name__)


class WebAgent:
    """
    Enhanced Autonomous AI Web Agent that uses the Observe-Decide-Act-Verify loop
    to accomplish user goals through intelligent web interactions.
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        headless: bool = False,
        slow_mo: int = 100,
        max_retries: int = 3
    ):
        """
        Initialize the WebAgent.
        
        Args:
            gemini_api_key: Google AI API key (or will load from env)
            headless: Whether to run browser in headless mode
            slow_mo: Milliseconds to slow down operations
            max_retries: Maximum retries per step before escalating
        """
        # Load environment variables
        load_dotenv()
        
        # Set up API key
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Gemini API key required. Set GEMINI_API_KEY environment variable "
                "or pass gemini_api_key parameter."
            )
        
        # Initialize components
        self.analyzer = GeminiAnalyzer(api_key)
        self.web_engine = WebAutomationEngine(headless=headless, slow_mo=slow_mo)
        self.max_retries = max_retries
        
        # Agent state
        self.context = None
        self.execution_plan = None
        self.is_running = False
        
    async def start(self) -> None:
        """Start the web agent."""
        await self.web_engine.start()
        self.is_running = True
        self._print_status("🚀 Web Agent started and ready!", Fore.GREEN)
        
    async def stop(self) -> None:
        """Stop the web agent and cleanup resources."""
        await self.web_engine.cleanup()
        self.is_running = False
        self._print_status("🛑 Web Agent stopped", Fore.RED)
        
    async def execute_goal(self, user_goal: str) -> bool:
        """
        Execute a user goal using the Observe-Decide-Act-Verify loop.
        
        Args:
            user_goal: The user's objective to accomplish
            
        Returns:
            True if goal was accomplished, False otherwise
        """
        if not self.is_running:
            raise RuntimeError("Agent not started. Call start() first.")
        
        try:
            # Step A: Initial Triage and Planning
            success = await self._initial_triage_and_planning(user_goal)
            if not success:
                return False
            
            # Step B: Step-by-Step Execution Loop
            success = await self._execution_loop()
            if not success:
                return False
            
            # Step D: Task Completion
            await self._task_completion()
            return True
            
        except KeyboardInterrupt:
            self._print_status("🛑 Execution interrupted by user", Fore.YELLOW)
            return False
        except Exception as e:
            self._print_status(f"❌ Unexpected error: {e}", Fore.RED)
            logger.error(f"Unexpected error during goal execution: {e}", exc_info=True)
            return False
    
    async def _initial_triage_and_planning(self, user_goal: str) -> bool:
        """Step A: Initial Triage and Planning."""
        self._print_status("🧠 Analyzing goal and creating execution plan...", Fore.CYAN)
        
        # Check if this is a simple query that doesn't need web interaction
        if await self._is_simple_query(user_goal):
            await self._handle_simple_query(user_goal)
            return False  # No web interaction needed
        
        # Initialize context
        self.context = TaskContext(
            original_goal=user_goal,
            current_step="Initial planning",
            max_retries=self.max_retries
        )
        
        # Generate high-level plan
        try:
            self.execution_plan = await self.analyzer.create_execution_plan(user_goal)
            self._print_plan()
            return True
        except Exception as e:
            self._print_status(f"❌ Failed to create execution plan: {e}", Fore.RED)
            return False
    
    async def _execution_loop(self) -> bool:
        """Step B: Step-by-Step Execution Loop."""
        while not self.execution_plan.is_complete:
            current_step = self.execution_plan.current_step
            if not current_step:
                break
                
            self.context.current_step = current_step.goal
            self.context.retry_count = 0
            
            self._print_status(f"📋 Executing Step {current_step.step_number}: {current_step.description}", Fore.BLUE)
            
            # Execute step with retries
            success = await self._execute_step_with_retries()
            
            if success:
                self.execution_plan.mark_step_complete()
                self.context.completed_steps.append(current_step.description)
                self._print_status(f"✅ Step {current_step.step_number} completed!", Fore.GREEN)
            else:
                # Step failed after all retries
                self.context.failed_steps.append(current_step.description)
                self._print_status(f"❌ Step {current_step.step_number} failed after {self.max_retries} attempts", Fore.RED)
                
                # Ask user for guidance
                if not await self._escalate_to_user():
                    return False
        
        return True
    
    async def _execute_step_with_retries(self) -> bool:
        """Execute current step with retry logic."""
        while self.context.retry_count < self.max_retries:
            try:
                # OBSERVE: Analyze the DOM
                page_analysis = await self._observe()
                
                # DECIDE: Generate the Next Action
                action = await self._decide(page_analysis)
                
                # VALIDATE: Check for required user input
                if await self._validate_user_input_needed(action):
                    continue  # User provided input, retry the step
                
                # ACT: Execute the Command
                result = await self._act(action)
                
                # VERIFY: Confirm the Outcome
                if await self._verify(action, result):
                    # UPDATE CONTEXT: Success
                    await self._update_context_success(action, result)
                    return True
                else:
                    # Action failed verification
                    self.context.retry_count += 1
                    if self.context.retry_count < self.max_retries:
                        self._print_status(f"⚠️  Step verification failed, retrying ({self.context.retry_count}/{self.max_retries})...", Fore.YELLOW)
                        await asyncio.sleep(1)  # Brief pause before retry
                    
            except Exception as e:
                self.context.retry_count += 1
                logger.error(f"Error during step execution: {e}")
                self._print_status(f"❌ Step execution error: {e}", Fore.RED)
                
                if self.context.retry_count < self.max_retries:
                    await asyncio.sleep(2)  # Longer pause after error
        
        # All retries exhausted, try re-orientation
        return await self._reorient_after_failure()
    
    async def _observe(self):
        """OBSERVE: Analyze the current page DOM."""
        self._print_status("👁️  Observing current page...", Fore.CYAN)
        
        current_url = await self.web_engine.get_current_url()
        html_content = await self.web_engine.get_page_content()
        
        if not html_content:
            # If no page loaded yet, start with a default page
            if not current_url or current_url == "about:blank":
                await self.web_engine.execute_action({
                    "action": "goto",
                    "parameters": {"url": "https://www.google.com"},
                    "expected_outcome": "Navigate to Google homepage"
                })
                current_url = await self.web_engine.get_current_url()
                html_content = await self.web_engine.get_page_content()
        
        page_analysis = await self.analyzer.analyze_html_structure(html_content, current_url)
        
        self._print_status(f"🔍 Found {len(page_analysis.interactive_elements)} interactive elements on {page_analysis.title}", Fore.BLUE)
        
        return page_analysis
    
    async def _decide(self, page_analysis):
        """DECIDE: Generate the next action."""
        self._print_status("🤔 Deciding next action...", Fore.CYAN)
        
        action = await self.analyzer.decide_next_action(
            current_goal=self.context.current_step,
            context_data=self.context.memory,
            ui_elements=page_analysis.interactive_elements
        )
        
        self._print_status(f"💡 Decided: {action.action} - {action.expected_outcome[:50]}...", Fore.BLUE)
        
        return action
    
    async def _validate_user_input_needed(self, action) -> bool:
        """VALIDATE: Check if user input is needed."""
        # Check if action requires sensitive information
        sensitive_fields = ["password", "username", "email", "login", "signin", "auth"]
        action_str = str(action.parameters).lower()
        
        if any(field in action_str for field in sensitive_fields):
            if "text" in action.parameters:
                # Prompt user for sensitive information
                field_name = self._extract_field_name(action.parameters)
                user_input = input(f"\n🔐 Please enter {field_name}: ")
                action.parameters["text"] = user_input
                return True
        
        return False
    
    async def _act(self, action):
        """ACT: Execute the command."""
        self._print_status(f"⚡ Executing: {action.action}", Fore.CYAN)
        
        result = await self.web_engine.execute_action(action)
        
        if result.success:
            self._print_status(f"✅ Action executed: {result.reason}", Fore.GREEN)
        else:
            self._print_status(f"❌ Action failed: {result.reason}", Fore.RED)
        
        return result
    
    async def _verify(self, action, result) -> bool:
        """VERIFY: Confirm the outcome."""
        if not result.success:
            return False
        
        self._print_status("🔍 Verifying action outcome...", Fore.CYAN)
        
        # Get new page state
        new_content = await self.web_engine.get_page_content()
        
        # Verify with Gemini
        verification = await self.analyzer.verify_action_result(
            expected_outcome=action.expected_outcome,
            new_page_content=new_content,
            action_executed=action
        )
        
        if verification.success:
            self._print_status(f"✅ Verification passed: {verification.reason}", Fore.GREEN)
            return True
        else:
            self._print_status(f"❌ Verification failed: {verification.reason}", Fore.RED)
            return False
    
    async def _update_context_success(self, action, result):
        """UPDATE CONTEXT: Update memory after successful action."""
        # Store relevant information in context
        if result.new_url:
            self.context.memory["current_url"] = result.new_url
        
        if result.screenshot_path:
            self.context.memory["last_screenshot"] = result.screenshot_path
        
        # Store action history
        if "actions_taken" not in self.context.memory:
            self.context.memory["actions_taken"] = []
        
        self.context.memory["actions_taken"].append({
            "action": action.action,
            "parameters": action.parameters,
            "result": result.reason
        })
    
    async def _reorient_after_failure(self) -> bool:
        """Step C: Error Handling and Recovery Protocol."""
        self._print_status("🔄 Attempting to reorient after failure...", Fore.YELLOW)
        
        try:
            # Get current page state
            current_title = await self.web_engine.get_page_title()
            current_url = await self.web_engine.get_current_url()
            html_content = await self.web_engine.get_page_content()
            
            page_analysis = await self.analyzer.analyze_html_structure(html_content, current_url)
            
            # Generate recovery action
            recovery_action = await self.analyzer.reorient_after_failure(
                original_goal=self.context.original_goal,
                failed_step=self.context.current_step,
                current_page_title=current_title,
                current_ui_elements=page_analysis.interactive_elements
            )
            
            # Execute recovery action
            result = await self.web_engine.execute_action(recovery_action)
            
            if result.success:
                self._print_status("✅ Recovery action succeeded, continuing...", Fore.GREEN)
                return True
            else:
                self._print_status(f"❌ Recovery action failed: {result.reason}", Fore.RED)
                return False
                
        except Exception as e:
            logger.error(f"Reorientation failed: {e}")
            return False
    
    async def _escalate_to_user(self) -> bool:
        """Escalate to user when agent can't proceed."""
        self._print_status("🆘 Need user guidance to continue", Fore.YELLOW)
        
        print(f"\n{Fore.YELLOW}❓ The agent is having trouble with the current step.")
        print(f"Original goal: {self.context.original_goal}")
        print(f"Current step: {self.context.current_step}")
        print(f"Failed attempts: {self.context.retry_count}")
        
        user_input = input(f"\nWhat should the agent do next? (or 'quit' to stop): {Style.RESET_ALL}")
        
        if user_input.lower() in ['quit', 'stop', 'exit']:
            return False
        
        # Add user guidance to context
        self.context.memory["user_guidance"] = user_input
        self.context.retry_count = 0  # Reset retry count with user help
        
        return True
    
    async def _task_completion(self):
        """Step D: Task Completion."""
        self._print_status("🎉 Task completed successfully!", Fore.GREEN)
        
        print(f"\n{Fore.GREEN}✅ Goal accomplished: {self.context.original_goal}")
        print(f"📋 Completed steps:")
        for i, step in enumerate(self.context.completed_steps, 1):
            print(f"   {i}. {step}")
        
        if self.context.failed_steps:
            print(f"\n⚠️  Steps that had issues:")
            for step in self.context.failed_steps:
                print(f"   • {step}")
        
        print(f"{Style.RESET_ALL}")
    
    async def _is_simple_query(self, user_goal: str) -> bool:
        """Check if the user goal is a simple query that doesn't need web interaction."""
        query_indicators = [
            "what is", "who is", "when is", "where is", "why is", "how is",
            "define", "explain", "tell me about", "calculate", "convert"
        ]
        return any(indicator in user_goal.lower() for indicator in query_indicators)
    
    async def _handle_simple_query(self, user_goal: str):
        """Handle simple queries without web interaction."""
        self._print_status("💬 This appears to be a simple query. Answering directly...", Fore.BLUE)
        print(f"\n{Fore.BLUE}I notice this is a question that doesn't require web automation.")
        print(f"For questions like '{user_goal}', I'd recommend using a search engine")
        print(f"or asking an AI assistant directly.{Style.RESET_ALL}\n")
    
    def _extract_field_name(self, parameters: Dict[str, Any]) -> str:
        """Extract field name from parameters for user prompts."""
        element_id = parameters.get("element_id", "")
        if "password" in element_id.lower():
            return "password"
        elif "username" in element_id.lower() or "user" in element_id.lower():
            return "username"
        elif "email" in element_id.lower():
            return "email"
        else:
            return "value"
    
    def _print_status(self, message: str, color: str = Fore.WHITE):
        """Print colored status message."""
        print(f"{color}{message}{Style.RESET_ALL}")
    
    def _print_plan(self):
        """Print the execution plan."""
        print(f"\n{Fore.CYAN}📋 Execution Plan:")
        print(f"🎯 Goal: {self.execution_plan.goal}")
        print(f"📝 Steps:")
        for step in self.execution_plan.steps:
            print(f"   {step.step_number}. {step.description}")
        print(f"{Style.RESET_ALL}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()