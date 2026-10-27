# Serial Reasoning → Position Sequence

150 items: 5 grades (K–4) × 5 base questions (one per position cycle)
× (1 original + 5 palette variations).

Reuses the position-cycle content model from Pattern Completion's
Position and Orientation subskill (a dot cycling through positions in
a frame: left/right, corners clockwise/counter-clockwise, perimeter),
but in the "row of boxed cells" format with only 3 cells shown and the
blank position varying by grade — not a long arrow-chained sequence
always asking "what's next".

Five cycles: `two_lr`, `two_tb`, `four_corners_cw`, `four_corners_ccw`,
`eight_perimeter_cw`.

Verified against the hardest case (`eight_perimeter_cw`, blank in the
middle: top-left → ? → top-right) by rendering an enlarged side-by-side
comparison of the top-left/top-middle/top-right dot positions — the
small thumbnail alone made top-left and top-middle hard to
distinguish by eye, but the zoomed check and the raw coordinate data
both confirmed the generated answer (top-middle) is correct.

## Regenerating

```bash
cd question_bank/serial_reasoning/position_sequence
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
