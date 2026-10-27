# Serial Reasoning → Color/Shading Progression

150 items: 5 grades (K–4) × 5 base questions (one per gradient theme)
× (1 original + 5 palette variations).

Reuses the monotonic-gradient content model from Pattern Completion's
Color/Shading Continuation (a trend that continues by one more
increment, never wraps — RGB-interpolated gradients, not hand-picked
steps), but in the "row of boxed cells" format with only 3 cells shown
and the blank position varying by grade.

Five gradient themes: `shade_darker`, `shade_lighter`, `hue_warm`,
`hue_cool`, `intensity_pink`.

Verified against hand-traced examples: pale-yellow → ? → gold (warm
gradient, blank in the middle) and light-gray → medium-gray → ?
(shade_darker, blank last, correctly resolves to the darkest choice).

## Regenerating

```bash
cd question_bank/serial_reasoning/color_shading_progression
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
