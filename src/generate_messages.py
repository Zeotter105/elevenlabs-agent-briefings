"""
generate_messages.py

Joins the 4 synthetic CRM tables plus this week's persona assignment into a
per-agent context, then calls Claude to write a short (~60-90 second spoken)
personalized weekly briefing script, in the voice/tone of that agent's
assigned exec persona this week.

Run order: generate_data.py -> assign_weekly_personas.py -> generate_messages.py -> generate_audio.py

Output: data/messages.json — one entry per agent with the generated script text.
"""

import csv
import json
import os
from collections import defaultdict
from dotenv import load_dotenv
from anthropic import Anthropic
from config import PERSONA_TONE_NOTES

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

DATA_DIR = "../data"


def load_csv(name):
    with open(f"{DATA_DIR}/{name}") as f:
        return list(csv.DictReader(f))


def build_agent_context():
    agents = load_csv("agents.csv")
    leads = load_csv("leads.csv")
    production = load_csv("production.csv")
    campaigns = load_csv("campaigns.csv")
    trends = {r["agent_id"]: r["trend"] for r in load_csv("agent_trends.csv")}
    weekly_assignment = {r["agent_id"]: r["assigned_exec"] for r in load_csv("weekly_assignment.csv")}

    leads_by_agent = defaultdict(list)
    for l in leads:
        leads_by_agent[l["agent_id"]].append(l)

    campaigns_by_agent = defaultdict(list)
    for c in campaigns:
        campaigns_by_agent[c["agent_id"]].append(c)

    # latest month production per agent/product
    latest_month = max(r["month"] for r in production)
    prod_latest = [r for r in production if r["month"] == latest_month]
    prod_by_agent = defaultdict(list)
    for r in prod_latest:
        prod_by_agent[r["agent_id"]].append(r)

    contexts = []
    for a in agents:
        aid = a["agent_id"]
        stale_leads = [l for l in leads_by_agent[aid] if l["lead_stage"] != "Closing"]
        top_campaign = max(campaigns_by_agent[aid], key=lambda c: 100 - int(c["agent_progress_pct"]), default=None)
        contexts.append({
            "agent_id": aid,
            "agent_name": a["agent_name"],
            "language": a["language"],
            "channel": a["channel"],
            "tenure_months": a["tenure_months"],
            "assigned_exec": weekly_assignment[aid],
            "trend": trends[aid],
            "open_leads_count": len(leads_by_agent[aid]),
            "stale_lead_products": list({l["product_category"] for l in stale_leads}),
            "production_snapshot": prod_by_agent[aid],
            "top_campaign": top_campaign,
        })
    return contexts


def build_prompt(ctx):
    persona = ctx["assigned_exec"]
    tone_note = PERSONA_TONE_NOTES[persona]
    lang_instruction = "Write the script in natural, spoken Mandarin Chinese." if ctx["language"] == "zh" \
        else "Write the script in natural, spoken English."

    campaign_line = ""
    if ctx["top_campaign"]:
        c = ctx["top_campaign"]
        campaign_line = (f"They are {c['agent_progress_pct']}% toward the '{c['campaign_name']}' campaign "
                          f"threshold (product: {c['product_category']}, ends {c['end_date']}, "
                          f"incentive: {c['incentive_type']}).")

    stale_line = (f"They have open/stale leads in: {', '.join(ctx['stale_lead_products'])}."
                  if ctx["stale_lead_products"] else "They have no notably stale leads right now.")

    return f"""You are writing a short spoken script for {persona} ({tone_note}).

The script is a weekly personal voice briefing to an insurance agent named {ctx['agent_name']}
({ctx['channel']} channel, {ctx['tenure_months']} months tenure). Their recent production trend is
"{ctx['trend']}" versus target.

{stale_line}
{campaign_line}

{lang_instruction}

Requirements:
- 3 short beats: (1) one specific, personal observation about their week, (2) one clear action tied to
  the live campaign or stale leads, (3) a brief motivating close in {persona}'s voice.
- Warm and direct. If the trend is "declining", be supportive and constructive — never shaming or guilt-tripping.
  If "improving", genuinely celebrate it. If "flat", nudge with specific encouragement.
- Target length: 140-160 words (~60-90 seconds spoken).
- Output ONLY the spoken script text, nothing else — no headers, no stage directions, no quotation marks."""


def generate_all_messages():
    contexts = build_agent_context()
    results = []
    for ctx in contexts:
        prompt = build_prompt(ctx)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        script_text = response.content[0].text.strip()
        results.append({
            "agent_id": ctx["agent_id"],
            "agent_name": ctx["agent_name"],
            "language": ctx["language"],
            "assigned_exec": ctx["assigned_exec"],
            "trend": ctx["trend"],
            "script": script_text,
        })
        print(f"Generated script for {ctx['agent_name']} ({ctx['assigned_exec']}, {ctx['language']})")

    with open(f"{DATA_DIR}/messages.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(results)} scripts to {DATA_DIR}/messages.json")


if __name__ == "__main__":
    generate_all_messages()
