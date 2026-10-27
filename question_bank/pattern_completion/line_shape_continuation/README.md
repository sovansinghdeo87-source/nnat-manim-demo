# Pattern Completion → Line and Shape Continuation

150 items: 5 grades (K–4) × 5 base questions (one per mark type: dot,
tick, square, triangle, star) × (1 original + 5 palette variations).

A counting/quantity-growth task: each sequence item is a small cluster
of N identical marks, and N grows by a constant step every position
(e.g. 1, 2, 3, 4 → ?). Mark type is fixed within a question — only the
count varies — so distractors are about count, not shape:

- **overshoot** — one step too far
- **undershoot** — repeats the last shown count ("didn't grow")
- **wrong step** — grew by a different increment than the real pattern
- a 4th near-miss (grades 3–4) or a clearly-wrong far-away count (K–2)

Clusters are laid out in a capped-width grid (`arrange_in_grid`, max 4
columns) so even the hardest case (grade 4, up to ~13 marks) stays
legible and within frame — verified by rendering the actual worst-case
spec (highest count across all 150 items), not just a typical one.

## Regenerating

```bash
cd question_bank/pattern_completion/line_shape_continuation
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
