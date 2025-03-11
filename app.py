from os import getenv

import cohere
import gradio as gr

CLIENT: cohere.ClientV2


def build_conversation(conversation) -> str:
    """
    Builds the conversation for display using Markdown.
    """
    return "\n\n".join([f"**{role}:** {msg}" for role, msg in conversation])


def next_message(conversation):
    """
    Generate the next message in the conversation.

    Parameters
    ----------
    conversation : list of tuple
        List of tuples representing the conversation.
        Each tuple is of the form (role, message).

    Returns
    -------
    tuple
        A tuple containing:
        - md_text: A string with the formatted conversation (for Markdown display).
        - conversation: The updated conversation list.
    """
    # Determine the next speaker:
    # If conversation is empty or last speaker was LLM B, next is LLM A; else LLM B.
    if not conversation:
        next_role = "LLM A"
    else:
        last_role, _ = conversation[-1]
        next_role = "LLM B" if last_role == "LLM A" else "LLM A"

    # build conversation for the corresponding LLM
    messages: list[dict[str, str]] = []
    for data in conversation:
        role, message = data
        llm_role = "user" if role == next_role else "assistant"
        messages.append({"role": llm_role, "content": message})

    if len(messages) == 0:
        messages = [{"role": "user", "content": " "}]

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
    md_text = build_conversation(conversation)
    return md_text, conversation


with gr.Blocks() as demo:
    gr.Markdown("## LLMs Conversation Chat Interface")
    # Markdown component to display the conversation.
    conversation_display = gr.Markdown("")
    # State variable to hold the conversation list.
    conversation_state = gr.State([])

    # A single button that triggers the next message generation.
    next_btn = gr.Button("Next Message")

    # When the button is clicked, call next_message and update both the conversation display and state.
    next_btn.click(fn=next_message, inputs=conversation_state, outputs=[conversation_display, conversation_state])

CLIENT = cohere.ClientV2(api_key=getenv("COHERE_API_KEY"))
demo.launch()
