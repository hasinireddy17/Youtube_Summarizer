"""
Fetches transcripts for YouTube videos using youtube-transcript-api.
No YouTube API key needed for this part.

Note: v1.0+ of youtube-transcript-api switched from static methods to an
instance-based API (YouTubeTranscriptApi().fetch(...) instead of
YouTubeTranscriptApi.get_transcript(...)).
"""
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url_or_id: str) -> str:
    """Handle full URLs, shortened youtu.be links, or a raw video ID."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"(?:youtu\.be\/)([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    if re.fullmatch(r"[0-9A-Za-z_-]{11}", url_or_id):
        return url_or_id
    raise ValueError("Could not extract a video ID from that input.")


def get_transcript_text(url_or_id: str) -> str:
    video_id = extract_video_id(url_or_id)
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched = ytt_api.fetch(video_id)
        return " ".join(snippet.text for snippet in fetched)
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise ValueError("No transcript found for this video.")