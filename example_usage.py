"""
Example usage of the Enhanced Autonomous AI Web Agent.
"""

import asyncio
import os
from ai_web_agent import WebAgent


async def example_search_task():
    """Example: Search for information on Google."""
    print("🔍 Example: Searching for Python tutorials")
    
    # Initialize the agent
    agent = WebAgent(headless=False, slow_mo=200)  # Visible browser, slower for demo
    
    async with agent:  # This will start and stop the agent automatically
        goal = "Go to Google and search for 'Python web scraping tutorials'"
        success = await agent.execute_goal(goal)
        
        if success:
            print("✅ Search task completed successfully!")
        else:
            print("❌ Search task failed")


async def example_weather_check():
    """Example: Check weather information."""
    print("🌤️  Example: Checking weather forecast")
    
    agent = WebAgent(headless=False)
    
    try:
        await agent.start()
        
        goal = "Go to weather.com and check the weather forecast for New York"
        success = await agent.execute_goal(goal)
        
        if success:
            print("✅ Weather check completed!")
        else:
            print("❌ Weather check failed")
    
    finally:
        await agent.stop()


async def example_news_browsing():
    """Example: Browse news websites."""
    print("📰 Example: Finding latest tech news")
    
    agent = WebAgent(headless=False, slow_mo=150)
    
    async with agent:
        goal = "Visit BBC News and find articles about artificial intelligence"
        success = await agent.execute_goal(goal)
        
        print("✅ News browsing completed!" if success else "❌ News browsing failed")


async def run_all_examples():
    """Run all example tasks."""
    print("🚀 Running AI Web Agent Examples\n")
    
    examples = [
        ("Search Task", example_search_task),
        ("Weather Check", example_weather_check),
        ("News Browsing", example_news_browsing)
    ]
    
    for name, example_func in examples:
        print(f"\n{'='*50}")
        print(f"Running: {name}")
        print('='*50)
        
        try:
            await example_func()
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
        
        # Wait between examples
        print("\nWaiting 3 seconds before next example...")
        await asyncio.sleep(3)


def main():
    """Main function to run examples."""
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Please set the GEMINI_API_KEY environment variable")
        print("   Example: export GEMINI_API_KEY='your_api_key_here'")
        return
    
    print("🤖 AI Web Agent Examples")
    print("=" * 50)
    
    try:
        asyncio.run(run_all_examples())
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"❌ Examples failed: {e}")


if __name__ == "__main__":
    main()