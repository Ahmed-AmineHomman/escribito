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


def generate(
        conversation: list[dict],
        model: str,
        client: ClientV2,
        system_prompt: str,
        temperature: float = 0.8,
) -> str:
    """
    Generates the next turn of the provided conversation.

    This method calls the API corresponding to the provided ``client`` to generate the turn's content.
    If the provided conversation is empty or undefined, it will generate the first turn of the conversation.

    Parameters
    ----------
    conversation: list of dict
        A gradio `ChatBot` of type "messages" value: a list of dictionaries with keys "role" and "content".
    model: str
        Identifier of the LLM to use for the generation.
    client: cohere.ClientV2
        The Cohere API client.
    system_prompt: str
        The system instructions given to the LLM generating the next message.
    temperature: float
        The temperature of the LLM generating the next message.

    Returns
    -------
    str
        The response from the API.
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
    response = (
        client.chat(model=model, messages=messages, temperature=temperature)
        .message
        .content[0]
        .text
    )

    return response


def download_conversation(
        conversation: list[dict],
        temp_dir: str,
        name_a: str,
        name_b: str,
) -> str:
    """
    Allows the download of the conversation as a JSON file.

    Parameters
    ----------
    conversation: list of dict
        The conversation to download.
    temp_dir: str
        The server's temporary directory where the conversation will be stored.
    name_a: str
        Name of character A (i.e. "user" character).
    name_b: str
        Name of character B (i.e. "assistant" character).
    """
    names = {k: v for k, v in zip(["user", "assistant"], [name_a, name_b])}
    filename = os.path.join(temp_dir, "conversation.json")
    data = [
        {"character": names.get(data.get("role")), "message": data.get("content")}
        for data in conversation
    ]
    with open(filename, "w") as f:
        json.dump(data, f)
    return filename


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
) -> tuple[list, str, str]:
    """
    Generate the next message in the conversation.

    Parameters
    ----------
    conversation : list of tuple
        Conversation history.
        It is a list of dictionaries with each element having two keys: "role" and "content".
        It corresponds to the "messages" type `ChatBot` component.
    user_character: str,
        The character chosen by the user to speak next.
        Only taken into account if ``user_message`` is not empty.
    user_message: str
        The message provided by the user.
        If empty, the next message will be generated by the system.
        Otherwise, the next message will correspond to this user message.
    name_a : str
        Name of character A.
    story_a : str
        Story of character A.
    name_b : str
        Name of character B.
    story_b : str
        Story of character B.
    model: str
        Identifier of the LLM to use for the generation.
    temperature: float
        Temperature of the LLM generating the next message.
    client: cohere.ClientV2
        The Cohere API client.

    Returns
    -------
    list
        A ``list`` of ``dict`` containing all the turns of the conversation.
        This object satisfies the "messages" values of the gradio ``Chatbot`` component.
        Each element of the list has two keys: "role" and "content".
    """
    _template = """
You will play the part of a given character, involved in a conversation with another character.
You will assume that this other character is the user, and you will respond as your character, which is described below.

- Name: {name},
- Backstory: {story}.

Take care in only replying as your character and to never break the fourth curtain.
And remember, you response should be in the form of a dialogue, as if you were speaking to the user.
"""

    # Determine the last & next speaker
    if not conversation:  # if conversation is empty -> we assume that A speaks first
        last_character = "Character A"
    else:
        last_character = CHARACTERS.get(conversation[-1].get("role"))

    # If the user provided a message -> append user message to conversation
    # If it did not -> generate a new turn in the conversation
    if user_message:
        next_character = user_character

        # If conversation is empty -> user message is the first message
        # Otherwise, we append the user message to the conversation
        if not conversation:
            conversation = [{"role": ROLES.get(user_character), "content": user_message}]
        else:
            # if next & last role are identical -> append user message to last turn of conversation
            # otherwise, append a new turn to the conversation
            if user_character == last_character:
                data = conversation[-1]
                conversation[-1] = {"role": data.get("role"), "content": f"{data.get('content')} {user_message}"}
            else:
                conversation.append({"role": ROLES.get(user_character), "content": user_message})
    else:
        next_character = "Character B" if last_character == "Character A" else "Character A"

        # set the system prompt
        if next_character == "Character A":
            system_prompt = _template.format(name=name_a, story=story_a)
        else:
            system_prompt = _template.format(name=name_b, story=story_b)

        # generate the next turn
        params = dict(
            client=client,
            system_prompt=system_prompt,
            model=MODELS.get(model),
            temperature=temperature,
        )
        if not conversation:  # if conversation is empty -> generate the first turn from empty user message
            temp = [{"role": "user", "content": " "}]
        else:  # if conversation exists -> provide it as-is
            temp = conversation
        response = generate(conversation=temp, **params)
        conversation.append({"role": ROLES.get(next_character), "content": response})

    # switch the next role & reset user message
    user_character = "Character A" if next_character == "Character B" else "Character B"
    user_message = ""
    return conversation, user_character, user_message
