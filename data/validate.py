#!/usr/bin/env python3
"""Validate the workout database. Run: python3 data/validate.py"""
import json, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
errors, warnings = [], []

ex_doc = json.load(open(os.path.join(HERE, "exercises.json")))
exercises = ex_doc["exercises"]
patterns = set(ex_doc["patterns"])

# id uniqueness, alias uniqueness, pattern validity, variant targets
ids, alias_map = set(), {}
for e in exercises:
    if e["id"] in ids:
        errors.append("duplicate id: " + e["id"])
    ids.add(e["id"])
    if e["pattern"] not in patterns:
        errors.append("%s: unknown pattern %r" % (e["id"], e["pattern"]))
    for a in [e["id"]] + e["aliases"]:
        if a in alias_map and alias_map[a] != e["id"]:
            errors.append("alias %r maps to both %s and %s" % (a, alias_map[a], e["id"]))
        alias_map[a] = e["id"]
    if e.get("needsReview"):
        warnings.append("%s needs review: %s" % (e["id"], e.get("reviewNote", "")))

for e in exercises:
    v = e.get("variantOf")
    if v and v not in ids:
        errors.append("%s: variantOf points at unknown id %r" % (e["id"], v))

# sessions resolve against the library, and declared totals match reality
s_doc = json.load(open(os.path.join(HERE, "sessions.json")))
entries = 0
for s in s_doc["sessions"]:
    seen = set()
    for b in s["blocks"]:
        for en in b["entries"]:
            entries += 1
            if en["exercise"] not in alias_map:
                errors.append("%s: unknown exercise %r" % (s["date"], en["exercise"]))
            key = (b["name"], en["exercise"])
            if key in seen:
                warnings.append("%s: %s listed twice in %s" % (s["date"], en["exercise"], b["name"]))
            seen.add(key)
            if en.get("weight") is not None and not en.get("unit"):
                errors.append("%s: %s has weight but no unit" % (s["date"], en["exercise"]))
    for x in s.get("notRun", []):
        if x not in alias_map:
            errors.append("%s: notRun has unknown exercise %r" % (s["date"], x))
    declared = s.get("totals", {}).get("workingSets")
    actual = sum(en["sets"] for b in s["blocks"] for en in b["entries"])
    if declared is not None and declared != actual:
        errors.append("%s: totals.workingSets says %d, entries sum to %d" % (s["date"], declared, actual))

print("%d exercises, %d lookup keys, %d session entries" % (len(exercises), len(alias_map), entries))
for w in warnings:
    print("  warn: " + w)
for e in errors:
    print("  ERROR: " + e)
print("FAIL" if errors else "OK")
sys.exit(1 if errors else 0)
