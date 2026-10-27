# Serial Reasoning → 3×3 Matrices

150 items: 5 grades (K–4) × 5 base questions (one per dimension pair)
× (1 original + 5 palette variations).

Same two-dimensional idea as 2×2 Matrices, scaled up: the row index
determines one attribute's value, the column index determines a
different attribute's value — now with 3 distinct values per
dimension instead of 2.

`fill` is deliberately excluded (unlike 2×2 Matrices): it's binary, so
a 3-row/3-column grid would repeat the same fill state twice per axis
— a weaker rule than shape/color/size, which each comfortably support
3+ distinct values. Five dimension pairs, including both row/column
orderings for variety: `shape_color`, `color_shape`, `shape_size`,
`size_shape`, `color_size`.

Blank cell position (`BLANK_BY_GRADE`, row-major 0–8): K/1 ask for
bottom-right (standard); grades 2/3 ask for bottom-left / top-right;
grade 4 asks for the **center** cell — the hardest position, since it
has no direct same-row/same-column "obvious copy" neighbor to lean on
Incorrectly.

Verified against hand-traced examples at both bottom-right-blank
(pink triangle: row=triangle, column=pink) and center-blank (teal
square: row=square, column=teal).

## Regenerating

```bash
cd question_bank/serial_reasoning/three_by_three_matrices
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
