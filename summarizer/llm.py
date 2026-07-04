"""
LLM helper — calls Groq's free API (OpenAI-compatible) to summarize a
transcript and generate quiz questions + flashcards from it.

Get a free key at https://console.groq.com/keys (no credit card needed),
then set it as an environment variable before running:
    export GROQ_API_KEY="gsk_..."
"""
import os
import json
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"  # free, fast, strong general-purpose model on Groq


def _call_llm(prompt: str, max_tokens: int = 1500) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def chunk_text(text: str, max_chars: int = 8000):
    """Split long transcripts into chunks so we don't blow past context limits."""
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind(". ", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(text[:split_at + 1])
        text = text[split_at + 1:]
    if text:
        chunks.append(text)
    return chunks


def summarize_transcript(transcript: str) -> str:
    """Map-reduce summarization: summarize each chunk, then summarize the summaries."""
    chunks = chunk_text(transcript)

    if len(chunks) == 1:
        prompt = f"Summarize this video transcript in 5-8 clear bullet points:\n\n{chunks[0]}"
        return _call_llm(prompt)

    partial_summaries = []
    for i, chunk in enumerate(chunks):
        prompt = f"Summarize this part ({i+1}/{len(chunks)}) of a video transcript in 3-4 bullet points:\n\n{chunk}"
        partial_summaries.append(_call_llm(prompt, max_tokens=500))

    combined = "\n\n".join(partial_summaries)
    final_prompt = f"Combine these partial summaries into one clean, non-repetitive 6-10 bullet point summary of the full video:\n\n{combined}"
    return _call_llm(final_prompt)


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def generate_quiz(summary: str, num_questions: int = 5):
    """Ask the LLM to return quiz questions as JSON."""
    prompt = f"""Based on this video summary, create {num_questions} multiple-choice quiz questions.

Respond with ONLY valid JSON (no markdown fences, no preamble), in this exact format:
[
  {{"question": "...", "options": ["Option text 1", "Option text 2", "Option text 3", "Option text 4"], "answer": "Option text 1"}}
]

IMPORTANT: the "answer" value must be an EXACT character-for-character copy of one of the strings in "options" for that question — not a letter like A/B/C/D, just the full option text repeated.

Summary:
{summary}"""

    raw = _call_llm(prompt, max_tokens=1200)
    try:
        return json.loads(_clean_json(raw))
    except json.JSONDecodeError:
        return []


def generate_flashcards(summary: str, num_cards: int = 8):
    """Ask the LLM to return flashcards as JSON."""
    prompt = f"""Based on this video summary, create {num_cards} flashcards for studying.

Respond with ONLY valid JSON (no markdown fences, no preamble), in this exact format:
[
  {{"front": "term or question", "back": "definition or answer"}}
]

Summary:
{summary}"""
    raw = _call_llm(prompt, max_tokens=1000)
    try:
        return json.loads(_clean_json(raw))
    except json.JSONDecodeError:
        return []
