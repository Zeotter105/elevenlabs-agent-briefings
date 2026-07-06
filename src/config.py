"""
config.py — persona / voice mapping and small shared constants.

IMPORTANT: These are ElevenLabs *pre-built library voices*, simply labeled with
fun internal nicknames (Rom / Ben / SanSan) for the demo. They are NOT voice
clones of any real person. See README.md for why this distinction matters.
"""

# Fill these in with your actual ElevenLabs voice IDs (Voice Library -> your saved voices).
PERSONA_VOICE_IDS = {
    "Rom":    "FXMPPfJPpDj0GSwJ6ASO",
    "Ben":    "mbL34QDB5FptPamlgvX5",   # <- set this to the one that supports Mandarin
    "SanSan": "eL7xfWghif0oJwtmX2qs",
}

# Which persona voice actually supports Mandarin well (only one of the three does).
MANDARIN_CAPABLE_PERSONA = "Ben"

PERSONA_TONE_NOTES = {
    "Rom":    "Chief Agency Officer — energetic, floor-focused, speaks like a coach who knows every agent by name.",
    "Ben":    "Chief Distribution Officer — calm, strategic, speaks in terms of the bigger channel picture.",
    "SanSan": "CEO — brief, inspirational, makes the agent feel part of something bigger than their own number.",
}

ELEVENLABS_MODEL = "eleven_multilingual_v2"  # supports English + Mandarin
