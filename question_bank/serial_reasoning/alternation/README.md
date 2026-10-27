# Serial Reasoning → Alternation

150 items: 5 grades (K–4) × 5 base questions (one per attribute)
× (1 original + 5 palette variations).

Reuses the "pure ABAB" content model from Pattern Completion's
Alternating Patterns subskill (period 2, varying shape/fill/color/
size/combo), but in the "row of boxed cells" format with only 3 cells
shown and the blank position varying by grade.

Five attributes: `shape`, `fill`, `color`, `size`, `combo`.

Verified against hand-traced examples: circle→square→? (blank last)
resolves to circle; red circle→?→red circle (blank in the middle,
`color` attribute) resolves to the alternate color (orange circle) —
confirming genuine alternation reasoning, not just pattern-matching
the visible cells.

## Regenerating

```bash
cd question_bank/serial_reasoning/alternation
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
