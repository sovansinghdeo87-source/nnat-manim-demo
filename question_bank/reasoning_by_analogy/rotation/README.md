# Reasoning by Analogy → Rotation

150 items: 5 grades (K–4) × 5 base questions (one per rotation
increment) × (1 original + 5 palette variations).

Establishes the **"two-pair analogy" format** used across all
Reasoning by Analogy subskills: a first pair (A → B) demonstrates a
transformation rule; the student applies the *same rule* to a second
pair's starting figure (C → ?) and picks the result from 5 choices.
This differs from Pattern Completion's single-sequence format — two
independent pairs, not one linear chain.

For Rotation: A and C are the **same arrow marker at two different
starting angles** (never the same angle — otherwise the question could
be answered by just copying B, without actually applying the rule).
Reuses the asymmetric-arrow-marker reasoning from Pattern Completion's
Rotation subskill (an arrow has no rotational symmetry, so every
increment stays visually distinguishable). Five increments, easiest to
hardest: `half_turn` (180°), `third_turn` (120°), `quarter_turn` (90°),
`sixth_turn` (60°), `eighth_turn` (45°).

Distractors: rotating the **wrong direction**, **copying B** instead of
transforming C (a classic analogy mistake — right transformation, wrong
figure), not rotating at all, and overshooting by an extra increment.

Validated programmatically that `angle_a != angle_c` for every one of
the 150 specs (otherwise the question would have an unintended
shortcut answer), plus the usual choice-uniqueness sweep.

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/rotation
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
