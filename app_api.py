import json
import os

from cohere import ClientV2

# Constants
MODELS = {
    "light": "command-r7b-12-2024",
    "medium": "command-r-08-2024",
    "heavy": "command-a-03-2025"
}


class ClientError(Exception):
    """Custom exception for API client errors."""
    pass


def generate(
        conversation: list[dict],
        model: str,
        client: ClientV2,
        system_prompt: str,
        temperature: float = 0.8,
) -> str:
    """
    Generate the next message in a conversation using the Cohere API.

    Uses the provided system prompt and conversation history to generate a contextually appropriate response.


    Parameters
    ----------
    conversation : list[dict]
        Chat history, where each dict contains:
        - 'role': str, either 'user' or 'assistant'
        - 'content': str, the message content
    model : str
        The identifier of the LLM model to use
    client : ClientV2
        Initialized Cohere API client instance
    system_prompt : str
        Instructions given to the LLM to guide the response generation
    temperature : float, optional
        Sampling temperature, controls response randomness.
        Higher values increase creativity, defaults to 0.8

    Returns
    -------
    str
        The generated response text

    Raises
    ------
    ClientError
        If API call fails or model is invalid
    """
    # consistency checks.
    if (not conversation) or (len(conversation) == 0):
        raise ClientError("Conversation history is empty.")

    # append system prompt to conversation
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
    if conversation:
        messages += conversation

    # call the API
    try:
        response = (
            client
            .chat(model=model, messages=messages, temperature=temperature)
            .message
            .content[0]
            .text
        )
        return response
    except Exception as e:
        raise ClientError(f"Failed to generate response: {e}") from e


def download_conversation(
        conversation: list[dict[str, str]],
        temp_dir: str,
        name_a: str,
        name_b: str,
) -> str:
    """
    Exports the conversation history to a JSON file and returns the file path.

    Parameters
    ----------
    conversation : list[dict[str, str]]
        List of conversation turns, where each dict contains:
        - 'role': str - either 'user' or 'assistant'
        - 'content': str - the message content
    temp_dir : str
        Directory path where the output file will be saved
    name_a : str
        Display name for the user character (Character A)
    name_b : str
        Display name for the assistant character (Character B)

    Returns
    -------
    str
        Path to the generated JSON file

    Raises
    ------
    IOError
        If writing to the output file fails
    """
    character_names = {"user": name_a, "assistant": name_b}
    output_path = os.path.join(temp_dir, "conversation.json")

    try:
        formatted_data = [
            {
                "character": character_names[turn["role"]],
                "message": turn["content"]
            }
            for turn in conversation
        ]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)

        return output_path

    except (IOError, KeyError, TypeError) as e:
        raise IOError(f"Failed to save conversation: {str(e)}") from e


def next_message(
        conversation: list[dict],
        user_character: str,
        user_message: str,
        name_a: str,
        story_a: str,
        name_b: str,
        story_b: str,
        model: str,
        temperature: float,
        client: ClientV2,
) -> tuple[list[dict], str, str]:
    """
    Generate or append the next message in a character conversation.

    The next message can either be associated with character A or B, depending on the last character to speak:
    - If character A spoke last, character B will respond.
    - If character B spoke last, character A will respond.
    Since a Chatbot element is used to display the conversation, each character must be assigned to one of the two roles supported by this element: user or assistant.
    Character A is always assigned to the user role, while character B is always assigned to the assistant role.

    Since most Generative APIs assume that the last message of the conversation should be the user message, roles are reverted whenever character A (user) should speak (i.e. character B spoke last).
    This reversion is done in the ``generate`` function, called whenever an AI response must be generated.

    Finally, the user can set the next message if it wants to.
    This is done by setting the ``user_message`` parameter, which is None by default.
    If this parameter is provided, no AI response is generated, and the user message is appended to the conversation.

    This method returns the updated conversation, the next character to speak, and an empty string to clear the user message input.

    Parameters
    ----------
    conversation : list[dict]
        List of conversation turns, where each dict contains:
        - 'role': str - either 'user' or 'assistant'
        - 'content': str - the message content
    user_character : str
        Currently selected character ("Character A" or "Character B")
    user_message : str
        Message input by the user. If empty, generates AI response
    name_a : str
        Name of Character A
    story_a : str
        Backstory of Character A
    name_b : str
        Name of Character B
    story_b : str
        Backstory of Character B
    model : str
        LLM model identifier to use
    temperature : float
        LLM temperature parameter (0.0-2.0)
    client : ClientV2
        Initialized Cohere API client

    Returns
    -------
    tuple[list[dict], str, str]
        - Updated conversation history (list[dict])
        - Next character to speak (str)
        - Empty string (str) clearing user message

    Raises
    ------
    ClientError
        If API call fails during response generation
    """
    _template = """
You are a character in a conversation with another character.
Stay in character and respond naturally, as if in a theater play.
Return in natural language, as if you were talking to a friend.
Do not add extra information.

- Name: {name}
- Backstory: {story}

If the first message is "<skip>", ignore it and start the conversation.
"""[1:-1]

    # If a user message is provided, append it without generating an AI response.
    if user_message.strip():
        # Determine message role based on the selected character.
        current_role = "user" if user_character == name_a else "assistant"
        conversation.append({"role": current_role, "content": user_message})
        # Toggle next speaker.
        next_character = name_b if current_role == "user" else name_a
        return conversation, next_character, ""

    # No user message provided, so generate the next message.
    if not conversation:  # Default to assistant if no conversation exists and skip first user message.
        last_role = "assistant" if user_character == name_a else "user"
        conversation = [{"role": "user", "content": "<skip>"}]
    else:
        last_role = conversation[-1].get("role")

    # If the last message was from the assistant, revert roles when generating.
    if last_role == "assistant":
        generated_role = "user"
        system_prompt = _template.format(name=name_a, story=story_a)
        next_character = name_b
    else:
        generated_role = "assistant"
        system_prompt = _template.format(name=name_b, story=story_b)
        next_character = name_a

    # Call the API to generate the response.
    try:
        response_text = generate(
            conversation=conversation,
            model=MODELS.get(model),
            client=client,
            system_prompt=system_prompt,
            temperature=temperature,
        )
    except Exception as e:
        raise e

    conversation.append({"role": generated_role, "content": response_text})
    return conversation, next_character, ""
