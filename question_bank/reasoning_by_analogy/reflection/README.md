# Reasoning by Analogy → Reflection

150 items: 5 grades (K–4) × 5 base questions × (1 original + 5 palette
variations).

Two-pair analogy format (see `../rotation/README.md` for the general
pattern): first pair (A → B) demonstrates "mirror left-right"; apply
the same rule to a second pair's starting arrow (C → ?).

A and C are the same arrow marker at two **different diagonal**
starting angles — never equal (copy-shortcut) and never
horizontal/vertical (a horizontal or vertical arrow is its own
left-right mirror, which would make the question trivial).

Mirror formulas used throughout (reflecting direction vector
`(cos θ, sin θ)`):
- left-right mirror (vertical line): `(180 - θ) mod 360`
- top-bottom mirror (horizontal line): `(360 - θ) mod 360`

Distractors: mirroring across the **wrong axis** (top-bottom instead
of left-right), **copying B** instead of transforming C, not
mirroring at all, and a 180° rotation (a different transformation
entirely).

Validated programmatically: `angle_a != angle_c`, and both are always
diagonal (`% 90 != 0`), across all 150 specs.

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/reflection
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
