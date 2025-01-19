import gradio as gr
import os


def respond(text, messages):
    print(text)
    print(messages)
    return ""


def build_ui():
    """
    Builds the chatbot UI.
    """
    # Instanciate the gradio chatbot interface
    chatbot = gr.ChatInterface(
        fn=respond,
        type="messages",
        examples=["hello", "hola", "merhaba"],
        title="Escribito"
    )
    return chatbot


if __name__ == "__main__":
    # Build the chatbot UI
    chatbot = build_ui()
    chatbot.launch()