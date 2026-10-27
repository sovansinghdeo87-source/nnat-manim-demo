# Serial Reasoning → Column Sequences

150 items: 5 grades (K–4) × 5 base questions (one per rule type)
× (1 original + 5 palette variations).

Same mechanic as Row Sequences, rotated 90 degrees: three cells
stacked in a column, each in its own box. Answer choices stay in a
horizontal row regardless (the standard NNAT choice-row convention) —
only the question figure's own arrangement is vertical.

Blank cell position (`BLANK_POS_BY_GRADE`): K/1/3 ask for the
**bottom** cell (intuitive); grade 2 asks for the **top** cell (run
the rule backwards); grade 4 asks for the **middle** cell
(interpolate). Verified by rendering both the easy (bottom-blank) and
hardest (middle-blank) cases — both resolve correctly against the
shape cycle.

**Exception — `fill_shift`**: fill is boolean (on/off), so the two
visible cells are always identical regardless of whether fill is
constant or toggling every step — a middle blank would be
mathematically unsolvable from what's visible. For this one attribute,
`blank_pos` overrides grade 4's middle-cell rule and falls back to the
last cell instead, where the actual toggle is directly visible.

Reused `row_sequences`' validated logic directly; the only functional
change is `build_row`'s `arrange(DOWN, ...)` instead of `arrange(RIGHT,
...)`, plus a reduced cell scale (1.0 → 0.75) since a stacked column of
3 boxes is much taller than a horizontal row of the same boxes and
would otherwise push the choices off-frame.

## Regenerating

```bash
cd question_bank/serial_reasoning/column_sequences
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
