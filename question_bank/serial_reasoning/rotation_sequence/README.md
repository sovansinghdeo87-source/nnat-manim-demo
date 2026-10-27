# Serial Reasoning → Rotation Sequence

150 items: 5 grades (K–4) × 5 base questions (one per increment)
× (1 original + 5 palette variations).

Reuses the "row of boxed cells" format (see Row Sequences), but unlike
Row Sequences (where rotation is just one of five attributes), each of
the five base questions here **is** a rotation increment — the same
five increments as Pattern Completion's Rotation subskill (`half_turn`
180°, `third_turn` 120°, `quarter_turn` 90°, `sixth_turn` 60°,
`eighth_turn` 45°), now shown in boxed-row form instead of an
arrow-chained sequence. An arrow marker is used because it has no
rotational symmetry, so every increment stays visible.

Blank position varies by grade (first/middle/last), same convention
as Row Sequences and Shape Progression.

Verified against a hand-traced example: `eighth_turn` (45°) with the
blank in the middle (0° → ? → 90°) correctly resolves to 45°
(up-right diagonal) — genuinely interpolating, not guessing.

## Regenerating

```bash
cd question_bank/serial_reasoning/rotation_sequence
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
