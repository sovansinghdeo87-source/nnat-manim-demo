# Serial Reasoning → Two Simultaneous Attributes

150 items: 5 grades (K–4) × 5 base questions (one per attribute pair) ×
(1 original + 5 palette variations).

Same "row of three boxed cells, one blank" format as Row Sequences, but
**two** attributes advance together at every step instead of one:

- `shape_color` — shape and color both cycle forward together
- `shape_size` — shape and size both cycle forward together
- `color_size` — color and size both cycle forward together
- `shape_fill` — shape cycles forward, fill (empty/filled) toggles
- `color_fill` — color cycles forward, fill toggles

The skill being tested is specifically whether a student tracks
**both** moving parts at once. Accordingly, the headline distractors
are "forgot one of the two rules" mistakes rather than a generic
off-by-one: one distractor keeps the first attribute frozen at a
neighboring cell's value while the second attribute is correct, and
another does the reverse — plus a same-step-later distractor and an
unrelated one, with a bounded shape-cycle fallback so distractor
generation always terminates.

Validated programmatically across all 150 specs: all 5 choices unique,
correct answer present at the claimed letter, and the row is never
static (both attributes always actually change). Spot-rendered and
visually confirmed the mechanic: e.g. diamond(unfilled) → star(filled)
→ ? correctly resolves to hexagon(unfilled), with distractors being
exactly "right shape, wrong fill" and "right fill, wrong shape."

**Fixed bug — unsolvable middle blank for `shape_fill`/`color_fill`**:
grade 4 normally puts the blank in the middle cell (the hardest
position, requiring interpolation). But fill is boolean (on/off), so
the two *visible* cells in a middle-blank row are always 2 steps
apart — which always share the same fill value whether fill is
constant or toggling every step. A student has no way to distinguish
those two hypotheses from what's shown, making the question
unsolvable even though the generator was internally consistent.
`blank_pos` now overrides grade 4's middle-cell rule specifically for
these two attributes and falls back to the last cell instead, where
the visible 0→1 pair shows the actual toggle directly. Verified
programmatically (no fill-attribute spec ever has `blank_pos == 1`
anymore) and by re-rendering the exact case that surfaced the bug:
circle(filled) → square(unfilled) → ? now correctly and verifiably
resolves to triangle(filled).

## Regenerating

```bash
cd question_bank/serial_reasoning/two_simultaneous_attributes
python generate_bank.py
```

## Rendering

```bash
cd question_bank/serial_reasoning/two_simultaneous_attributes
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

See `../../README.md` for the full taxonomy context and metadata schema.
