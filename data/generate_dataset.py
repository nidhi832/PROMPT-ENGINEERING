"""Generate SpendWise's synthetic, labelled datasets (no real personal data).

Outputs (in this folder):
  labelled_transactions.csv  ~200 rows with ground-truth category + split (dev/test 70/30)
  sample_expenses.csv        3 months of realistic transactions for the live demo (no labels)

Run:  python data/generate_dataset.py
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).parent
SEED = 42

# (description template, category, (min_amount, max_amount), is_ambiguous)
MERCHANTS: list[tuple[str, str, tuple[int, int], bool]] = [
    # Food
    ("Swiggy order #{n}", "Food", (150, 650), False),
    ("Zomato - {r}", "Food", (180, 900), False),
    ("Dominos Pizza", "Food", (250, 800), False),
    ("Starbucks Coffee", "Food", (220, 550), False),
    ("BigBasket groceries", "Food", (400, 2500), False),
    ("Campus canteen", "Food", (40, 180), False),
    ("Chai point", "Food", (20, 90), False),
    ("McDonalds", "Food", (150, 450), False),
    ("Blinkit - milk & bread", "Food", (60, 350), False),
    ("Local bakery", "Food", (50, 300), False),
    # Transport
    ("Uber ride", "Transport", (90, 650), False),
    ("Ola auto", "Transport", (40, 250), False),
    ("Rapido bike taxi", "Transport", (30, 160), False),
    ("Namma Metro card recharge", "Transport", (200, 500), False),
    ("HP Petrol pump", "Transport", (300, 1500), False),
    ("IRCTC train ticket", "Transport", (250, 2200), False),
    ("BMTC bus pass", "Transport", (800, 1200), False),
    ("Indigo flight booking", "Transport", (3500, 8000), False),
    # Shopping
    ("Myntra order", "Shopping", (500, 3000), False),
    ("Flipkart - headphones", "Shopping", (800, 4000), False),
    ("Decathlon", "Shopping", (400, 3500), False),
    ("H&M store", "Shopping", (700, 3200), False),
    ("Croma electronics", "Shopping", (1000, 9000), False),
    ("Nykaa beauty", "Shopping", (300, 1500), False),
    ("IKEA", "Shopping", (500, 5000), False),
    # Bills
    ("BESCOM electricity bill", "Bills", (600, 2200), False),
    ("Airtel postpaid", "Bills", (399, 999), False),
    ("Jio recharge", "Bills", (239, 719), False),
    ("ACT Fibernet broadband", "Bills", (700, 1200), False),
    ("Monthly rent transfer", "Bills", (8000, 15000), False),
    ("Water bill BWSSB", "Bills", (150, 500), False),
    ("LPG cylinder Indane", "Bills", (850, 1100), False),
    # Entertainment
    ("Netflix subscription", "Entertainment", (199, 649), False),
    ("Spotify Premium", "Entertainment", (119, 179), False),
    ("BookMyShow movie tickets", "Entertainment", (250, 900), False),
    ("PVR cinemas", "Entertainment", (200, 800), False),
    ("Steam game purchase", "Entertainment", (300, 2500), False),
    ("Bowling at Smaaash", "Entertainment", (400, 1200), False),
    ("Concert ticket Insider", "Entertainment", (800, 3500), False),
    # Health
    ("Apollo Pharmacy", "Health", (120, 1200), False),
    ("Cult.fit membership", "Health", (999, 2500), False),
    ("Practo doctor consult", "Health", (300, 800), False),
    ("1mg medicines", "Health", (150, 900), False),
    ("Dental clinic", "Health", (500, 3000), False),
    # Education
    ("Coursera subscription", "Education", (2000, 4000), False),
    ("Udemy course", "Education", (399, 799), False),
    ("Sapna Book House", "Education", (300, 1500), False),
    ("University exam fee", "Education", (1000, 3000), False),
    ("Stationery store", "Education", (50, 400), False),
    ("Library fine", "Education", (20, 150), False),
    # Other
    ("ATM cash withdrawal", "Other", (500, 3000), False),
    ("Birthday gift for friend", "Other", (300, 1500), False),
    ("Donation to NGO", "Other", (200, 2000), False),
    ("Laundry service", "Other", (100, 400), False),
    ("Haircut at salon", "Other", (150, 600), False),
    # Deliberately ambiguous descriptions (labelled carefully by the team)
    ("Amazon", "Shopping", (200, 3000), True),
    ("Amazon Fresh", "Food", (300, 1800), True),
    ("Amazon Prime renewal", "Entertainment", (299, 1499), True),
    ("UPI transfer to Rahul", "Other", (100, 2000), True),
    ("Paytm payment", "Other", (50, 800), True),
    ("Google Play", "Entertainment", (99, 999), True),
    ("Apple.com/bill", "Entertainment", (99, 399), True),
    ("Reliance", "Shopping", (200, 2500), True),
    ("Tata 1mg", "Health", (150, 900), True),
    ("Uber Eats", "Food", (150, 600), True),
    ("POS 4411 MUMBAI", "Other", (100, 2500), True),
    ("Gym + protein shake", "Health", (200, 900), True),
]

RESTAURANTS = ["Meghana Foods", "Truffles", "Empire", "Third Wave", "Leon Grill", "Vidyarthi Bhavan"]
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]


def _desc(template: str, rng: random.Random) -> str:
    return template.format(n=rng.randint(1000, 9999), r=rng.choice(RESTAURANTS))


def make_labelled(rng: random.Random) -> list[dict]:
    rows = []
    start = date(2026, 8, 1)
    # Each merchant appears 2-4 times with varied wording -> ~200 rows
    for template, cat, (lo, hi), amb in MERCHANTS:
        for _ in range(rng.choice([2, 3, 3, 4])):
            d = start + timedelta(days=rng.randint(0, 91))
            desc = _desc(template, rng)
            # light noise like real bank exports
            if rng.random() < 0.25:
                desc = desc.upper()
            if rng.random() < 0.15:
                desc = f"UPI/{rng.randint(100000, 999999)}/{desc}"
            rows.append({
                "date": d.isoformat(),
                "description": desc,
                "amount": round(rng.uniform(lo, hi), 2),
                "category": cat,
                "ambiguous": int(amb),
            })
    rng.shuffle(rows)
    # Stratified 70/30 dev/test split
    by_cat: dict[str, list[dict]] = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r)
    for items in by_cat.values():
        cut = round(len(items) * 0.7)
        for i, r in enumerate(items):
            r["split"] = "dev" if i < cut else "test"
    for i, r in enumerate(rows, 1):
        r["id"] = f"T{i:03d}"
    return rows


def make_sample(rng: random.Random) -> list[dict]:
    """3 months (Aug-Oct 2026) of a student's expenses for the demo, unlabelled."""
    rows = []
    recurring = [
        ("Monthly rent transfer", 12000, 1), ("ACT Fibernet broadband", 999, 5),
        ("Airtel postpaid", 599, 7), ("BESCOM electricity bill", None, 10),
        ("Netflix subscription", 499, 12), ("Spotify Premium", 119, 15),
        ("Cult.fit membership", 1499, 3), ("BMTC bus pass", 1050, 2),
    ]
    variable = [m for m in MERCHANTS if m[0] not in {r[0] for r in recurring} and m[2][1] <= 4000
                and m[0] != "Monthly rent transfer"]
    weights = {"Food": 9, "Transport": 5, "Shopping": 2, "Entertainment": 2, "Health": 1,
               "Education": 1, "Other": 1, "Bills": 0.3}
    for month in (8, 9, 10):
        for desc, amt, day in recurring:
            rows.append({"date": date(2026, month, day).isoformat(), "description": desc,
                         "amount": amt if amt else round(rng.uniform(900, 1900), 2)})
        n = {8: 44, 9: 47, 10: 52}[month]   # spending creeps up -> interesting insight
        for _ in range(n):
            m = rng.choices(variable, weights=[weights[v[1]] for v in variable])[0]
            lo, hi = m[2]
            amt = rng.uniform(lo, hi) * (1.15 if month == 10 and m[1] == "Food" else 1)
            rows.append({"date": date(2026, month, rng.randint(1, 30 if month != 8 else 31)).isoformat(),
                         "description": _desc(m[0], rng), "amount": round(amt, 2)})
    rows.append({"date": "2026-10-24", "description": "IRCTC train ticket - trip home", "amount": 1840.0})
    rows.sort(key=lambda r: r["date"])
    return rows


def write(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    rng = random.Random(SEED)
    labelled = make_labelled(rng)
    write(HERE / "labelled_transactions.csv", labelled,
          ["id", "date", "description", "amount", "category", "ambiguous", "split"])
    sample = make_sample(random.Random(33))   # seed chosen for a smooth Aug < Sep < Oct trend
    write(HERE / "sample_expenses.csv", sample, ["date", "description", "amount"])
    dev = sum(r["split"] == "dev" for r in labelled)
    print(f"labelled: {len(labelled)} rows (dev={dev}, test={len(labelled) - dev}); sample: {len(sample)} rows")
