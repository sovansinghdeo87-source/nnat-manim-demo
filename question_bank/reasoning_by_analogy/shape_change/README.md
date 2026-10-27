# Reasoning by Analogy → Shape Change

150 items: 5 grades (K–4) × 5 base questions (one per shift amount)
× (1 original + 5 palette variations).

Two-pair analogy format: first pair (A → B) demonstrates "shift N
positions forward along a fixed shape cycle" (circle → square →
triangle → diamond → star → hexagon → back to circle); apply the same
shift to a second pair's starting shape (C → ?).

A fixed **cycle** is used deliberately instead of one hardcoded pair
substitution (e.g. "circle always becomes square") — a literal fixed
pair would force A and C to both be circles for the rule to even
apply, breaking the "A and C must differ" guard against copy-shortcuts.
Shifting along a shared cycle lets A and C be different shapes while
testing the same abstract rule — consistent with how Rotation (shift
angle) and Size Change (shift size level) are modeled.

Distractors: copying C (no change), copying B (right transformation,
wrong figure), shifting the **wrong direction** (backward instead of
forward), and shifting by the **wrong amount**.

Verified against hand-computed examples: shift_1 on a diamond
(index 3) correctly lands on star (index 4); shift_5 on a diamond
correctly wraps around to triangle (index (3+5) mod 6 = 2).

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/shape_change
python generate_bank.py
```

## Rendering

Pick any entry's `question_id` out of one of the files in `questions/`, then render it by
setting `QUESTION_ID` (same code every time -- only the parameters change):

```bash
cd <this subskill dir>
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.
