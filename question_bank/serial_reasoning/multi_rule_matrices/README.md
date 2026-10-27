# Serial Reasoning → Multi-Rule Matrices

150 items: 5 grades (K–4) × 5 base questions (one per attribute triple) ×
(1 original + 5 palette variations).

The capstone of the matrix family: **three** independent rules apply to
every cell of a 3×3 grid at once — one attribute keyed to the row, a
second keyed to the column (the familiar 2×2/3×3 Matrices idea), AND a
third attribute — always fill (empty/filled) — keyed to
`(row + col) % 2`, layered on top of both. Getting the blank cell right
requires tracking all three rules simultaneously, not just a row/column
pair.

- `shape_color_fill` — row=shape, column=color, fill=parity
- `shape_size_fill` — row=shape, column=size, fill=parity
- `color_size_fill` — row=color, column=size, fill=parity
- `shape_color_fill_rev` — same as the first but row/column roles swapped
- `shape_size_fill_rev` — same as the second but row/column roles swapped

Distractors are the natural "got 2 of 3 rules right" mistakes: the
whole cell copied from the wrong row, the whole cell copied from the
wrong column, the right shape/color/size but the fill rule ignored, and
one cell wrong on both row and column — plus a bounded shape-cycle
fallback so distractor generation always terminates.

Validated programmatically across all 150 specs: every row's row-rule
attribute is constant across that row, every column's column-rule
attribute is constant across that column, the fill parity rule holds
at all 9 cells, all 5 choices are unique, and the correct answer is
always present at the claimed letter. Spot-rendered and visually
confirmed: a `shape_color_fill` grid (grade 4) resolves its blank cell
(row 1, col 1) to a filled orange square, matching the row's shape
(square), the column's color (orange), and the fill-parity rule
(`(1+1)%2==0` → filled) all at once.

## Regenerating

```bash
cd question_bank/serial_reasoning/multi_rule_matrices
python generate_bank.py
```

## Rendering

```bash
cd question_bank/serial_reasoning/multi_rule_matrices
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
