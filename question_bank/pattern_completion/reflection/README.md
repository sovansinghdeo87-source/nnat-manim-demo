# Pattern Completion → Reflection

150 items: 5 grades (K–4) × 5 base questions (one per diagonal-angle
family) × (1 original + 5 palette variations).

A directional arrow alternates between its normal orientation and its
left-right mirror image every step (period 2, like Alternating
Patterns). The base angle is always diagonal (30°–60°, 120°–150°, etc.
— never 0/90/180/270), because a purely horizontal or vertical arrow
looks identical to its own left-right mirror, which would make the
"reflection" invisible.

Verified empirically before building (`flip(axis=UP)` mirrors
left-right, `flip(axis=RIGHT)` mirrors top-bottom — not obvious from
the name, so don't assume).

Distractors specifically target reflection/rotation confusion:

- **rotate90 / rotate180** — a rotation, not a reflection
- **mirror_tb** — mirrored across the *wrong* axis (top-bottom instead
  of left-right) — the classic "which axis" mistake
- the other unit member (repeats instead of continuing the alternation)

## Regenerating

```bash
cd question_bank/pattern_completion/reflection
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
