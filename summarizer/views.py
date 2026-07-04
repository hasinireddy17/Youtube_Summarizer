from django.shortcuts import render
from .transcript import get_transcript_text
from .llm import summarize_transcript, generate_quiz, generate_flashcards


def home(request):
    context = {}

    if request.method == "POST":
        url = request.POST.get("video_url", "").strip()
        context["video_url"] = url

        try:
            transcript = get_transcript_text(url)
            summary = summarize_transcript(transcript)
            quiz = generate_quiz(summary)
            flashcards = generate_flashcards(summary)

            context["summary"] = summary
            context["quiz"] = quiz
            context["flashcards"] = flashcards

        except ValueError as e:
            context["error"] = str(e)
        except Exception as e:
            context["error"] = f"Something went wrong: {e}"

    return render(request, "summarizer/home.html", context)
