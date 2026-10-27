# Pattern Completion → Symmetry

150 items: 5 grades (K–4) × 5 base questions (one per motif)
× (1 original + 5 palette variations).

**Different engine from the other 9 subskills.** This is not a
sequence-with-arrows question — a square frame is split by a dashed
vertical mirror line. The left half shows 1–3 small marks (more marks
at higher grades, `MARKS_COUNT_BY_GRADE`); the right half is blank. The
student picks which of 5 complete pictures correctly mirrors the left
half across the line.

Four distractor types, always present regardless of mark count:

- `upside_down` — right half flipped across **both** axes (wrong-axis
  mistake — rotated instead of mirrored)
- `no_mirror` — right half has the same arrangement as the left, just
  moved over, **not reflected** (mirror vs. copy confusion)
- `shifted` — correctly mirrored but offset vertically (off
  registration)
- `color_swap` — correct shape and position, wrong color

**Two bugs caught during spot-rendering:**

1. Marks positioned near a pool extreme (e.g. `(-0.32, 0.32)`) landed
   with their *center* exactly on the frame's corner, so the mark's own
   radius pushed it visibly outside the frame border. Fixed by
   loosening the position-to-frame normalization divisor (0.32 → 0.45),
   giving every mark margin from the edge.
2. The overall layout (title + question + big frame + choice row) was
   taller than the renderable frame, cutting the choices off at the
   bottom. Fixed by shrinking the big frame's scale (3.4 → 2.5) and
   tightening a buffer.
3. **Design flaw, not just a rendering bug**: the original `no_mirror`
   distractor kept a mark's `x` unchanged, which for a single mark
   landed it exactly on top of the original left-half mark — visually
   indistinguishable from "nothing on the right side" rather than a
   plausible wrong answer. Fixed by shifting the mark into the right
   half without reflecting it, so it reads as a genuine (if wrong)
   attempt at completing the picture.

All fixes verified by re-rendering the kindergarten (1 mark) and
grade-4 (3 marks, hardest) cases and checking the resulting image
against each question's own `question.json` metadata.

## Regenerating

```bash
cd question_bank/pattern_completion/symmetry
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
