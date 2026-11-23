#!/usr/bin/env python3
"""Convert local image/audio inputs to inline Data URIs.

The image generation endpoint officially accepts URL or Data URI inputs.
For video reference media the documented contract is a public HTTPS URL;
inline Data URIs for audio/keyframes are an empirically accepted fallback
(see the skill SKILL.md caveats), not a documented guarantee.
"""
import base64
import mimetypes
import os
import os.path

MAX_IMAGE_BYTES = 15 * 1024 * 1024
MAX_AUDIO_BYTES = 15 * 1024 * 1024

_AUDIO_MIME = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".ogg": "audio/ogg",
    ".oga": "audio/ogg",
    ".flac": "audio/flac",
}


def _data_uri(path, mime):
    with open(path, "rb") as handle:
        raw = handle.read()
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")


def prepare_image(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("image input must be a URL, Data URI, or local file path")
    if value.startswith("data:image/"):
        return value
    if value.startswith(("http://", "https://")):
        return value
    path = os.path.abspath(os.path.expanduser(value))
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    mime = mimetypes.guess_type(path)[0] or "image/png"
    if os.path.getsize(path) > MAX_IMAGE_BYTES:
        raise ValueError("image exceeds the 15MB reference limit")
    return _data_uri(path, mime)


def prepare_audio(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("audio input must be a URL, Data URI, or local file path")
    if value.startswith("data:audio/"):
        return value
    if value.startswith(("http://", "https://")):
        return value
    path = os.path.abspath(os.path.expanduser(value))
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    ext = os.path.splitext(path)[1].lower()
    mime = _AUDIO_MIME.get(ext, "audio/mpeg")
    if os.path.getsize(path) > MAX_AUDIO_BYTES:
        raise ValueError("audio exceeds the 15MB reference limit")
    return _data_uri(path, mime)
