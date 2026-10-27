# Reasoning by Analogy → Color or Shading Change

150 items: 5 grades (K–4) × 5 base questions × (1 original + 5 palette
variations).

Two-pair analogy format with two rule types:

- `fill_on` / `fill_off` — outline ↔ filled (exactly the rule from the
  original 3-question proof-of-concept demo's Analogy video, now
  generalized with palette variations and a reverse direction)
- `color_shift_1/2/3` — shifts N steps along a fixed 6-color cycle

Shape identity differs between A and C (never the same shape — avoids
the copy-shortcut), but the **correct answer's shape always matches
C's shape**; only the varying attribute (fill or color) changes,
exactly like the original demo's circle/triangle example.

Distractors: copying C (no change), copying B wholesale (right
transformation, **wrong shape** — since B's shape is always shape_a,
never shape_c), the correct color/fill applied to the wrong shape, and
an unrelated filler.

Verified against hand-computed examples: `color_shift_3` on a teal
diamond (color index 3) correctly wraps around to a red diamond
(index (3+3) mod 6 = 0).

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/color_shading_change
python generate_bank.py
```

## Rendering

Pick any entry's `question_id` out of one of the files in `questions/`, then render it by
setting `QUESTION_ID` (same code every time -- only the parameters change):

```bash
cd <this subskill dir>
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.
