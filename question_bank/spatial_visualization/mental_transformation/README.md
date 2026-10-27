# Spatial Visualization → Mental Transformation

150 items: 5 grades (K–4) × 5 base questions (one per step combination) ×
(1 original + 5 palette variations).

Reuses the same asymmetric triangle+dot shape as Spatial
Visualization's Rotation/Reflection subskills, but now **two**
operations — always one rotation + one reflection, in a stated order —
are applied in sequence: "first do X, then do Y — what does the shape
look like?"

- `rotate_then_flip_v` — rotate 90°, then mirror across vertical
- `flip_then_rotate_v` — mirror across vertical, then rotate 90°
- `rotate_then_flip_h` — rotate 135°, then mirror across horizontal
- `flip_then_rotate_h` — mirror across horizontal, then rotate 135°
- `rotate_then_flip_diag` — rotate 60°, then mirror across the ↗ diagonal (hardest)

The headline distractor is applying the two steps in the **reverse**
order. This is mathematically guaranteed to differ from the correct
answer, not just incidentally different: composing a rotation with a
reflection is non-commutative whenever the rotation angle isn't a
multiple of 180° — rotate-then-reflect and reflect-then-rotate land on
reflections about genuinely different axes. Every attribute pairs a
rotation with a reflection (never two rotations, since pure rotations
commute and order would stop mattering), so this distractor is always
a real, distinct image. Other distractors: only the first step applied
(forgot the second), only the second step applied (forgot the first),
and the correct steps with the rotation angle off by 40° — plus a
bounded angle-bump fallback so distractor generation always
terminates.

Validated two ways across all 150 specs: structurally (all 5 choices
unique, correct answer present at the claimed letter) AND
geometrically — every choice's actual transformed triangle vertices
were computed independently in NumPy and confirmed to differ from the
correct answer's vertices as point sets (not just differently
labeled). Spot-rendered and visually confirmed (grade 4,
`rotate_then_flip_diag`): all 5 choices render as clearly
distinguishable orientations.

## Regenerating

```bash
cd question_bank/spatial_visualization/mental_transformation
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/mental_transformation
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
