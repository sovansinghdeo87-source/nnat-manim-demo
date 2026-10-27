# Serial Reasoning → Shape Progression

150 items: 5 grades (K–4) × 5 base questions (one per step amount)
× (1 original + 5 palette variations).

Deliberately distinct from Row Sequences' `shape_shift` (which cycles
through an arbitrary list of unrelated shapes): this is a genuine
**monotonic progression** — a regular polygon gaining or losing sides
each step (triangle → diamond → pentagon → ...), 3 to 10 sides. Same
"growth" idea as Pattern Completion's Line/Shape Continuation, applied
to polygon complexity instead of mark count.

Reuses Row Sequences' "row of boxed cells" format and blank-position-
varies-by-grade convention (`BLANK_POS_BY_GRADE`).

Five step amounts: `grow_1`, `grow_2`, `grow_3`, `shrink_1`,
`shrink_2`. Starting side-counts are drawn from a pool constrained so
every cell in the row stays within 3–10 sides (verified programmatically
across all 150 specs).

Verified against hand-traced examples: `grow_1` (triangle→diamond→?)
correctly resolves to a pentagon; `grow_3` with the blank in the
middle (triangle→?→nonagon) correctly resolves to a hexagon.

## Regenerating

```bash
cd question_bank/serial_reasoning/shape_progression
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
