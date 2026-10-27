# Serial Reasoning → Overlay/Intersection Rules

150 items: 5 grades (K–4) × 5 base questions (one per attribute) ×
(1 original + 5 palette variations).

Each box in a 3×3 grid shows **two overlapping shapes**: a larger
"back" shape and a smaller, diagonally-shifted "front" shape drawn on
top of it with partial opacity, so the overlap region is visibly
blended — a literal overlay. The back shape follows a rule down each
**row**; the front shape follows a different rule down each **column**
(reversed for the `_rev` variant). This is the same "independent
row/column attribute" idea as 2×2/3×3 Matrices, but both attributes are
layered into one image instead of split across separate cells — the
skill being tested is pulling two independent rules out of one combined
picture, not just reading one rule per cell.

- `shape_overlay` — back/front shape identity each cycle independently
- `color_overlay` — back is always a circle, front always a square;
  only their colors vary by row/column
- `size_overlay` — fixed shapes/colors, only relative sizes vary
- `combo_overlay` — both shape AND color vary independently per role
  (hardest — four moving parts at once)
- `shape_overlay_rev` — same as `shape_overlay` but the row/column
  roles are swapped, so memorizing "back = row" doesn't work

Distractors are the on-point mistakes: swapping the back/front shapes,
copying the back shape from the wrong row, copying the front shape
from the wrong column, or getting both wrong — plus a bounded
shape-cycle fallback so distractor generation always terminates.

Validated programmatically across all 150 specs: every row's "row
role" value is constant across that row, every column's "column role"
value is constant across that column, all 5 choices are unique, and
the correct answer is always present at the claimed letter.

## Regenerating

```bash
cd question_bank/serial_reasoning/overlay_intersection_rules
python generate_bank.py
```

## Rendering

```bash
cd question_bank/serial_reasoning/overlay_intersection_rules
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
