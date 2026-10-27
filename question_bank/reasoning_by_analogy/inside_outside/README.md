# Reasoning by Analogy → Inside-Outside Transformation

150 items: 5 grades (K–4) × 5 base questions (one per container/direction
combo) × (1 original + 5 palette variations).

Two-pair analogy format: a fixed container shape stays constant within
a question; a small dot sits at a given angle around it, either just
outside or just inside the boundary. First pair (A → B) demonstrates
"move from outside to inside" (or the reverse); apply the same
direction to a second pair's starting dot (C → ?). A and C sit at
different angles so the question can't be answered by copying B.

Five configs: `out_to_in_circle`, `in_to_out_circle`,
`out_to_in_square`, `in_to_out_triangle`, `out_to_in_star`.

Distractors: copying C (no change), copying B (right direction, wrong
angle), moving the **wrong way** (away instead of in, or vice versa),
and landing exactly **on the edge** (ambiguously neither in nor out).

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/inside_outside
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
