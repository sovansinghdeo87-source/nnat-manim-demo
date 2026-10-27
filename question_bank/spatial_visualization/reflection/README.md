# Spatial Visualization → Reflection

150 items: 5 grades (K–4) × 5 base questions (one per reflection axis) ×
(1 original + 5 palette variations).

Reuses the same intentionally asymmetric compound shape as Spatial
Visualization's Rotation subskill (a right triangle with a dot marking
one corner, so it has no rotational or reflective symmetry), but the
task is genuine mirror reflection across one of four axis directions
instead of rotation.

- `flip_vertical` — mirror across a vertical (up-and-down) line
- `flip_horizontal` — mirror across a horizontal (side-to-side) line
- `flip_diag_up` — mirror across the ↗ diagonal
- `flip_diag_down` — mirror across the ↘ diagonal
- `flip_vertical_offset` — vertical mirror again, but the shown shape
  starts at a deliberately off-axis angle (hardest — nothing lines up
  with the frame to anchor intuition)

The headline distractor is the mirror-image counterpart of the
Rotation subskill's mistake: a plain rotated copy (no reflection at
all) looks deceptively similar but is never reachable by mirroring.
Other distractors: the unreflected shape as shown (forgot to reflect
at all), reflecting across the wrong axis, and an unrelated
angle+axis combination — plus a bounded 15°-step/axis-cycling fallback
so distractor generation always terminates.

Validated programmatically across all 150 specs: all 5 choices unique,
correct answer present at the claimed letter, the correct answer is
always actually reflected (never equal to the unreflected shown
shape), and the shown/correct pair is never accidentally identical.
Spot-rendered and visually confirmed (grade 4, `flip_diag_up`): clean,
clearly distinguishable choices with the corner dot legible throughout.

## Regenerating

```bash
cd question_bank/spatial_visualization/reflection
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/reflection
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
