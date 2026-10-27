# Serial Reasoning → Addition/Subtraction of Elements

150 items: 5 grades (K–4) × 5 base questions (one per base shape)
× (1 original + 5 palette variations).

Deliberately distinct from Count Progression (a bare cluster of N
identical marks): here a **fixed base shape** sits at the center of
each cell, with a growing or shrinking number of small decorator dots
attached around it at fixed clock-position slots. The base shape never
changes within a question — only the number of attached dots does —
so the student is counting *added elements on a figure*, not just
cluster size.

Five base shapes: `circle`, `square`, `triangle`, `diamond`, `star`.
Step direction varies by grade — most grades add a dot each step;
grade 3 removes one each step (`STEP_BY_GRADE`), so the subskill tests
both directions.

Verified against hand-traced examples: 0→1→? dots on a circle
correctly resolves to 2; 2→1→? dots on a triangle (subtraction
direction) correctly resolves to 0.

## Regenerating

```bash
cd question_bank/serial_reasoning/addition_subtraction
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
