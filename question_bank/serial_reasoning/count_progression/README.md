# Serial Reasoning → Count Progression

150 items: 5 grades (K–4) × 5 base questions (one per mark type)
× (1 original + 5 palette variations).

Reuses the mark-cluster growth model from Pattern Completion's
Line/Shape Continuation (a cluster of N identical marks, N growing by
a constant step), but in the "row of boxed cells" format with only 3
cells shown and the blank position varying by grade — not always
asking for the next count in line.

Five mark types: `dot`, `square`, `triangle`, `star`, `hexagon`. Step
size also scales with grade (1 for K–2, 2 for grades 3–4).

Verified against a hand-traced example: 1 star → ? → 5 stars (blank in
the middle, step 2) correctly resolves to 3 stars.

## Regenerating

```bash
cd question_bank/serial_reasoning/count_progression
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
