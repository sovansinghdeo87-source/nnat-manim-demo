# Pattern Completion → Position and Orientation

150 items: 5 grades (K–4) × 5 base questions (one per position cycle)
× (1 original + 5 palette variations).

Each item is a small square frame with a dot at one position inside
it. The dot cycles through a fixed set of positions — same cyclic math
as Repeating Patterns, but the "token" is a position-in-a-frame instead
of a shape attribute. Five cycles:

- `two_lr` / `two_tb` — alternates left↔right or top↔bottom (period 2)
- `four_corners_cw` / `four_corners_ccw` — around the 4 corners,
  clockwise or counter-clockwise (period 4)
- `eight_perimeter_cw` — all 8 perimeter spots, clockwise (period 8)

**Bug caught during spot-rendering**: the first version showed 3 full
cycles for every attribute regardless of period, which meant the
8-position cycle rendered 24 tiny illegible squares in a row. Fixed by
`displayed_count` targeting a roughly constant total item count
(`TARGET_ITEMS_BY_GRADE`, 4–8 items) instead of a constant number of
*cycles* — cycles-shown now scales down as period grows, verified by
re-rendering the period-8 case (now 8 items, clean and legible).

## Regenerating

```bash
cd question_bank/pattern_completion/position_orientation
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
