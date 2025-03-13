import json
import os

from cohere import ClientV2

CHARACTERS = {
    "user": "Character A",
    "assistant": "Character B",
}
ROLES = {v: k for k, v in CHARACTERS.items()}
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
    # initialize messages with system prompt
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    # append the conversation turns to the messages
    last_role = conversation[-1].get("role")
    if last_role == "assistant":  # if conversation ends with "assistant" -> revert the roles
        messages += [
            {"role": "user" if data.get("role") == "assistant" else "assistant", "content": data.get("content")}
            for data in conversation
        ]
    else:
        messages += conversation

    # call the API
    try:
        response = (
            client.chat(model=model, messages=messages, temperature=temperature)
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


def _determine_next_speaker(
        conversation: list[dict],
        user_character: str | None = None
) -> str:
    """Determines who speaks next based on conversation history and user input."""
    if user_character:
        return user_character
    if not conversation:
        return "Character A"
    last_character = CHARACTERS.get(conversation[-1].get("role"))
    return "Character B" if last_character == "Character A" else "Character A"


def _append_user_message(
        conversation: list[dict],
        user_message: str,
        user_character: str
) -> list[dict]:
    """Handles adding a user message to the conversation."""
    if not conversation:
        return [{"role": ROLES.get(user_character), "content": user_message}]

    last_turn = conversation[-1]
    if user_character == CHARACTERS.get(last_turn.get("role")):
        conversation[-1] = {
            "role": last_turn.get("role"),
            "content": f"{last_turn.get('content')} {user_message}"
        }
        return conversation

    conversation.append({"role": ROLES.get(user_character), "content": user_message})
    return conversation


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
    """Generate or append the next message in a character conversation.

    The function either adds a user message to the conversation or generates
    an AI response based on the current context and character roles.

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
You will play the part of a given character, involved in a conversation with another character.
You will assume that this other character is the user, and you will respond as your character, which is described below.

- Name: {name},
- Backstory: {story}.

Take care in only replying as your character and to never break the fourth curtain.
And remember, you response should be in the form of a dialogue, as if you were speaking to the user.
"""
    next_character = _determine_next_speaker(conversation, user_character if user_message else None)

    if user_message:
        conversation = _append_user_message(conversation, user_message, next_character)
    else:
        # Generate AI response
        system_prompt = _template.format(
            name=name_a if next_character == "Character A" else name_b,
            story=story_a if next_character == "Character A" else story_b
        )

        temp_convo = [{"role": "user", "content": " "}] if not conversation else conversation
        response = generate(
            conversation=temp_convo,
            client=client,
            system_prompt=system_prompt,
            model=MODELS.get(model),
            temperature=temperature,
        )
        conversation.append({"role": ROLES.get(next_character), "content": response})

    return (
        conversation,
        "Character A" if next_character == "Character B" else "Character B",
        ""
    )
