# Serial Reasoning → Distribution Rules

150 items: 5 grades (K–4) × 5 base questions (one per attribute) ×
(1 original + 5 palette variations).

A 3×3 Latin-square constraint — genuinely different from 2×2/3×3
Matrices, where row and column each control a *different* independent
attribute. Here there is only **one** attribute with exactly 3 distinct
values, and every row **and** every column must contain all 3 values
exactly once (like a mini Sudoku):

- `shape_fwd` — `cell(r, c) = values[(r + c) % 3]`
- `color_fwd` — same cyclic rule, on color
- `size_fwd` — same cyclic rule, on size
- `combo_fwd` — same cyclic rule, on shape+color combined
- `shape_rev` — `cell(r, c) = values[(r - c) % 3]` (opposite diagonal
  direction, for variety)

One cell is left blank (position varies by grade — see
`BLANK_BY_GRADE`). Distractors: the two *other* values in the triple
(guaranteed to create a genuine row-or-column conflict if placed at the
blank — exactly the mistake this subskill targets), plus unrelated
fillers from `SHAPE_CYCLE`/`COLOR_CYCLE` capped so the search always
terminates.

## Regenerating

```bash
cd question_bank/serial_reasoning/distribution_rules
python generate_bank.py
```

## Rendering

```bash
cd question_bank/serial_reasoning/distribution_rules
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
