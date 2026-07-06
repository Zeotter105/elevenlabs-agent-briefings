"""
assign_weekly_personas.py

Assigns each agent a persona (Rom / Ben / SanSan) for THIS week's briefing.

This is deliberately separate from generate_data.py: who speaks to an agent is a
weekly-changing fact, not a stable attribute of the agent, so it shouldn't live in
agents.csv. Re-run this script each time you want to generate a new week's briefings —
it overwrites data/weekly_assignment.csv with a fresh random assignment.

Rule: Mandarin-speaking agents always get the Mandarin-capable persona (only one of our
three ElevenLabs voices currently performs well in Mandarin). English-speaking agents get
a random pick across all three, each week.
"""

import csv
import random
from config import MANDARIN_CAPABLE_PERSONA

PERSONAS = ["Rom", "Ben", "SanSan"]
DATA_DIR = "../data"


def assign_weekly_personas(week_label="2026-W27"):
    with open(f"{DATA_DIR}/agents.csv") as f:
        agents = list(csv.DictReader(f))

    assignments = []
    for a in agents:
        if a["language"] == "zh":
            exec_assigned = MANDARIN_CAPABLE_PERSONA
        else:
            exec_assigned = random.choice(PERSONAS)
        assignments.append({
            "agent_id": a["agent_id"],
            "week": week_label,
            "assigned_exec": exec_assigned,
        })

    with open(f"{DATA_DIR}/weekly_assignment.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["agent_id", "week", "assigned_exec"])
        writer.writeheader()
        writer.writerows(assignments)

    print(f"Assigned personas for week {week_label} -> {DATA_DIR}/weekly_assignment.csv")
    return assignments


if __name__ == "__main__":
    assign_weekly_personas()
