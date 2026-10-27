# Spatial Visualization → Shape Combination

150 items: 5 grades (K–4) × 5 base questions (one per attribute) ×
(1 original + 5 palette variations).

The first Spatial Visualization engine — a genuinely different format
from Pattern Completion / Reasoning by Analogy / Serial Reasoning:
there is no sequence and no blank cell in a grid. Instead the question
shows 2 or 3 separate shape **pieces** side by side (joined by "+"
signs) and asks what they combine into. The 5 answer choices each show
a combined (overlaid) figure; only one is the literal overlay of
exactly those pieces with their exact shape/color/size.

- `two_shapes` — 2 pieces, only shape identity varies (easiest)
- `two_colors` — 2 pieces, same shape, only color varies
- `shape_and_size` — 2 pieces, same shape, only relative size varies
- `three_pieces` — 3 pieces layered back-to-front (shape + color vary)
- `combo_full` — 2 pieces, shape AND color AND size all vary (hardest)

Distractors are the on-point mistakes: the first piece swapped for a
different one, the last piece swapped, the two pieces' front/back order
swapped (classic "which was on top" confusion), and a fully unrelated
combination — plus a bounded shape-cycle fallback so distractor
generation always terminates.

Validated programmatically across all 150 specs: every spec produces
the correct piece count for its attribute, all 5 choices are unique,
and the correct combination is always present at the claimed letter.
Spot-rendered and visually confirmed for both the 2-piece case (grade
K: blue circle + orange triangle → the overlay with blue circle behind,
orange triangle in front and shifted) and the 3-piece case (grade 4:
red circle + purple triangle + pink star → all three correctly layered
back-to-front, readable and distinguishable).

## Regenerating

```bash
cd question_bank/spatial_visualization/shape_combination
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/shape_combination
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
