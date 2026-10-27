# Pattern Completion → Alternating Patterns

150 items: 5 grades (K–4) × 5 base questions (one per attribute: shape,
fill, color, size, combo) × (1 original + 5 palette variations).

The "pure ABAB" special case of Repeating Patterns: the unit is always
exactly 2 items. Unlike Repeating Patterns (where period grows 2→4 with
grade), difficulty here scales via how many cycles are shown
(`CYCLES_SHOWN_BY_GRADE`: 2 cycles at K/1, up to 4 at Grade 4).

Same proven rendering skeleton as `../repeating_patterns/_shared/pattern_lib.py`
(actual-width measurement so nothing overflows the frame, row+arrows
moved as one rigid group so arrows never detach from shapes).

## Regenerating

```bash
cd question_bank/pattern_completion/alternating_patterns
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
