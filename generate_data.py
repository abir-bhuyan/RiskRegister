"""
RiskRegister - synthetic data generator.

Builds an enterprise risk register for a fictional mid-size retailer
("Northwind Retail Group"). Each row is a risk with inherent likelihood/impact,
a mapped control, control effectiveness, and a residual rating - the structure
used in real governance / risk management frameworks (e.g. ISO 31000 style).

All data is synthetic.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd

RNG = np.random.default_rng(7)
DATA_DIR = Path(__file__).parent / "data"

CATEGORIES = ["Cyber & Data", "Financial", "Operational",
              "Compliance & Legal", "People", "Strategic", "ESG"]
OWNERS = ["CISO", "CFO", "COO", "Head of Legal", "Head of HR",
          "CEO", "Head of Sustainability"]
CONTROL_TYPES = ["Preventive", "Detective", "Corrective"]
COMPLIANCE_FRAMEWORKS = ["APRA CPS 234", "Privacy Act", "ISO 27001",
                         "WHS Act", "Modern Slavery Act", "None"]

RISK_TEMPLATES = [
    ("Cyber & Data", "Ransomware attack encrypts core systems"),
    ("Cyber & Data", "Customer PII breach via third-party vendor"),
    ("Cyber & Data", "Phishing leads to credential compromise"),
    ("Financial", "Inaccurate revenue recognition"),
    ("Financial", "Cash-flow shortfall during peak season"),
    ("Financial", "Fraudulent supplier payments"),
    ("Operational", "Key supplier fails to deliver"),
    ("Operational", "Warehouse fire disrupts distribution"),
    ("Operational", "Point-of-sale outage during trading"),
    ("Compliance & Legal", "Breach of consumer guarantees"),
    ("Compliance & Legal", "Late statutory reporting"),
    ("People", "Loss of key personnel"),
    ("People", "Skills shortage in analytics team"),
    ("Strategic", "New entrant undercuts pricing"),
    ("Strategic", "Failure to adapt to e-commerce shift"),
    ("ESG", "Modern slavery in supply chain"),
    ("ESG", "Excess packaging waste / regulatory penalty"),
    ("ESG", "Scope 3 emissions disclosure gap"),
]


def _residual(inh_score: int, effectiveness: str) -> int:
    factor = {"Strong": 0.45, "Adequate": 0.7, "Weak": 0.95}[effectiveness]
    return max(1, int(round(inh_score * factor)))


def generate() -> pd.DataFrame:
    rows = []
    for i in range(80):
        cat, title = RISK_TEMPLATES[RNG.integers(0, len(RISK_TEMPLATES))]
        owner = OWNERS[CATEGORIES.index(cat)]
        likelihood = int(RNG.integers(1, 6))       # 1..5
        impact = int(RNG.integers(1, 6))           # 1..5
        inherent = likelihood * impact             # 1..25
        effectiveness = RNG.choice(["Strong", "Adequate", "Weak"],
                                   p=[0.35, 0.45, 0.20])
        residual = _residual(inherent, effectiveness)
        framework = (RNG.choice(COMPLIANCE_FRAMEWORKS)
                     if cat in ("Cyber & Data", "Compliance & Legal", "ESG")
                     else "None")
        last_review = pd.Timestamp("2025-09-01") + pd.Timedelta(
            days=int(RNG.integers(-330, 230)))
        overdue = (pd.Timestamp("2026-05-30") - last_review).days > 365
        rows.append([
            f"R{i+1:03d}", cat, title, owner,
            RNG.choice(CONTROL_TYPES), effectiveness,
            likelihood, impact, inherent, residual,
            framework, last_review.date().isoformat(),
            "Overdue" if overdue else "Current",
        ])
    return pd.DataFrame(rows, columns=[
        "risk_id", "category", "risk_title", "owner", "control_type",
        "control_effectiveness", "likelihood", "impact", "inherent_score",
        "residual_score", "compliance_framework", "last_review_date",
        "review_status"])


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    df = generate()
    df.to_csv(DATA_DIR / "risk_register.csv", index=False)
    con = sqlite3.connect(DATA_DIR / "risks.db")
    df.to_sql("risks", con, if_exists="replace", index=False)
    con.close()
    print(f"Wrote {len(df)} risks to data/risk_register.csv and data/risks.db")


if __name__ == "__main__":
    main()
