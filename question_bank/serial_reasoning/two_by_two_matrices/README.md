# Serial Reasoning → 2×2 Matrices

150 items: 5 grades (K–4) × 5 base questions (one per dimension pair)
× (1 original + 5 palette variations).

A genuinely two-dimensional rule, distinct from the Reasoning by
Analogy format: the **row** index determines one attribute's value,
the **column** index determines a *different* attribute's value, and
each cell is the combination of both. The student must identify both
the row pattern and the column pattern independently, then combine
them for the missing cell — not just copy a single transformation.

Five dimension pairs: `shape_color`, `shape_size`, `color_size`,
`shape_fill`, `size_fill`.

Blank cell position (`BLANK_BY_GRADE`): K/1/3 ask for **bottom-right**
(the standard, most intuitive NNAT matrix convention); grade 2 asks
for top-right; grade 4 asks for **top-left** (hardest — both the row
and column values must be inferred from cells that aren't directly
adjacent in the usual reading order).

Distractors: right row, wrong column (and vice versa) — the classic
matrix mistake of satisfying only one axis — plus copies of the other
visible cells.

Verified against hand-traced examples at both the easiest
(bottom-right blank: teal square, combining row-shape=square with
column-color=teal) and hardest (top-left blank: purple circle) cases.

## Regenerating

```bash
cd question_bank/serial_reasoning/two_by_two_matrices
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
