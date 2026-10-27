# Pattern Completion → Rotation

150 items: 5 grades (K–4) × 5 base questions (one per rotation
increment) × (1 original + 5 palette variations).

A directional arrow rotates by a constant angle every step (e.g. 0°,
90°, 180°, 270° → ?). An **arrow** is used specifically because it has
no rotational symmetry — an equilateral triangle maps onto itself every
120°, which would make a 120°-increment pattern invisible. Five
increments, easiest to hardest:

- `half_turn` — 180° (period 2)
- `third_turn` — 120° (period 3)
- `quarter_turn` — 90° (period 4)
- `sixth_turn` — 60° (period 6)
- `eighth_turn` — 45° (period 8)

Distractors: one-step-too-far (overshoot), rotating the **wrong
direction** (classic rotation-question mistake), an extra overshoot or
a 180°-flipped decoy, and "didn't rotate" (repeats the last shown
angle).

## Regenerating

```bash
cd question_bank/pattern_completion/rotation
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
