from openai import OpenAI
from app.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def suggest_reply(messages: list[dict]) -> str:
    """
    Given the last few chat messages, suggest a helpful reply.
    messages = [{"sender": "me", "text": "..."}, ...]
    """
    
    conversation = "\n".join(
        f"{'Me' if m['isOwn'] else 'Them'}: {m['text']}"
        for m in messages[-6:]  # Only last 6 messages for context
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[
            {
                "role": "system",
                "content": (
                    "You help socially anxious users reply to messages. "
                    "Suggest a warm, friendly, natural reply in 1-2 short sentences. "
                    "Don't add any explanation — just the reply text."
                )
            },
            {
                "role": "user",
                "content": f"Conversation so far:\n{conversation}\n\nSuggest my next reply:"
            }
        ],
        max_tokens=100,
        temperature=0.7,  # Slightly creative but not random
    )
    return response.choices[0].message.content.strip()


def summarize_conversation(messages: list[dict]) -> str:
    """
    Summarize a list of chat messages into key bullet points.
    """
    text = "\n".join(f"{m['senderId']}: {m['text']}" for m in messages)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Summarize the following conversation in 3-5 clear bullet points."
            },
            {"role": "user", "content": text}
        ],
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


def extract_tasks(text: str) -> list[dict]:
    """
    Extract tasks or reminders from a message.
    Returns a list like: [{"task": "Call dentist", "date": "2025-03-15", "repeat": "none"}]
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract any tasks, deadlines, or reminders from the text. "
                    "Return a JSON array of objects with keys: task, date (YYYY-MM-DD or null), repeat (none/daily/weekly/yearly). "
                    "If no tasks found, return empty array []. "
                    "Return ONLY the JSON array, no other text."
                )
            },
            {"role": "user", "content": text}
        ],
        max_tokens=200,
    )

    import json
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return []  # Return empty list if parsing fails