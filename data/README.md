# Workout database

Two files. Both are hand-editable JSON; run the validator after touching either.

```
python3 data/validate.py
```

## `exercises.json` — the shared vocabulary

So Jared can write "clamshells" or "sa row" and it resolves to one canonical exercise.

| Field | Required | What it is |
|---|---|---|
| `id` | yes | kebab-case, stable, never reused |
| `name` | yes | how it's written out in full |
| `aliases` | yes | every string Jared might actually type. Must be globally unique |
| `pattern` | yes | one of the `patterns` list at the top of the file |
| `equipment` | no | `bodyweight`, `dumbbell`, `barbell`, `band`, `cable`, `machine`, `bench` |
| `venue` | no | `home`, `gym`, or both |
| `setup` | no | how to do it without gym equipment |
| `cue` | no | the single thing that matters for form |
| `video` | no | a form demo |
| `variantOf` | no | id of the parent movement |
| `source` | no | e.g. `PT` when it came from the physio |
| `needsReview` | no | true when the movement isn't confirmed yet — validator warns |

Adding one only needs `id`, `name`, `aliases`, `pattern`.

## `sessions.json` — what actually happened

Sessions as performed, not as planned. `planned` vs `actual` captures the gap on purpose.

Entries are `{exercise, sets, reps, weight, unit}`. `weight` is **per hand** for dumbbells, `null` for bodyweight. `notRun` lists prescribed work that didn't happen — the omissions are as informative as the reps.

## What the validator checks

Duplicate ids, alias collisions across exercises, unknown patterns, dangling `variantOf`, session exercises that don't resolve, weights without units, and declared set totals that disagree with the entries.

## How voice logging works (for a future session)

Jared logs by talking in Claude chat. Claude normalises what he says and writes it
straight into the live app. Nothing is typed into the app by hand.

**The app:** `https://claude.ai/code/artifact/4787b210-881d-44fb-b8fa-5edf4b691c7f`
Revise it by republishing that same artifact — never create a new one.

**The store:** the app declares the `db` capability and keeps all state in one
document, `progress/log`. Read and write it with the Artifact tool
(`action: "read_db"` / `"write_db"`, `collection: "progress"`, `doc_id: "log"`).
The page holds an `onSnapshot` listener, so a write lands on his phone live.

**The document replaces app state wholesale on snapshot**, so always read it
first and write the merged whole. Shape:

```jsonc
{
  "checks": {},            // "w<week>d<day><slot>" -> true, ticked planned sessions
  "days":   {},            // "w<week>d<day>" -> {mi, min, hip 0-4, feel 1-5, note}
  "lift":   {},            // "w<week><A|B|C>[h]<index>" -> {w, d}; "h" = home variant
  "ven":    {},            // session id -> "home" (absent means gym)
  "act":    {}             // "w<week>d<day>" -> a session as actually performed
}
```

An `act` entry:

```jsonc
{
  "t": ["strength","pt","core","run"],   // tags; drive the week's "done" column
  "m": 62,                                // minutes, optional
  "src": "voice",
  "note": "",
  "b": [                                  // blocks, in the order performed
    { "n": "Shoulders",
      "e": [ { "n": "Arnold press", "s": 4, "r": 12, "w": 10 } ] }  // sets, reps, lb per hand
  ]
}
```

Week 0 = the week of Sep 7 2026; day 0 = Monday. Keys use **his local date**
(Boise, UTC-6/-7), not the container's UTC clock — they differ in the evening.

**Also append the session to `sessions.json`** so the record survives outside the
artifact, then run `python3 data/validate.py`. Resolve every exercise name he says
through `exercises.json` aliases; add a new entry the first time he mentions a
movement rather than inventing an id at write time.
