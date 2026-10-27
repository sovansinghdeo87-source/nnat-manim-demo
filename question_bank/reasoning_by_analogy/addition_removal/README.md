# Reasoning by Analogy → Addition or Removal of Elements

150 items: 5 grades (K–4) × 5 base questions (one per delta amount)
× (1 original + 5 palette variations).

Two-pair analogy format: first pair (A → B) demonstrates "add/remove N
marks from a cluster" (reusing the mark-cluster renderer from Pattern
Completion's Line/Shape Continuation); apply the same delta to a
second pair's starting cluster (C → ?). Mark type is fixed within a
question; A and C start at different counts so the question can't be
answered by copying B.

Five deltas: `add_1`, `add_2`, `add_3`, `remove_1`, `remove_2`.

Distractors: copying C (no change), copying B wholesale (right delta,
wrong starting count), the **opposite** delta (removed instead of
added, or vice versa), and one step past the correct count.

Verified by rendering the worst case found by sweeping all 150 specs
for the highest mark count (12, at `an_add_K_q02_v2`) — stays legible
via the capped-width grid layout.

## Regenerating

```bash
cd question_bank/reasoning_by_analogy/addition_removal
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
