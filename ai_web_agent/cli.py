"""
Command-line interface for the Enhanced Autonomous AI Web Agent.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from colorama import Fore, Style, init

from .agent import WebAgent


# Initialize colorama
init()


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('web_agent.log')
        ]
    )


def print_banner():
    """Print the application banner."""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🤖 Enhanced Autonomous AI Web Agent 🤖             ║
║                                                              ║
║  Intelligently automates web tasks using AI decision making ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)


def print_examples():
    """Print usage examples."""
    examples = f"""
{Fore.GREEN}Example Usage:{Style.RESET_ALL}

  {Fore.YELLOW}Interactive mode:{Style.RESET_ALL}
    ai-web-agent --interactive
    
  {Fore.YELLOW}Execute a specific goal:{Style.RESET_ALL}
    ai-web-agent --goal "Search for Python tutorials on Google"
    
  {Fore.YELLOW}With visible browser (non-headless):{Style.RESET_ALL}
    ai-web-agent --goal "Book a flight" --no-headless
    
  {Fore.YELLOW}With verbose logging:{Style.RESET_ALL}
    ai-web-agent --goal "Check weather forecast" --verbose
    
  {Fore.YELLOW}Slow down for debugging:{Style.RESET_ALL}
    ai-web-agent --goal "Fill out a form" --slow-mo 500

{Fore.GREEN}Setup:{Style.RESET_ALL}
  1. Install dependencies: pip install -r requirements.txt
  2. Set up Gemini API key: export GEMINI_API_KEY="your_api_key"
  3. Install browser: playwright install chromium

{Fore.GREEN}Goals Examples:{Style.RESET_ALL}
  • "Search for machine learning courses on Coursera"
  • "Find the latest news about AI on BBC"
  • "Look up the weather forecast for New York"
  • "Find Python job listings on Indeed"
  • "Search for healthy recipes on a cooking website"
"""
    print(examples)


async def interactive_mode():
    """Run the agent in interactive mode."""
    print(f"{Fore.CYAN}🚀 Starting Interactive Mode{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Enter your goals one at a time. Type 'quit' to exit.{Style.RESET_ALL}\n")
    
    agent = WebAgent(headless=False, slow_mo=100)
    
    try:
        await agent.start()
        
        while True:
            try:
                goal = input(f"{Fore.GREEN}🎯 Enter your goal: {Style.RESET_ALL}")
                
                if goal.lower() in ['quit', 'exit', 'stop']:
                    break
                
                if not goal.strip():
                    print(f"{Fore.YELLOW}⚠️  Please enter a valid goal.{Style.RESET_ALL}")
                    continue
                
                print(f"\n{Fore.CYAN}🚀 Starting execution...{Style.RESET_ALL}")
                success = await agent.execute_goal(goal)
                
                if success:
                    print(f"{Fore.GREEN}✅ Goal accomplished!{Style.RESET_ALL}\n")
                else:
                    print(f"{Fore.RED}❌ Goal was not completed.{Style.RESET_ALL}\n")
                
                # Ask if user wants to continue
                continue_choice = input(f"{Fore.BLUE}Continue with another goal? (y/n): {Style.RESET_ALL}")
                if continue_choice.lower() not in ['y', 'yes']:
                    break
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}⚠️  Interrupted by user{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
                continue
    
    finally:
        await agent.stop()
        print(f"{Fore.CYAN}👋 Thanks for using AI Web Agent!{Style.RESET_ALL}")


async def execute_single_goal(goal: str, headless: bool = True, slow_mo: int = 100):
    """Execute a single goal and exit."""
    print(f"{Fore.CYAN}🎯 Goal: {goal}{Style.RESET_ALL}\n")
    
    agent = WebAgent(headless=headless, slow_mo=slow_mo)
    
    try:
        await agent.start()
        success = await agent.execute_goal(goal)
        
        if success:
            print(f"\n{Fore.GREEN}🎉 Mission accomplished!{Style.RESET_ALL}")
            return 0
        else:
            print(f"\n{Fore.RED}❌ Mission failed{Style.RESET_ALL}")
            return 1
    
    finally:
        await agent.stop()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enhanced Autonomous AI Web Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="For more information, visit: https://github.com/Arkane-o7/Code-Monkeys-DevJam"
    )
    
    # Main operation modes
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--goal", "-g",
        type=str,
        help="Execute a specific goal and exit"
    )
    group.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    group.add_argument(
        "--examples",
        action="store_true",
        help="Show usage examples and exit"
    )
    
    # Configuration options
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show browser window (disable headless mode)"
    )
    parser.add_argument(
        "--slow-mo",
        type=int,
        default=100,
        metavar="MS",
        help="Slow down operations by specified milliseconds (default: 100)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Gemini API key (overrides environment variable)"
    )
    
    args = parser.parse_args()
    
    # Show examples and exit
    if args.examples:
        print_banner()
        print_examples()
        return 0
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Print banner
    print_banner()
    
    try:
        if args.interactive:
            # Interactive mode
            asyncio.run(interactive_mode())
            return 0
        elif args.goal:
            # Single goal execution
            return asyncio.run(execute_single_goal(
                goal=args.goal,
                headless=not args.no_headless,
                slow_mo=args.slow_mo
            ))
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Interrupted by user{Style.RESET_ALL}")
        return 1
    except Exception as e:
        print(f"{Fore.RED}❌ Fatal error: {e}{Style.RESET_ALL}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())