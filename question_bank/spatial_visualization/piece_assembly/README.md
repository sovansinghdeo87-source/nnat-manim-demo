# Spatial Visualization → Piece Assembly

150 items: 5 grades (K–4) × 5 base questions (one per cut type) ×
(1 original + 5 palette variations).

Shows a target rectangle's outline, then 5 candidate **pairs** of
separate rectangular pieces (drawn with a visible gap between them, to
true scale against the target). The student must judge which pair's
combined dimensions would exactly tile the target if pushed together —
genuine piece-assembly reasoning (mentally summing two disjoint
pieces' dimensions), distinct from Shape Combination/Overlay (which
stack pieces on top of each other rather than tiling them edge to
edge).

- `vertical_half` — vertical cut at the midpoint (easiest — equal halves)
- `vertical_uneven` — vertical cut at 1/3
- `horizontal_half` — horizontal cut at the midpoint
- `horizontal_uneven` — horizontal cut at 1/3
- `vertical_quarter` — vertical cut at 1/4 (hardest — most uneven split)

Distractors are the on-point mistakes: one piece's cross-dimension
shrunk (looks plausible edge-on but wouldn't align — "height
mismatch"), one piece's along-axis dimension stretched 30% too wide
(a deliberately subtle "close but doesn't quite sum right" trap), the
pieces for the *other* cut orientation entirely (wide flat bars instead
of tall narrow ones, or vice versa), and a fully unrelated small pair —
plus a bounded shrink-step fallback so distractor generation always
terminates.

**Known simplification**: pieces are always axis-aligned rectangles
cut by one straight vertical or horizontal line (no diagonal or
triangular pieces) — this keeps "do these dimensions sum correctly" an
exact, checkable arithmetic fact rather than requiring real polygon
geometry.

Validated programmatically across all 150 specs with real arithmetic
checks, not just uniqueness: the correct pair's dimensions are verified
to sum exactly to the target's width/height, and — critically — every
single distractor is verified to **not** also exactly tile the target
(which would make the question ambiguous with two valid answers).
Spot-rendered and numerically cross-checked (grade 4,
`vertical_quarter`, target 3.4×1.7): correct answer (E) is
`(0.85,1.7)+(2.55,1.7)`, summing exactly to `3.4`; the closest
distractor (D) is `(1.105,1.7)+(2.55,1.7)` — deliberately only 30% off
on one piece — and choice A visibly shows the flat, wide
wrong-orientation pieces.

## Regenerating

```bash
cd question_bank/spatial_visualization/piece_assembly
python generate_bank.py
```

## Rendering

```bash
cd question_bank/spatial_visualization/piece_assembly
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
