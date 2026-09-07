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
