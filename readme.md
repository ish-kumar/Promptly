# Promptly

Promptly is a Chrome extension and backend service that helps you optimize, rewrite, and enhance your prompts for large language models (LLMs) directly in your browser. Designed for data scientists, developers, and prompt engineers, Promptly streamlines prompt engineering by providing instant, context-aware improvements—right where you work.

## Features
* **Seamless Prompt Detection:** Detects and extracts prompts from text fields on sites like ChatGPT, Notion, and Google.
* **One-Click Optimization:** Instantly rewrites prompts for clarity, creativity, cost-efficiency, or safety using state-of-the-art LLMs via OpenRouter.
* **Replace in Place:** Replaces your original prompt with the optimized version in the same input field—no copy-paste required.
* **Customizable Goals:** Choose your optimization goal (clarity, creativity, cost, safety) from the extension popup.
* **Modern, Extensible Architecture:** Modular backend (FastAPI) and frontend (Chrome extension) for easy customization and future features.

## Demo

![Promptly Screenshot](path/to/screenshot.png) *Promptly in action on ChatGPT.com*

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/promptly.git
cd promptly
```

### 2. Backend Setup
* Navigate to the backend directory:
```bash
cd backend
```

* Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```

* Install dependencies:
```bash
pip install -r requirements.txt
```

* Set up your `.env` file with your OpenRouter API key:
```
OPENROUTER_API_KEY=your_openrouter_key_here
```

* Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Extension Setup
* Go to `chrome://extensions/` in your browser.
* Enable **Developer mode**.
* Click **Load unpacked** and select the `extension` folder.
* The Promptly icon should appear in your Chrome toolbar.

## Usage
1. **Navigate to a supported site** (e.g., ChatGPT).
2. **Click into a prompt field** to activate Promptly.
3. **Open the Promptly extension** from your Chrome toolbar.
4. **Select your optimization goal** and click **Optimize**.
5. **Review the optimized prompt** in the popup.
6. **Click "Replace"** to insert the improved prompt back into the original field.

## Customization
* **Model Selection:** The backend uses Mistral 7B Instruct via OpenRouter by default. You can change the model in `backend/app/prompt_engine.py`.
* **Add More Goals:** Edit the `GOAL_INSTRUCTIONS` dictionary in `prompt_engine.py` to add or refine optimization strategies.
* **UI Enhancements:** The extension popup is modular and can be restyled using your preferred CSS framework.

## Roadmap
* UI/UX improvements (modern design, notifications)
* Model selection from the popup
* Prompt history and analytics
* Support for more sites and input types
* Team/collaboration features

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for bug fixes, new features, or documentation improvements.

## License

MIT License

## Acknowledgments
* [OpenRouter](https://openrouter.ai/) for LLM API access
* [Mistral AI](https://mistral.ai/) for the default model
* The open-source community for inspiration and support
