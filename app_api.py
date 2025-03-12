from cohere import ClientV2

CHARACTERS = [
    "Character A",
    "Character B",
]


def build_conversation(
        conversation,
        name_a: str,
        name_b: str,
) -> str:
    """
    Builds the conversation for display using Markdown.
    """
    names = {"Character A": name_a, "Character B": name_b}
    return "\n\n".join([f"### {names.get(role)}\n{msg}" for role, msg in conversation])


def reset_conversation() -> tuple[str, list]:
    """
    Resets the conversation.
    """
    return "", []


def next_message(
        conversation,
        user_role: str,
        user_message: str,
        name_a: str,
        story_a: str,
        name_b: str,
        story_b: str,
        client: ClientV2,
) -> tuple[str, list, str, str]:
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
    client: cohere.ClientV2
        The Cohere API client.

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
    # Determine the last & next speaker
    if not conversation:  # if conversation is empty -> we assume that A speaks first
        last_role = "Character A"
    else:
        last_role, _ = conversation[-1]

    # If the user provided a message -> append user message to conversation
    # If it did not -> generate a new turn in the conversation
    if user_message:
        next_role = user_role

        # If conversation is empty -> user message is the first message
        # Otherwise, we append the user message to the conversation
        if not conversation:
            conversation = [(user_role, user_message)]
        else:
            # if next & last role are identical -> append user message to last turn of conversation
            # otherwise, append a new turn to the conversation
            if user_role == last_role:
                role, message = conversation[-1]
                conversation[-1] = (role, f"{message} {user_message}")
            else:
                conversation.append((user_role, user_message))
    else:
        next_role = "Character B" if last_role == "Character A" else "Character A"

        # initialize conversation
        messages: list[dict[str, str]] = []

        # set system prompt
        if next_role == "Character A":
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
            client.chat(
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
    markdown_text = build_conversation(
        conversation=conversation,
        name_a=name_a,
        name_b=name_b,
    )

    # switch the next role & reset user message
    user_role = "Character A" if next_role == "Character B" else "Character B"
    user_message = ""
    return markdown_text, conversation, user_role, user_message
