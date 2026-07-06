"""
generate_audio.py

Reads data/messages.json (produced by generate_messages.py) and converts each
agent's script to an MP3 using ElevenLabs text-to-speech, using the voice ID
mapped to that agent's assigned exec persona for the week.

Output: output/<agent_id>_<agent_name>.mp3
"""

import json
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from config import PERSONA_VOICE_IDS, ELEVENLABS_MODEL

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

DATA_DIR = "../data"
OUTPUT_DIR = "../output"


def generate_all_audio():
    with open(f"{DATA_DIR}/messages.json") as f:
        messages = json.load(f)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for m in messages:
        voice_id = PERSONA_VOICE_IDS[m["assigned_exec"]]
        safe_name = m["agent_name"].replace(" ", "_")
        out_path = f"{OUTPUT_DIR}/{m['agent_id']}_{safe_name}.mp3"

        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id=ELEVENLABS_MODEL,
            text=m["script"],
        )

        with open(out_path, "wb") as f:
            for chunk in audio:
                if chunk:
                    f.write(chunk)

        print(f"Saved audio for {m['agent_name']} ({m['assigned_exec']}) -> {out_path}")

    print(f"\nDone. {len(messages)} audio files written to {OUTPUT_DIR}/")


if __name__ == "__main__":
    generate_all_audio()
