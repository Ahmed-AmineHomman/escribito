# Escribito

![](config/escribito.svg)

**Open Source under the MIT License**

Welcome to **Escribito**, a straightforward app that enables two Large Language Models (LLMs) to converse with one another in real time. This playful yet powerful tool is perfect for writers, creatives, and anyone eager to explore AI-generated dialogues, brainstorm story ideas, or simply spark inspiration.

## Why Escribito?

- **Creative Storytelling**: Craft engaging scenes by letting two AI “characters” exchange dialogue.
- **Idea Generation**: Spur new narratives, gather fresh perspectives, or break writer’s block.
- **Simplicity**: With a minimalistic approach powered by [Gradio](https://gradio.app/), Escribito aims to be both accessible and straightforward.

## Features

- **Dialogue Between LLMs**: Put two AI models face to face to co-create or debate.
- **Cohere Integration**: Seamlessly connect with Cohere’s LLM via API key.
- **User-Friendly Interface**: Launch a local web UI, no complicated setups.
- **Extendable**: Plans to support more APIs and local LLMs in the future.

## Prerequisites

- Basic familiarity with [Python](https://www.python.org/about/gettingstarted/). (If you need a refresh, follow the link.)
- A valid [Cohere API key](https://dashboard.cohere.com/). (Free trials are available.)

## Installation

1.  **Clone or Download** the repository:
    ```bash
    git clone https://github.com/Ahmed-AmineHomman/escribito
    ```
2.  **Install Dependencies**:
    ```bash
    pip install .
    ```

That’s it! You’re ready to explore the app.

## Usage

1. **Set Up Your API Key**:
   - Option A: Export it as an environment variable:
     ```bash
     export COHERE_API_KEY=your_api_key
     ```
   - Option B: Pass it when launching the app:
     ```bash
     python app.py --api-key your_api_key
     ```

2. **Launch Escribito**:
   ```bash
   python app.py
   ```
   Then open your browser at `http://localhost:7860/` and start creating AI dialogues.

3. **Explore Other Settings**:
   ```bash
   python app.py --help
   ```
   This will list optional parameters to customize your experience.

## How It Works

- **Under the Hood**: Escribito harnesses Cohere’s LLM to propose responses for each "character." You can name these characters, set the conversation context, and watch them build a dynamic dialogue.
- **Creative Use Cases**: Character interviews, story ideation, role-playing scenarios, and more.

## Roadmap

- **Additional Providers**: Integration with other AI models (including local solutions) is in the pipeline.
- **Enhanced UI**: Sleek design improvements and extra settings for controlling creativity.

## Contributing

We welcome contributions! If you’d like to add features, fix bugs, or improve documentation:

1. **Fork** the repository.
2. **Create a new branch** with a descriptive name.
3. **Implement your changes** and submit a pull request.

## License

Escribito is released under the [MIT License](https://en.wikipedia.org/wiki/MIT_License). Feel free to use, modify, and distribute this project as you wish. We kindly ask that you credit this repository when sharing your version.

---

Have fun experimenting with AI-generated dialogues, and feel free to share your creations! If you have any questions or issues, please open an [issue on GitHub](https://github.com/Ahmed-AmineHomman/escribito/issues) or reach out on LinkedIn. Happy writing!