# Weekly Agent Voice Briefings — an ElevenLabs prototype

A prototype exploring how voice AI could personalize a recurring operational touchpoint I run
today by hand: getting the right nudge, in the right tone, to the right distribution agent, every week.

## The problem

At Prudential Singapore, I run a bi-weekly commercial forum that turns seller-push and customer-pull
signals into a strategy memo for the CDO, CEO, and CFO. That memo is precise and well-targeted — but
it's built for leadership, not for the 6,000+ agents whose day-to-day behavior actually moves the number.
Agents get generic, one-size-fits-all campaign comms. The information that *should* reach them —
"you have 3 stale Shield leads and the campaign closes in 4 days" — usually doesn't, or arrives too
generic to act on.

## The idea

A short (60-90 second) personalized weekly voice briefing per agent, generated from their own pipeline,
production trend, and live campaign eligibility — delivered in their language, in the voice of one of
three senior leaders, randomly assigned each week. The randomization is a small, deliberate product
choice: agents don't know whether Rom, Ben, or SanSan will be "speaking" to them this week, which makes
a routine operational nudge something they might actually look forward to.

**Important note on the voices:** "Rom," "Ben," and "SanSan" are pre-built ElevenLabs library voices,
simply given fun internal nicknames for this demo. They are not clones of any real individual's voice.
Voice cloning a real, named executive without their explicit consent is exactly the kind of misuse
ElevenLabs' own safety systems are designed to catch — so this prototype deliberately avoids it,
even though it costs a little of the "wow" factor of the real thing.

## What's actually built (Phase 1)

- **A synthetic CRM**, modeled as four tables (`data/`): `agents`, `leads`, `production`, `campaigns` —
  mirroring the kind of multi-source join I do today in Alteryx/Tableau, just smaller and fully fake.
  No real Prudential (or any company's) data is used anywhere in this repo.
- **`generate_data.py`** — creates the synthetic dataset (10 agents, ~2 languages, varied tenure,
  trend, and campaign eligibility).
- **`generate_messages.py`** — joins the four tables per agent and calls the Claude API to write a
  personalized script in the tone of that week's assigned persona, in English or Mandarin.
- **`generate_audio.py`** — converts each script to audio via the ElevenLabs Text-to-Speech API,
  using the voice mapped to that agent's assigned persona.
- **A real localization constraint I hit and had to design around**: of the three ElevenLabs voices
  I picked, only one performs well in Mandarin. Rather than force a bad-quality Mandarin voice on
  agents who need it, Mandarin-speaking agents are always routed to the Mandarin-capable persona,
  while English-speaking agents get the full random rotation. Small decision, but it's the kind of
  thing that only shows up once you actually build something instead of just describing it.

## Sample outputs

See `output/` for 2-3 sample MP3s and their corresponding scripts — different agents, different
trends (declining/flat/improving), different personas, different languages.

## Phase 2 (proposed, not built)

- **Delivery via WhatsApp** rather than a manually-played file, so briefings land where agents already
  are.
- **Extending the same mechanic upward**: a GM's weekly written update to a regional team, turned into
  a short multilingual voice briefing pushed to the team — the same "operating rhythm on voice" idea,
  aimed at leadership coordination rather than agent activation.
- **Agent voice-note replies flowing back up** — closing the loop so the operating rhythm runs in both
  directions.

## Why I built this

I'm exploring the Chief of Staff, APAC role at ElevenLabs, and I didn't want to apply on enthusiasm
alone. This is a genuine (if small) attempt to think the way I'd want to think in that role: start
from a real operating problem I already own, and ask what ElevenLabs' actual product stack would
change about it.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in your own API keys
cd src
python generate_data.py
python generate_messages.py
python generate_audio.py
```

Requires an Anthropic API key and an ElevenLabs API key (Text to Speech: Access, Voices: Read is
sufficient — no other scopes needed).
