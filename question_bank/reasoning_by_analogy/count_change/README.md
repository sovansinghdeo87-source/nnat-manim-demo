# Reasoning by Analogy → Count Change

150 items: 5 grades (K–4) × 5 base questions (one per ratio)
× (1 original + 5 palette variations).

Deliberately distinct from **Addition/Removal of Elements** (additive
delta, ±N): this subskill is **multiplicative** — double, triple,
quadruple, half, or a third. Two-pair analogy format: first pair
(A → B) demonstrates the ratio; apply the same ratio to a second
pair's starting cluster (C → ?). Starting counts come from a pool
chosen so results are always exact whole numbers (e.g. `half` only
starts from even counts).

The standout distractor — **additive instead of multiplicative**
reasoning (`count_c + (count_b - count_a)`) — is the classic analogy
confusion this subskill targets: a student who adds the same *amount*
instead of applying the same *ratio*. Verified in rendered samples:
for `double` (1→4... wait, 1→2), applying to a 2-dot start gives the
additive distractor exactly 3 (2 + 1) alongside the correct
multiplicative answer 4.

**Bug caught during validation**: `count_c`'s original offset formula
(`len(pool)//2 + 1`) reduced to 0 mod 2 for the 2-entry `quadruple`
pool, so `count_a` and `count_c` were always identical — silently
breaking the "can't just copy B" guard. Fixed with a simple `+1`
offset, which is always nonzero mod any pool length ≥ 2.

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/count_change
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
