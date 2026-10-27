# Reasoning by Analogy → Movement or Position Change

150 items: 5 grades (K–4) × 5 base questions (one per movement vector)
× (1 original + 5 palette variations).

Two-pair analogy format: first pair (A → B) demonstrates "move the dot
by a fixed (dcol, drow) step within a 3×3 grid, wrapping around the
edges"; apply the same movement to a second pair's starting position
(C → ?). A and C start at different grid cells so the question can't
be answered by copying B.

Five movement vectors: `right_1`, `down_1`, `diag_1`, `antidiag_1`,
`down_2`.

Distractors: copying C (no change), copying B (right movement, wrong
start), moving the **opposite direction**, and moving along the
**wrong axis** (swapped dcol/drow).

**Bug caught during validation** (same root cause as Multi-Rule
Patterns' earlier bug): the first version's distractor fallback search
only varied delta via `salt % 3` / `(salt * 2) % 3`, which cycles
through just 3 distinct deltas — if all 3 were already used, the
`while` loop could never terminate. Fixed by replacing it with a fixed,
bounded list of all 9 possible grid deltas.

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/movement_position
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
