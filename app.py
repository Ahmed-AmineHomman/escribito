import os
import tomllib
from argparse import ArgumentParser, Namespace
from functools import partial
from os import getenv

import gradio as gr
from PIL.ImageOps import scale
from cohere import ClientV2

from app_api import next_message, download_conversation, CHARACTERS, MODELS


def load_parameters() -> Namespace:
    parser = ArgumentParser(description="Escribito - A character-based dialogue generation application")
    parser.add_argument(
        "--language",
        type=str,
        default="en",
        help="Interface language code (e.g., 'en' for English). Defaults to 'en'."
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Cohere API key. If not provided, reads from COHERE_API_KEY environment variable.",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Enable public URL sharing for remote access.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Local port number for the web interface. Defaults to 7860.",
    )
    parser.add_argument(
        "--server-name",
        type=str,
        default="localhost",
        help="Server hostname to bind to. Defaults to 'localhost'.",
    )
    parser.add_argument(
        "--temp-dir",
        type=str,
        default="temp",
        help="Directory path for storing conversation exports. Defaults to 'temp'.",
    )
    return parser.parse_args()


def build_ui(
        config: dict,
        client: ClientV2,
        temp_dir: str,
):
    """
    Builds the UI.
    """
    with gr.Blocks() as demo:
        gr.Markdown(f"# Escribito", elem_classes=["header"])
        with gr.Row(equal_height=True):
            with gr.Column(scale=1):
                gr.Image(
                    value="config/escribito.svg",
                    height=200,
                    width=200,
                    interactive=False,
                    show_label=False,
                    show_download_button=False,
                    show_share_button=False,
                    show_fullscreen_button=False,
                    container=False,
                    scale=1,
                )
            with gr.Column(scale=3):
                gr.Markdown(config.get('description', ''))

        with gr.Row(equal_height=True):
            # Left panel: conversation & inputs
            with gr.Column(scale=5):
                # The dialogue displayed as a chatbot
                conversation = gr.Chatbot(
                    label="Story",
                    type="messages",
                    container=True,
                    editable="all",
                    avatar_images=("config/avatars/character_a.png", "config/avatars/character_b.png"),
                    height=600,
                    show_copy_button=True,
                    show_copy_all_button=True,
                )

                # Inputs
                with gr.Row(equal_height=True):
                    role_selector = gr.Dropdown(
                        value=CHARACTERS.get("user"),
                        choices=list(CHARACTERS.values()),
                        multiselect=False,
                        label=config.get("user_panel").get("role_selector_label"),
                        scale=1,
                        container=True
                    )
                    text_input = gr.Textbox(
                        label=config.get("user_panel").get("message_label"),
                        placeholder="Type your message here",
                        container=True,
                        scale=3,
                    )
                    with gr.Column():
                        send_btn = gr.Button(
                            value=config.get("user_panel").get("send_btn_label"),
                            variant="primary"
                        )
                        download_btn = gr.DownloadButton(
                            label=config.get("user_panel").get("download_btn_label"),
                            variant="secondary"
                        )

            # Right Panel: controls
            with gr.Column(scale=3):
                # Character Definition Panel
                gr.Markdown(
                    f"## {config.get('character_panel').get('title')}\n\n{config.get('character_panel').get('description')}")
                with gr.Column(scale=1, variant="panel"):
                    with gr.Tab(label="Character A"):
                        name_a = gr.Text(
                            label=config.get("character_panel").get("character_a_name_label"),
                            value=config.get("character_panel").get("character_a_name")
                        )
                        story_a = gr.Textbox(
                            label=config.get("character_panel").get("character_a_story_label"),
                            value=config.get("character_panel").get("character_a_story"),
                            lines=3,
                        )
                    with gr.Tab(label="Character B"):
                        name_b = gr.Text(
                            label=config.get("character_panel").get("character_b_name_label"),
                            value=config.get("character_panel").get("character_b_name")
                        )
                        story_b = gr.Text(
                            label=config.get("character_panel").get("character_b_story_label"),
                            value=config.get("character_panel").get("character_b_story"),
                            lines=3,
                        )

                # LLM Control Panel
                gr.Markdown(
                    f"## {config.get('llm_panel').get('title')}\n\n{config.get('llm_panel').get('description')}")
                with gr.Column(scale=1, variant="panel"):
                    model = gr.Dropdown(
                        label=config.get("llm_panel").get("model_btn_label"),
                        info=config.get("llm_panel").get("model_btn_info"),
                        value=list(MODELS.keys())[0],
                        choices=MODELS.keys(),
                        multiselect=False,
                    )
                    temperature = gr.Slider(
                        label=config.get("llm_panel").get("temperature_btn_label"),
                        info=config.get("llm_panel").get("temperature_btn_info"),
                        value=0.8,
                        minimum=0.0,
                        maximum=2.0,
                        step=0.05,
                    )

        # States
        temp_dir = gr.State(value=temp_dir)

        # When the button is clicked, call next_message and update both the conversation display and state.
        send_btn.click(
            fn=partial(next_message, client=client),
            inputs=[conversation, role_selector, text_input, name_a, story_a, name_b, story_b, model, temperature],
            outputs=[conversation, role_selector, text_input],
        )
        text_input.submit(
            fn=partial(next_message, client=client),
            inputs=[conversation, role_selector, text_input, name_a, story_a, name_b, story_b, model, temperature],
            outputs=[conversation, role_selector, text_input],
        )
        download_btn.click(
            fn=download_conversation,
            inputs=[conversation, temp_dir, name_a, name_b],
            outputs=[download_btn]
        )
    return demo


if __name__ == "__main__":
    params = load_parameters()

    # load the API client (use provided key if parameter is set, otherwise use the environment variable)
    api_key = params.api_key if params.api_key else getenv("COHERE_API_KEY")
    client = ClientV2(api_key=api_key)

    # load app language
    with open(os.path.join("config", "languages", f"{params.language}.toml"), "rb") as fp:
        config = tomllib.load(fp)

    # set up for temp directory
    os.makedirs(params.temp_dir, exist_ok=True)

    # run the app
    (
        build_ui(
            config=config,
            client=client,
            temp_dir=params.temp_dir,
        )
        .launch(
            share=params.share,
            server_name=params.server_name,
            server_port=params.port,
        )
    )
