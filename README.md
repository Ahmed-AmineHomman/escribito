# Escribito

This minimalistic app, built using [Gradio](https://gradio.app/), and allows you to put face to face two LLMs (Large
Language Models) to create dialogues for your stories.

## Getting Started

### Prerequisites

In order for a successfull installation, you need the following:

- A working installation of [python](https://www.python.org/downloads/),
- A Cohere API key.
  You can obtain one by signing up on the [Cohere website](https://cohere.ai/).
  Cohere offers free trial API keys with limited rates that you can use to test this app.

First clone this deposit on your system. You can do this by running the following command in your terminal:

```bash
git clone https://github.com/Ahmed-AmineHomman/escribito
```

You can also download the zip file from the GitHub page of this solution and extract it on your disk.

Then, open a terminal inside the root directory of this deposit and install the required libraries by running the
following command:

```bash
pip install .
```

### Usage

To start the app, run the following command:

```bash
python app.py
```

Then, open your browser and go to `http://localhost:7860/` to start using the app.

The app takes additional parameter whose details you can find by running the following command:

```bash
python app.py --help
```

The app is minimalistic and very simple. Please refer to the in-app documentation for more information.

### API Key

This app only supports LLMs from Cohere. You need to provide your API key in order to use the app. You can do this by
signing up on the [Cohere platform](https://dashboard.cohere.com/) and creating a free trial API key. Such keys come
with rates limitations but are enough to test this app.

In order for the app to recognize your API key, you need to set it in the environment variable `COHERE_API_KEY`. You can
do this by running the following command in your terminal:

```bash
export COHERE_API_KEY=your_api_key
```

You can also directly provide the API key to the app by setting the ``api-key`` parameter when running the app. For
example:

```bash
python app.py --api-key your_api_key
```

**Note**: The API key is sensitive information. Do not share it with anyone.

**Note (2)**: Additional APIs, and even local LLMs are planned to be supported in the future.
