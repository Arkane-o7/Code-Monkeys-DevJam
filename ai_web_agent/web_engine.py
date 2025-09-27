"""
Web automation engine using Playwright for executing web actions.
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from .models import WebAction, ActionResult, ActionType


logger = logging.getLogger(__name__)


class WebAutomationEngine:
    """Handles web automation using Playwright."""
    
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        """
        Initialize web automation engine.
        
        Args:
            headless: Whether to run browser in headless mode
            slow_mo: Milliseconds to slow down operations (helpful for debugging)
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def start(self) -> None:
        """Start the browser and create a new page."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            self.page = await self.context.new_page()
            logger.info("Web automation engine started")
        except Exception as e:
            logger.error(f"Failed to start web automation engine: {e}")
            await self.cleanup()
            raise
    
    async def cleanup(self) -> None:
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Web automation engine cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def execute_action(self, action: WebAction) -> ActionResult:
        """
        Execute a web action.
        
        Args:
            action: WebAction to execute
            
        Returns:
            ActionResult with execution outcome
        """
        if not self.page:
            return ActionResult(
                success=False,
                reason="Browser not initialized. Call start() first."
            )
        
        try:
            action_type = ActionType(action.action)
            
            if action_type == ActionType.GOTO:
                return await self._goto(action.parameters)
            elif action_type == ActionType.CLICK:
                return await self._click(action.parameters)
            elif action_type == ActionType.TYPE:
                return await self._type(action.parameters)
            elif action_type == ActionType.SELECT:
                return await self._select(action.parameters)
            elif action_type == ActionType.SCROLL:
                return await self._scroll(action.parameters)
            elif action_type == ActionType.HOVER:
                return await self._hover(action.parameters)
            elif action_type == ActionType.WAIT_FOR_ELEMENT:
                return await self._wait_for_element(action.parameters)
            elif action_type == ActionType.HANDLE_POPUP:
                return await self._handle_popup(action.parameters)
            elif action_type == ActionType.SCREENSHOT:
                return await self._screenshot(action.parameters)
            else:
                return ActionResult(
                    success=False,
                    reason=f"Unknown action type: {action.action}"
                )
                
        except Exception as e:
            logger.error(f"Error executing action {action.action}: {e}")
            return ActionResult(
                success=False,
                reason=f"Action execution failed: {str(e)}"
            )
    
    async def get_page_content(self) -> str:
        """Get current page HTML content."""
        if not self.page:
            return ""
        try:
            return await self.page.content()
        except Exception as e:
            logger.error(f"Failed to get page content: {e}")
            return ""
    
    async def get_page_title(self) -> str:
        """Get current page title."""
        if not self.page:
            return ""
        try:
            return await self.page.title()
        except Exception as e:
            logger.error(f"Failed to get page title: {e}")
            return ""
    
    async def get_current_url(self) -> str:
        """Get current page URL."""
        if not self.page:
            return ""
        try:
            return self.page.url
        except Exception as e:
            logger.error(f"Failed to get current URL: {e}")
            return ""
    
    async def _goto(self, params: Dict[str, Any]) -> ActionResult:
        """Navigate to a URL."""
        url = params.get("url")
        if not url:
            return ActionResult(success=False, reason="Missing 'url' parameter")
        
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            new_url = self.page.url
            
            return ActionResult(
                success=True,
                reason=f"Successfully navigated to {url}",
                new_url=new_url
            )
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Navigation failed: {str(e)}"
            )
    
    async def _click(self, params: Dict[str, Any]) -> ActionResult:
        """Click on an element."""
        element_id = params.get("element_id")
        selector = params.get("selector")
        
        if not element_id and not selector:
            return ActionResult(success=False, reason="Missing element identifier")
        
        try:
            # Try to find element by various methods
            target_selector = selector or f"[data-agent-id='{element_id}']"
            
            # Fallback selectors if primary fails
            fallback_selectors = [
                f"#{element_id}",
                f".{element_id}",
                f"[id*='{element_id}']",
                f"[class*='{element_id}']",
                f"[name='{element_id}']"
            ]
            
            element = None
            used_selector = target_selector
            
            try:
                element = await self.page.wait_for_selector(target_selector, timeout=5000)
            except:
                # Try fallback selectors
                for fallback in fallback_selectors:
                    try:
                        element = await self.page.wait_for_selector(fallback, timeout=2000)
                        used_selector = fallback
                        break
                    except:
                        continue
            
            if not element:
                return ActionResult(
                    success=False,
                    reason=f"Element not found with any selector"
                )
            
            # Click the element
            await element.click()
            
            return ActionResult(
                success=True,
                reason=f"Successfully clicked element using selector: {used_selector}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Click failed: {str(e)}"
            )
    
    async def _type(self, params: Dict[str, Any]) -> ActionResult:
        """Type text into an element."""
        element_id = params.get("element_id")
        selector = params.get("selector")
        text = params.get("text", "")
        
        if not element_id and not selector:
            return ActionResult(success=False, reason="Missing element identifier")
        
        try:
            target_selector = selector or f"[data-agent-id='{element_id}']"
            
            # Fallback selectors for input elements
            fallback_selectors = [
                f"input#{element_id}",
                f"textarea#{element_id}",
                f"input[name='{element_id}']",
                f"textarea[name='{element_id}']",
                f"input[id*='{element_id}']",
                f"textarea[id*='{element_id}']"
            ]
            
            element = None
            used_selector = target_selector
            
            try:
                element = await self.page.wait_for_selector(target_selector, timeout=5000)
            except:
                for fallback in fallback_selectors:
                    try:
                        element = await self.page.wait_for_selector(fallback, timeout=2000)
                        used_selector = fallback
                        break
                    except:
                        continue
            
            if not element:
                return ActionResult(
                    success=False,
                    reason=f"Input element not found"
                )
            
            # Clear and type text
            await element.clear()
            await element.type(text)
            
            return ActionResult(
                success=True,
                reason=f"Successfully typed '{text}' into element using selector: {used_selector}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Type failed: {str(e)}"
            )
    
    async def _select(self, params: Dict[str, Any]) -> ActionResult:
        """Select an option from a dropdown."""
        element_id = params.get("element_id")
        selector = params.get("selector")
        value = params.get("value")
        text = params.get("text")
        
        if not element_id and not selector:
            return ActionResult(success=False, reason="Missing element identifier")
        
        try:
            target_selector = selector or f"select[data-agent-id='{element_id}']"
            
            fallback_selectors = [
                f"select#{element_id}",
                f"select[name='{element_id}']",
                f"select[id*='{element_id}']"
            ]
            
            element = None
            used_selector = target_selector
            
            try:
                element = await self.page.wait_for_selector(target_selector, timeout=5000)
            except:
                for fallback in fallback_selectors:
                    try:
                        element = await self.page.wait_for_selector(fallback, timeout=2000)
                        used_selector = fallback
                        break
                    except:
                        continue
            
            if not element:
                return ActionResult(
                    success=False,
                    reason=f"Select element not found"
                )
            
            # Select by value or text
            if value:
                await element.select_option(value=value)
            elif text:
                await element.select_option(label=text)
            else:
                return ActionResult(
                    success=False,
                    reason="Missing 'value' or 'text' parameter for select"
                )
            
            return ActionResult(
                success=True,
                reason=f"Successfully selected option using selector: {used_selector}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Select failed: {str(e)}"
            )
    
    async def _scroll(self, params: Dict[str, Any]) -> ActionResult:
        """Scroll the page."""
        direction = params.get("direction", "down")
        amount = params.get("amount", 300)
        
        try:
            if direction == "down":
                await self.page.keyboard.press("PageDown")
            elif direction == "up":
                await self.page.keyboard.press("PageUp")
            elif direction == "bottom":
                await self.page.keyboard.press("End")
            elif direction == "top":
                await self.page.keyboard.press("Home")
            else:
                # Scroll by specific amount
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
            
            return ActionResult(
                success=True,
                reason=f"Successfully scrolled {direction}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Scroll failed: {str(e)}"
            )
    
    async def _hover(self, params: Dict[str, Any]) -> ActionResult:
        """Hover over an element."""
        element_id = params.get("element_id")
        selector = params.get("selector")
        
        if not element_id and not selector:
            return ActionResult(success=False, reason="Missing element identifier")
        
        try:
            target_selector = selector or f"[data-agent-id='{element_id}']"
            
            element = await self.page.wait_for_selector(target_selector, timeout=5000)
            if not element:
                return ActionResult(
                    success=False,
                    reason=f"Element not found: {target_selector}"
                )
            
            await element.hover()
            
            return ActionResult(
                success=True,
                reason=f"Successfully hovered over element: {target_selector}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Hover failed: {str(e)}"
            )
    
    async def _wait_for_element(self, params: Dict[str, Any]) -> ActionResult:
        """Wait for an element to appear."""
        element_id = params.get("element_id")
        selector = params.get("selector")
        timeout = params.get("timeout", 10000)
        
        if not element_id and not selector:
            return ActionResult(success=False, reason="Missing element identifier")
        
        try:
            target_selector = selector or f"[data-agent-id='{element_id}']"
            
            await self.page.wait_for_selector(target_selector, timeout=timeout)
            
            return ActionResult(
                success=True,
                reason=f"Element appeared: {target_selector}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Element did not appear within timeout: {str(e)}"
            )
    
    async def _handle_popup(self, params: Dict[str, Any]) -> ActionResult:
        """Handle popup dialogs."""
        action_type = params.get("action", "accept")  # accept, dismiss
        
        try:
            # Set up dialog handler
            def handle_dialog(dialog):
                if action_type == "accept":
                    return dialog.accept()
                else:
                    return dialog.dismiss()
            
            self.page.on("dialog", handle_dialog)
            
            return ActionResult(
                success=True,
                reason=f"Dialog handler set to {action_type}"
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Failed to set dialog handler: {str(e)}"
            )
    
    async def _screenshot(self, params: Dict[str, Any]) -> ActionResult:
        """Take a screenshot of the current page."""
        try:
            # Create screenshots directory if it doesn't exist
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            # Generate filename
            import time
            filename = f"screenshot_{int(time.time())}.png"
            filepath = screenshots_dir / filename
            
            # Take screenshot
            await self.page.screenshot(path=str(filepath), full_page=True)
            
            return ActionResult(
                success=True,
                reason=f"Screenshot saved to {filepath}",
                screenshot_path=str(filepath)
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                reason=f"Screenshot failed: {str(e)}"
            )