# Pattern Completion → Multi-Rule Patterns

150 items: 5 grades (K–4) × 5 base questions (one per attribute pair)
× (1 original + 5 palette variations).

Two independent attribute cycles run on the same sequence at once —
e.g. shape cycles every 2 steps while color independently cycles every
3 steps, sharing one global step index. Every pair combines one
period-2 and one period-3 sub-cycle (so the combined pattern always has
period lcm(2,3) = 6, but which concrete attribute plays which role
varies):

- `shape_color` — shape period 2, color period 3
- `shape_fill` — shape period 3, fill period 2
- `color_size` — color period 2, size period 3
- `shape_size` — shape period 2, size period 3
- `fill_color` — fill period 2, color period 3

Distractors are specifically "right on one rule, wrong on the other":
correct color but wrong shape, correct shape but wrong color, wrong on
both, or a flat repeat of the last shown item. Verified correct by
manually tracing both sub-cycles against two rendered samples (grade K
`shape_color` and grade 4 `shape_fill`) — in both cases the "obviously
right-looking" choice matched hand-computed `(shape_value, other_value)`
pairs.

**Bug caught before generating**: the first version of the distractor
search had an unbounded `while` loop that could never find a new
candidate (it only varied one attribute within its own small period,
and every value in that period was already used) — this hung the
validation script indefinitely. Fixed by replacing the open-ended
search with a small fixed list of `(delta_a, delta_b)` offset
combinations (bounded, always terminates) and fixing a related bug
where the "repeat the last shown item" distractor was self-excluded by
its own dedup check.

## Regenerating

```bash
cd question_bank/pattern_completion/multi_rule_patterns
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
