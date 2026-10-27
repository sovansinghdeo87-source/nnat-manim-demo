# Spatial Visualization → Multiple Spatial Operations

150 items: 5 grades (K–4) × 5 base questions (one per attribute) ×
(1 original + 5 palette variations).

The capstone of the Spatial Visualization area: combines Shape
Combination's "add a piece" and Shape Subtraction's "remove a piece"
into one explicit two-step pipeline applied to three pieces (A, B, C):

> start with (A, B) → then ADD C → then REMOVE A → what remains?

Correct answer: **(B, C)**.

- `shape_ops` — shape identity varies across A/B/C (easiest)
- `color_ops` — color varies
- `size_ops` — relative size varies
- `combo_ops` — shape AND color both vary
- `combo_ops_hard` — shape, color, AND size all vary (hardest)

Note that add/remove of two *different* pieces always commute as set
operations (`(S + C) - A == (S - A) + C` whenever `A != C`), so "did
the steps in the wrong order" is **not** a meaningful distractor here
— unlike Mental Transformation's rotate+reflect combo, which
genuinely doesn't commute. The real mistakes tested instead: forgot
the remove step (still has A, B, and C), forgot the add step (only B
remains), removed the wrong piece (kept A instead of removing it,
yielding A+C instead of B+C), and a fully unrelated pair — plus a
bounded shape-cycle fallback so distractor generation always
terminates.

Validated programmatically across all 150 specs: the correct result is
always exactly `(B, C)` — the removed piece A is never present and the
added piece C is always present — all 5 choices are unique, and the
correct answer is present at the claimed letter. Spot-rendered and
visually confirmed (grade 4, `combo_ops_hard`): circle+triangle,
add star, remove circle → correctly resolves to triangle+star (choice
A), with all four distractor types visible among the other choices
(forgot-add, forgot-remove, removed-wrong-piece, unrelated).

## Regenerating

```bash
cd question_bank/spatial_visualization/multiple_spatial_operations
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/multiple_spatial_operations
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
