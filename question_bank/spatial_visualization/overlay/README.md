# Spatial Visualization → Overlay

150 items: 5 grades (K–4) × 5 base questions (one per attribute) ×
(1 original + 5 palette variations).

Complementary to Shape Combination/Shape Subtraction: the question
shows the **final** overlaid picture of 2 or 3 pieces (back to front,
each layer slightly smaller and shifted) and asks which single piece
is on the bottom — partially hidden behind the others. A genuine
depth/occlusion visualization skill, the mirror image of Pattern
Completion's Overlapping Shapes (which asks "who's on top"). Answer
choices are single shapes, not combos, since the student must isolate
one specific layer out of the merged picture.

- `two_back_shape` — 2 pieces, only shape identity varies (easiest)
- `two_back_color` — 2 pieces, same shape, only color varies
- `two_back_size` — 2 pieces, same shape, only relative size varies
- `three_back` — 3 pieces, shape varies
- `three_back_combo` — 3 pieces, shape AND color both vary (hardest)

Distractors are the on-point mistakes: any of the other (non-back)
pieces in the stack (classic "confused a front piece for the back
one"), a shape-shifted variant of the correct piece, and an unrelated
shape — plus a bounded shape-cycle fallback so distractor generation
always terminates.

Validated programmatically across all 150 specs: every spec produces
the correct piece count, all 5 choices are unique, and the true back
piece is always present at the claimed letter. Spot-rendered and
visually confirmed (grade 4, `three_back_combo`): red circle (back) +
purple triangle + pink star (front) correctly resolves to the red
circle as the answer.

## Regenerating

```bash
cd question_bank/spatial_visualization/overlay
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/overlay
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
