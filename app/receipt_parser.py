import re

IGNORE_PATTERNS = [
    r"subtotal", r"tax", r"total", r"balance", r"tender", r"change",
    r"visa", r"mastercard", r"debit", r"credit", r"auth", r"approval",
    r"cashier", r"store", r"receipt", r"thank", r"refund",
]

ignore_re = re.compile("|".join(IGNORE_PATTERNS), re.IGNORECASE)

price_re = re.compile(r"\b\d+\.\d{2}\b")

def parse_receipt_text(raw: str):
    """
    Very simple parser:
    - split lines
    - ignore obvious non-item lines
    - if a line has a price, treat left side as item name
    - default quantity = 1
    """
    items = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if ignore_re.search(s):
            continue

        # looks like an item line if it includes a price
        if price_re.search(s):
            # remove price(s) and trailing junk
            name = price_re.sub("", s).strip(" -\t")
            name = re.sub(r"\s{2,}", " ", name).strip()

            # ignore very short noise
            if len(name) < 2:
                continue

            items.append({"name": name, "quantity": 1})

    # merge duplicates (same name)
    merged = {}
    for it in items:
        key = it["name"].lower()
        merged.setdefault(key, {"name": it["name"], "quantity": 0})
        merged[key]["quantity"] += it["quantity"]

    return list(merged.values())
