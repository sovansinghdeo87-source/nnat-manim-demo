# Serial Reasoning → Row Sequences

150 items: 5 grades (K–4) × 5 base questions (one per rule type)
× (1 original + 5 palette variations).

**Establishes the "row of boxed cells" format** used across Serial
Reasoning: three cells in a row, each in its own box — no connecting
arrows, visually distinct from Pattern Completion's arrow-chained
sequences. A single rule (shift by a constant step through shape,
color, size, rotation, or fill) applies across all three cells.

**Key format differentiator from Pattern Completion**: the blank cell
can be first, middle, or last — not always "what comes next"
(`BLANK_POS_BY_GRADE`). K/1/3 ask for the last cell (the intuitive
case); grade 2 asks for the first cell (requires running the rule
backwards); grade 4 asks for the **middle** cell (requires
interpolating). Verified by rendering all three cases: a `color_shift`
question with red/?/purple correctly resolves to orange — the true
midpoint of the color cycle, not a guess.

**Exception — `fill_shift`**: fill is boolean (on/off), so positions 0
and 2 are *always* identical regardless of whether fill is constant or
toggling every step — a middle blank would be mathematically
unsolvable from what's visible (both hypotheses look the same). For
this one attribute, `blank_pos` overrides grade 4's middle-cell rule
and falls back to the last cell instead, where the visible 0→1 pair
shows the toggle directly. Every other attribute keeps the normal
grade-based position.

Five rule types: `shape_shift`, `color_shift`, `size_shift`,
`rotate_shift`, `fill_shift`.

**Bug caught during validation**: `fill_shift` only has 2 naturally
distinct values (filled/empty), but 5 unique choices are needed. The
original distractor fallback kept extending the same shift family
indefinitely, which can never produce a 4th unique value from a
2-value domain — an infinite loop. Fixed with a bounded fallback that
pads with shape variety (always 6 distinct shapes available,
regardless of how narrow the tested attribute's own domain is).

## Regenerating

```bash
cd question_bank/serial_reasoning/row_sequences
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
