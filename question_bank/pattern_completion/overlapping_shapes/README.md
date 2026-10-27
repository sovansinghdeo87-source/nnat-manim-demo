# Pattern Completion → Overlapping Shapes

150 items: 5 grades (K–4) × 5 base questions (one per shape pair)
× (1 original + 5 palette variations).

Two fixed, overlapping shapes alternate which one is drawn on top
every step (period 2, like Alternating Patterns). Shape identity, size,
color, and overlap amount all stay constant; only front/back order
changes. Z-order in Manim is draw-order within a `VGroup` — whichever
shape is added last renders on top.

**Fix applied after spot-rendering**: shapes were originally drawn at
`fill_opacity=0.9` so the back shape's color would faintly tint through
the overlap. For simple pairs (circle+square) this read fine, but for
complex silhouettes (star+hexagon) the tinting was too subtle to
clearly tell which shape was in front — verified by rendering both
z-orders side by side at 3x scale. Switched to `fill_opacity=1` (sharp
hard occlusion, no blending) — now the "back" shape's silhouette is
visibly cut off by the front one in every pair, confirmed by
re-rendering the same comparison.

Distractors: the other z-order (didn't alternate), shapes with **no
overlap** (wrong relationship entirely), one shape **swapped** for an
unrelated third shape, and a **tighter overlap** than established
(changed the relationship, not just the order).

## Regenerating

```bash
cd question_bank/pattern_completion/overlapping_shapes
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
