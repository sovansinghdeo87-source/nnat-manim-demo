# Spatial Visualization → Rotation

150 items: 5 grades (K–4) × 5 base questions (one per turn amount) ×
(1 original + 5 palette variations).

A genuine mental-rotation task, distinct from Pattern Completion's
Rotation (a sequence of rotating arrows) and Reasoning by Analogy's
Rotation (A→B :: C→? transformation pairs). Here there is a single
snapshot: an intentionally asymmetric compound shape — a right
triangle with a dot marking one specific corner, so it has no
rotational or reflective symmetry — is shown in one orientation. The
student must identify which answer choice shows the *same* shape
correctly rotated by a given amount.

- `quarter_turn` — 90°
- `eighth_turn` — 45°
- `half_turn` — 180°
- `third_turn` — 120°
- `odd_turn` — 73° (deliberately not a "clean" angle — hardest)

The headline distractor is the classic rotation-vs-reflection
confusion: a mirrored version of the correct answer (same angle, but
flipped — not reachable by any rotation) looks deceptively similar but
is never the right answer. The other distractors are overshoot/
undershoot angles (±30°) and an unrelated angle (+150°), with a
bounded 15°-step fallback so distractor generation always terminates.

Validated programmatically across all 150 specs: all 5 choices unique,
correct answer present at the claimed letter, the correct answer is
never the mirrored variant, and exactly one choice is the mirrored
decoy. Spot-rendered and visually confirmed (grade 4, `odd_turn`): the
triangle+dot shape renders clearly, with a visibly distinguishable
spread of rotated and mirrored choices.

## Regenerating

```bash
cd question_bank/spatial_visualization/rotation
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/rotation
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
