# Reasoning by Analogy → Size Change

150 items: 5 grades (K–4) × 5 base questions (one per shift amount)
× (1 original + 5 palette variations).

Two-pair analogy format: first pair (A → B) demonstrates "grow/shrink
by N discrete size steps" (`SIZE_LEVELS`, 6 steps); apply the same
step count to a second pair's starting shape (C → ?). Shape identity
stays constant within one question (circle, square, etc. — only size
varies, so size is the only thing being tested across A/B/C/correct).

Five shift amounts: `grow_1`, `grow_2`, `grow_3`, `shrink_1`,
`shrink_2`. `idx_a` and `idx_c` (starting size-level indices) are
always different — proven mathematically in code comments, not just
tested — so the question can't be answered by copying B.

Distractors: copying C (no change), copying B (right transformation,
wrong figure), one step past the correct size (overshoot), and the
**opposite direction** (shrank instead of grew, or vice versa).

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/size_change
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
