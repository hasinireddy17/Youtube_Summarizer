# YouTube Video Summarizer

An AI-powered web app that summarizes YouTube videos and auto-generates
quizzes and flashcards from the content, built with Django and the
Claude (Anthropic) LLM API.

## Features
- Paste any YouTube URL and fetch its transcript (no YouTube API key needed)
- Long transcripts are chunked and summarized using a map-reduce strategy
  to stay within LLM context limits
- Auto-generates multiple-choice quiz questions from the summary
- Auto-generates flashcards (front/back) for studying
- Simple Django server-rendered UI

## Tech Stack
- **Backend:** Django
- **Transcript fetching:** youtube-transcript-api
- **LLM:** Groq API (free tier, Llama 3.3 70B, OpenAI-compatible endpoint, via `requests`)

## Setup

```bash
pip install -r requirements.txt
export GROQ_API_KEY="gsk_..."   # free key from https://console.groq.com/keys
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and paste a YouTube link.

## How it works
1. `transcript.py` extracts the video ID from any YouTube URL format and
   pulls the transcript via `youtube-transcript-api`.
2. `llm.py` chunks long transcripts (~8000 chars/chunk) and summarizes each
   chunk, then does a second summarization pass over the partial summaries
   to produce one clean final summary (map-reduce pattern — avoids blowing
   past the model's context window on long videos).
3. The summary is then used to prompt the LLM twice more: once for a JSON
   quiz, once for JSON flashcards.
4. `views.py` orchestrates the pipeline and renders results in
   `templates/summarizer/home.html`.

## Design decisions worth mentioning in an interview
- Used `youtube-transcript-api` instead of the official YouTube Data API
  because it doesn't require API key setup/quota management just to pull
  captions — the Data API would be needed only for metadata like title/
  channel, which wasn't in scope here.
- Chose a map-reduce summarization strategy over simple truncation so
  longer videos don't lose information from the back half of the transcript.
- Quiz/flashcard generation is done as separate LLM calls (not one giant
  prompt) so each output is easier to validate/parse independently as JSON.
