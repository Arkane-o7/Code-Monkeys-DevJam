# Enhanced Autonomous AI Web Agent

**DevJam Project 2025 | Browser MCP Automation**

An intelligent web automation agent that can understand user goals, decompose tasks, and execute them through web interactions using the Observe-Decide-Act-Verify (OODA) loop with Gemini AI.

## 🚀 Features

- **Intelligent Task Decomposition**: Breaks down complex user goals into actionable steps
- **Advanced Web Perception**: Analyzes webpage HTML and identifies interactive elements
- **AI-Powered Decision Making**: Uses Google's Gemini AI to make intelligent automation choices
- **Contextual Memory**: Maintains persistent context throughout task execution
- **Robust Error Recovery**: Handles failures gracefully and attempts recovery
- **User Interaction**: Prompts for sensitive information when needed
- **Comprehensive Web Actions**: Supports goto, click, type, select, scroll, hover, wait, and more

## 🏗️ Architecture

The agent follows a structured workflow:

1. **Initial Triage and Planning**: Analyzes the user goal and creates an execution plan
2. **Step-by-Step Execution Loop**: For each step:
   - **OBSERVE**: Analyze the current page DOM
   - **DECIDE**: Use Gemini AI to determine the best action
   - **ACT**: Execute the web action using Playwright
   - **VERIFY**: Confirm the outcome matches expectations
3. **Error Handling and Recovery**: Re-orient when things go wrong
4. **Task Completion**: Provide summary of accomplished work

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Google AI API key (Gemini)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Arkane-o7/Code-Monkeys-DevJam.git
   cd Code-Monkeys-DevJam
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Gemini API key
   export GEMINI_API_KEY="your_api_key_here"
   ```

5. **Install the package**:
   ```bash
   pip install -e .
   ```

## 🎯 Usage

### Command Line Interface

**Interactive Mode** (recommended for first-time users):
```bash
ai-web-agent --interactive
```

**Execute a specific goal**:
```bash
ai-web-agent --goal "Search for Python tutorials on Google"
```

**With visible browser** (great for debugging):
```bash
ai-web-agent --goal "Check the weather forecast" --no-headless
```

**Show examples**:
```bash
ai-web-agent --examples
```

### Python API

```python
import asyncio
from ai_web_agent import WebAgent

async def main():
    agent = WebAgent(headless=False)  # Visible browser for demo
    
    async with agent:  # Automatically starts and stops
        success = await agent.execute_goal(
            "Go to Google and search for machine learning courses"
        )
        
        if success:
            print("Goal accomplished!")

if __name__ == "__main__":
    asyncio.run(main())
```

## 🎮 Example Goals

The agent can handle a wide variety of web automation tasks:

- **Information Gathering**:
  - "Search for the latest AI news on BBC"
  - "Find Python job listings on Indeed"
  - "Look up the weather forecast for San Francisco"

- **Research Tasks**:
  - "Find information about machine learning courses on Coursera"
  - "Search for healthy recipes on AllRecipes"
  - "Look up reviews for the latest iPhone"

- **Navigation Tasks**:
  - "Go to Wikipedia and read about quantum computing"
  - "Visit YouTube and search for guitar tutorials"
  - "Navigate to GitHub and find popular Python repositories"

## 🛠️ Configuration

The agent can be configured via environment variables or constructor parameters:

```python
agent = WebAgent(
    headless=False,           # Show browser window
    slow_mo=200,             # Slow down for visibility
    max_retries=3            # Retries per step
)
```

### Environment Variables

- `GEMINI_API_KEY`: Your Google AI API key (required)
- `GEMINI_MODEL`: Gemini model to use (default: gemini-1.5-pro)
- `HEADLESS`: Run browser in headless mode (default: false)
- `SLOW_MO`: Milliseconds to slow down operations

## 🔒 Security & Privacy

- **Sensitive Information**: The agent will prompt you for passwords and sensitive data rather than attempting to guess or use stored information
- **Local Execution**: All web automation happens locally on your machine
- **API Usage**: Only sends webpage structure and action decisions to Gemini AI, never sensitive personal data

## 🧪 Testing

Run the example script to test functionality:

```bash
python example_usage.py
```

Run tests (if available):

```bash
pytest tests/
```

## 🐛 Troubleshooting

### Common Issues

1. **"Browser not found"**: Run `playwright install chromium`
2. **"API key not found"**: Set the `GEMINI_API_KEY` environment variable
3. **"Element not found"**: The agent will attempt recovery automatically
4. **Slow performance**: Reduce `slow_mo` value or increase timeout values

### Debugging

- Use `--no-headless` to see what the browser is doing
- Use `--verbose` for detailed logging
- Check `web_agent.log` for full execution logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for intelligent decision making
- [Playwright](https://playwright.dev/) for robust web automation
- [Pydantic](https://pydantic.dev/) for data validation and modeling

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Look at the [examples](#-example-goals) for usage patterns
3. Open an issue on GitHub
4. Review the logs in `web_agent.log`

---

**Built with ❤️ by Code Monkeys for DevJam 2025**
