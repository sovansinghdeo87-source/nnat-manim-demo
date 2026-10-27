# Reasoning by Analogy → Combined Transformations

150 items: 5 grades (K–4) × 5 base questions (one per dimension pair)
× (1 original + 5 palette variations).

The hardest Analogy subskill: **two rules apply simultaneously** —
e.g. the arrow both rotates AND changes color at once. Two-pair
analogy format: first pair (A → B) demonstrates both rules; apply both
to a second pair's starting figure (C → ?). A and C start at different
combined states so the question can't be answered by copying B.

Five dimension pairs (each combining two of four transform
dimensions): `rotate_color`, `rotate_size`, `rotate_fill`,
`color_size`, `size_fill`. When `rotate` is active the marker is an
**arrow** (so rotation is always visible, same reasoning as the plain
Rotation subskill); otherwise it's a plain circle.

Distractors specifically target **partial-rule application** — the
classic combined-transformation mistake:

- copying C (neither rule applied)
- copying B (right figure's transform, wrong starting point)
- applying only the **first** rule, not the second
- applying only the **second** rule, not the first

**Bug caught during validation**: `_apply_delta`'s rotate case didn't
wrap the angle mod 360. Two tokens at, say, 90° and 450° are visually
identical but would compare as *different* by exact field equality —
risking two choices that look the same on screen without being
deduplicated. Fixed by wrapping every rotation delta mod 360.

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/combined_transformations
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
