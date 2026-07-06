"""
generate_data.py

Creates a small, fully synthetic CRM dataset for the agent-briefing prototype.
No real Prudential (or any real company) data is used anywhere in this file —
all agent names, lead figures, and campaign details are invented for demo purposes.

Produces 4 CSVs in ../data/:
  - agents.csv      (dimension table: who the agents are)
  - leads.csv       (fact table: open pipeline by product)
  - production.csv  (fact table: monthly output by product)
  - campaigns.csv   (fact table: active campaigns + agent progress)
"""

import csv
import random
from datetime import date, timedelta

random.seed(42)  # reproducible demo data

OUT_DIR = "../data"

PRODUCTS = ["Wealth", "Protection", "Shield", "Retirement"]
CHANNELS = ["Agency", "Bancassurance"]
PERSONAS = ["Rom", "Ben", "SanSan"]  # ElevenLabs pre-built voices, named as a fun weekly device.
                                     # These are NOT clones of any real individual's voice.

TODAY = date(2026, 7, 6)


def random_date(days_back_min, days_back_max):
    delta = random.randint(days_back_min, days_back_max)
    return TODAY - timedelta(days=delta)


# ---------- Table 1: agents.csv ----------
agents = [
    {"agent_id": "A001", "agent_name": "Priya Nair", "language": "en", "channel": "Agency", "tenure_months": 8},
    {"agent_id": "A002", "agent_name": "Wei Ming Tan", "language": "zh", "channel": "Agency", "tenure_months": 34},
    {"agent_id": "A003", "agent_name": "Farah Yusof", "language": "en", "channel": "Bancassurance", "tenure_months": 14},
    {"agent_id": "A004", "agent_name": "Kevin Goh", "language": "en", "channel": "Agency", "tenure_months": 3},
    {"agent_id": "A005", "agent_name": "Li Xin", "language": "zh", "channel": "Bancassurance", "tenure_months": 22},
    {"agent_id": "A006", "agent_name": "Amirah Hassan", "language": "en", "channel": "Agency", "tenure_months": 61},
    {"agent_id": "A007", "agent_name": "Jason Lim", "language": "en", "channel": "Bancassurance", "tenure_months": 11},
    {"agent_id": "A008", "agent_name": "Zhang Wei", "language": "zh", "channel": "Agency", "tenure_months": 5},
    {"agent_id": "A009", "agent_name": "Nur Aisyah", "language": "en", "channel": "Agency", "tenure_months": 19},
    {"agent_id": "A010", "agent_name": "Marcus Teo", "language": "en", "channel": "Bancassurance", "tenure_months": 45},
]

# NOTE: who speaks to an agent (Rom/Ben/SanSan) is a WEEKLY fact, not a stable attribute of
# the agent — so it deliberately does NOT live in this table. See assign_weekly_personas.py,
# which is re-run each time you generate a new week's briefings.

with open(f"{OUT_DIR}/agents.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["agent_id", "agent_name", "language", "channel", "tenure_months"])
    writer.writeheader()
    writer.writerows(agents)


# ---------- Table 2: leads.csv ----------
leads = []
lead_counter = 1
for a in agents:
    n_leads = random.randint(2, 6)
    for _ in range(n_leads):
        created = random_date(3, 45)
        last_contact = created + timedelta(days=random.randint(0, min(20, (TODAY - created).days)))
        leads.append({
            "lead_id": f"L{lead_counter:04d}",
            "agent_id": a["agent_id"],
            "product_category": random.choice(PRODUCTS),
            "lead_created_date": created.isoformat(),
            "last_contact_date": last_contact.isoformat(),
            "lead_stage": random.choice(["New", "Contacted", "Proposal", "Closing"]),
            "estimated_case_size": random.choice([5000, 8000, 12000, 15000, 20000, 30000]),
        })
        lead_counter += 1

with open(f"{OUT_DIR}/leads.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["lead_id", "agent_id", "product_category", "lead_created_date",
                                            "last_contact_date", "lead_stage", "estimated_case_size"])
    writer.writeheader()
    writer.writerows(leads)


# ---------- Table 3: production.csv ----------
production = []
months = ["2026-05", "2026-06", "2026-07"]
for a in agents:
    # give each agent a "trend" so messages can be genuinely differentiated
    trend = random.choice(["declining", "flat", "improving"])
    base_pct = random.randint(50, 90)
    for i, m in enumerate(months):
        if trend == "declining":
            pct = max(20, base_pct - i * 15)
        elif trend == "improving":
            pct = min(110, base_pct + i * 12)
        else:
            pct = base_pct + random.randint(-5, 5)
        for product in random.sample(PRODUCTS, k=random.randint(1, 3)):
            production.append({
                "agent_id": a["agent_id"],
                "month": m,
                "product_category": product,
                "cases_closed": random.randint(0, 5),
                "case_value": random.choice([4000, 9000, 14000, 22000]),
                "vs_target_pct": pct,
            })
    a["_trend"] = trend  # stash for message logic later (not written to agents.csv)

with open(f"{OUT_DIR}/production.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["agent_id", "month", "product_category", "cases_closed",
                                            "case_value", "vs_target_pct"])
    writer.writeheader()
    writer.writerows(production)


# ---------- Table 4: campaigns.csv ----------
campaign_defs = [
    {"campaign_id": "C01", "campaign_name": "Shield Rider Wealth Push", "product_category": "Shield",
     "start_date": "2026-06-01", "end_date": "2026-07-15", "incentive_type": "Cash bonus"},
    {"campaign_id": "C02", "campaign_name": "New Agent Ramp Bonus", "product_category": "Protection",
     "start_date": "2026-06-15", "end_date": "2026-08-01", "incentive_type": "Recognition"},
    {"campaign_id": "C03", "campaign_name": "Retirement Season Sprint", "product_category": "Retirement",
     "start_date": "2026-06-01", "end_date": "2026-07-31", "incentive_type": "Trip qualifier"},
]

campaigns_rows = []
for a in agents:
    # each agent eligible for 1-2 campaigns
    eligible = random.sample(campaign_defs, k=random.randint(1, 2))
    for c in eligible:
        campaigns_rows.append({
            **c,
            "agent_id": a["agent_id"],
            "agent_progress_pct": random.randint(10, 95),
        })

with open(f"{OUT_DIR}/campaigns.csv", "w", newline="") as f:
    fieldnames = ["campaign_id", "campaign_name", "product_category", "start_date", "end_date",
                  "incentive_type", "agent_id", "agent_progress_pct"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(campaigns_rows)


# ---------- Store trend separately since it's a derived/demo-only signal ----------
with open(f"{OUT_DIR}/agent_trends.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["agent_id", "trend"])
    writer.writeheader()
    writer.writerows([{"agent_id": a["agent_id"], "trend": a["_trend"]} for a in agents])

print("Generated: agents.csv, leads.csv, production.csv, campaigns.csv, agent_trends.csv in", OUT_DIR)
