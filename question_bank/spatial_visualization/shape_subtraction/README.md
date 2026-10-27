# Spatial Visualization → Shape Subtraction

150 items: 5 grades (K–4) × 5 base questions (one per attribute) ×
(1 original + 5 palette variations).

The inverse of Shape Combination: the question shows a combined
(overlaid) figure of 2 or 3 pieces, shows ONE of those pieces being
taken away, and asks what remains. Reuses the same `Piece` /
combo-overlay drawing building blocks as Shape Combination.

- `two_minus_shape` — 2 pieces, subtract one → a single shape remains (easiest)
- `two_minus_color` — 2 pieces (color varies), subtract one → single shape remains
- `two_minus_size` — 2 pieces (size varies), subtract one → single shape remains
- `three_minus_mid` — 3 pieces, subtract the middle layer → 2 pieces remain
- `three_minus_edge` — 3 pieces, subtract the front (last) layer → 2 pieces remain (hardest)

Distractors are the on-point mistakes: subtracting the wrong piece
(leaves a different, also-plausible remainder), forgetting to subtract
at all (the full original combo), the correct remaining pieces but with
one shifted to the wrong shape, and a fully unrelated combo — plus a
bounded shape-cycle fallback so distractor generation always
terminates.

Validated programmatically across all 150 specs: every spec produces
the correct starting piece count, the remaining set is always exactly
one piece shorter than the start, all 5 choices are unique, and the
correct remainder is always present at the claimed letter.
Spot-rendered and visually confirmed (grade 3, `three_minus_mid`):
circle+triangle+star minus the middle piece (triangle) correctly
leaves circle+star, with distractors showing exactly "forgot to
subtract" (still has all 3) and "subtracted the wrong piece" (left
circle+triangle instead).

## Regenerating

```bash
cd question_bank/spatial_visualization/shape_subtraction
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/shape_subtraction
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
