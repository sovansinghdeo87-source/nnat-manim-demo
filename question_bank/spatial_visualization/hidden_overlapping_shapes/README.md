# Spatial Visualization → Hidden/Overlapping Shapes

150 items: 5 grades (K–4) × 5 base questions (one per piece count/variety) ×
(1 original + 5 palette variations).

2 or 3 shapes are drawn **outline-only** (no fill) at scattered,
overlapping positions, so their boundaries interweave into one
cluttered line figure — genuine figure-ground segregation, distinct
from the Overlay subskill (which stacks *filled* pieces concentrically
and asks about depth/z-order, not about tracing a shape out of line
clutter). The question asks which single shape is actually hidden in
the figure.

- `two_hidden_shape` — 2 pieces, only shape identity varies (easiest)
- `two_hidden_color` — 2 pieces, same shape, only color varies
- `three_hidden` — 3 pieces, shape varies
- `three_hidden_combo` — 3 pieces, shape AND color both vary
- `three_hidden_hard` — same as above, with a wider positional spread
  (more visual clutter — hardest)

**Critical correctness invariant**: every distractor must be a
(shape, color) combination that is **not** any of the pieces actually
in the figure — otherwise the question would have more than one
"correct" answer. Distractors are built by explicitly excluding every
shape and color already used (not just the literal target piece):
same shape as the target but a guaranteed-unused color, same color but
a guaranteed-unused shape, and two fully unrelated combinations — plus
a bounded cycling fallback so distractor generation always terminates.

Validated programmatically across all 150 specs with the ambiguity
check as the headline test: every single distractor was confirmed to
**not** coincide with any of the actual figure pieces (which would
silently create a second valid answer), in addition to the standard
checks (correct piece — always the first figure piece — present at the
claimed letter, all 5 choices unique). Spot-rendered and visually
confirmed (grade 4, `three_hidden_hard`): a circle/triangle/star
outline cluster where only the matching-color circle choice
corresponds to an actual figure piece, and every other choice uses a
shape or color that never appears in the figure.

## Regenerating

```bash
cd question_bank/spatial_visualization/hidden_overlapping_shapes
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/hidden_overlapping_shapes
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
