import os
import tomllib
from argparse import ArgumentParser, Namespace
from functools import partial
from os import getenv

import gradio as gr
from cohere import ClientV2

from app_api import next_message, reset_conversation, CHARACTERS


def load_parameters() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--language",
        type=str,
        required=False,
        default="en",
        help="The language of the application.",
    )
    parser.add_argument(
        "--api_key",
        type=str,
        required=False,
        help="The API key for the Cohere API. If unprovided, it will be obtained via the COHERE_API_KEY environment variable.",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Whether to share the application.",
    )
    return parser.parse_args()


def build_ui(
        config: dict,
        client: ClientV2,
):
    """
    Builds the UI.
    """
    with gr.Blocks() as demo:
        gr.Markdown(f"# Escribito\n\n{config.get('description', '')}")

        with gr.Row():
            # Left panel: conversation & inputs
            with gr.Column(scale=3):
                # Markdown component to display the conversation.
                conversation = gr.Markdown(label="Story", value="", container=True)

                # Inputs
                with gr.Row():
                    role_selector = gr.Dropdown(
                        value=CHARACTERS[0],
                        choices=CHARACTERS,
                        multiselect=False,
                        label="Character",
                        scale=1,
                    )
                    text_input = gr.Textbox(
                        label="Message",
                        placeholder="Type your message here",
                        lines=1,
                        scale=3,
                    )
                    with gr.Column():
                        send_btn = gr.Button(value=config.get("send_btn_label"), variant="primary")
                        reset_btn = gr.Button(value=config.get("reset_btn_label"), variant="secondary")

            # Right panel: Character Definition
            with gr.Column(scale=1, variant="panel"):
                with gr.Tab(label="Character A"):
                    name_a = gr.Text(label="name", value="A")
                    story_a = gr.Text(label="story", value="A middle aged man happy with his life.")
                with gr.Tab(label="Character B"):
                    name_b = gr.Text(label="name", value="B")
                    story_b = gr.Text(label="story", value="A middle aged woman happy with her life.")

        # State variable to hold the conversation list.
        conversation_state = gr.State([])

        # When the button is clicked, call next_message and update both the conversation display and state.
        send_btn.click(
            fn=partial(next_message, client=client),
            inputs=[conversation_state, role_selector, text_input, name_a, story_a, name_b, story_b],
            outputs=[conversation, conversation_state, role_selector, text_input],
        )
        text_input.submit(
            fn=partial(next_message, client=client),
            inputs=[conversation_state, role_selector, text_input, name_a, story_a, name_b, story_b],
            outputs=[conversation, conversation_state, role_selector, text_input],
        )
        reset_btn.click(
            fn=reset_conversation,
            outputs=[conversation, conversation_state]
        )
    return demo


if __name__ == "__main__":
    params = load_parameters()

    # load the API client
    client = ClientV2(api_key=getenv("COHERE_API_KEY"))

    # load app language
    with open(os.path.join("config", "languages", f"{params.language}.toml"), "rb") as fp:
        config = tomllib.load(fp)

    # run the app
    (
        build_ui(
            config=config,
            client=client,
        )
        .launch(
            share=params.share,
        )
    )
