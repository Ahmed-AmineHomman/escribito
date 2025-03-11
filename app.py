from os import getenv

import cohere
import gradio as gr

CLIENT: cohere.ClientV2


def build_conversation(
        conversation,
        name_a: str,
        name_b: str,
) -> str:
    """
    Builds the conversation for display using Markdown.
    """
    names = {"LLM A": name_a, "LLM B": name_b}
    return "\n\n".join([f"### {names.get(role)}\n{msg}" for role, msg in conversation])


def next_message(
        conversation,
        name_a: str,
        story_a: str,
        name_b: str,
        story_b: str,
):
    """
    Generate the next message in the conversation.

    Parameters
    ----------
    conversation : list of tuple
        List of tuples representing the conversation.
        Each tuple is of the form (role, message).
    name_a : str
        Name of character A.
    story_a : str
        Story of character A.
    name_b : str
        Name of character B.
    story_b : str
        Story of character B.

    Returns
    -------
    tuple
        A tuple containing:
        - md_text: A string with the formatted conversation (for Markdown display).
        - conversation: The updated conversation list.
    """
    _template = """
You will play the part of a given character, involved in a conversation with another character.
You will assume that this other character is the user, and you will respond as your character, which is described below.

- Name: {name},
- Backstory: {story}.

Take care in only replying as your character and to never break the fourth curtain.
"""

    # Determine the next speaker:
    # If conversation is empty or last speaker was LLM B, next is LLM A; else LLM B.
    if not conversation:
        next_role = "LLM A"
    else:
        last_role, _ = conversation[-1]
        next_role = "LLM B" if last_role == "LLM A" else "LLM A"

    # initialize conversation
    messages: list[dict[str, str]] = []

    # set system prompt
    if next_role == "LLM A":
        messages.append({"role": "system", "content": _template.format(name=name_a, story=story_a)})
    else:
        messages.append({"role": "system", "content": _template.format(name=name_b, story=story_b)})

    # set conversation history
    for data in conversation:
        character, message = data
        role = "user" if character == next_role else "assistant"
        messages.append({"role": role, "content": message})
    if len(conversation) == 0:
        messages.append({"role": "user", "content": " "})

    # generate the next message
    response = (
        CLIENT.chat(
            model="command-r",
            messages=messages
        )
        .message
        .content[0]
        .text
    )

    # Append the new message to the conversation.
    conversation.append((next_role, response))

    # Format the conversation for display using Markdown.
    md_text = build_conversation(
        conversation=conversation,
        name_a=name_a,
        name_b=name_b,
    )
    return md_text, conversation


def build_ui():
    """
    Builds the UI.
    """
    with gr.Blocks() as demo:
        gr.Markdown("# Escribito")

        with gr.Row():
            # Left panel: conversation & inputs
            with gr.Column(scale=3):
                # Markdown component to display the conversation.
                conversation = gr.Markdown(label="Story", value="", container=True)

                # Inputs
                gr.Markdown("""
Fill in the fields below to add the corresponding message to the conversation.
Send an empty message to let the character speak freely.
""")
                with gr.Row():
                    role_selector = gr.Dropdown(
                        value="Character A",
                        choices=["Character A", "Character B"],
                        multiselect=False,
                        label="Character",
                        scale=1,
                    )
                    text_input = gr.Text(
                        label="Message",
                        placeholder="Type your message here",
                        lines=1,
                        scale=3,
                    )
                    send_btn = gr.Button("Send")

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
            fn=next_message,
            inputs=[conversation_state, name_a, story_a, name_b, story_b],
            outputs=[conversation, conversation_state]
        )
    return demo


if __name__ == "__main__":
    CLIENT = cohere.ClientV2(api_key=getenv("COHERE_API_KEY"))
    build_ui().launch()
