# Pattern Completion → Repeating Patterns

Pilot subskill for the NNAT3 question bank. 150 question items: 5 grades
(K–4) × 5 base questions × (1 original + 5 palette variations).

## How a question is defined

Every item is fully described by a `PatternSpec` (see `_shared/pattern_lib.py`):

- `grade_rank` — 0 (K) through 4 (Grade 4)
- `attribute` — which dimension repeats: `shape`, `fill` (empty/filled,
  like the original 3-question demo), `color`, `size`, or `combo`
  (shape+color together)
- `period` — how many distinct items make up the repeating unit (derived
  from grade + attribute: 2 for K/Grade1, 3 for Grade2/3, up to 4 for
  Grade4 — see `PERIOD_BY_ATTR_GRADE`)
- `variation_index` / `palette_offset` — 0 for the base question, 1–5 for
  palette variations that test the *same rule* with different concrete
  shapes/colors (so kids can't just memorize one image)

Everything else — the displayed sequence, the correct answer, the 4
distractors, the narration script, and the full visual layout — is
derived deterministically from the spec. Distractor difficulty scales
naturally with period: a period-2 question has 1 "other unit member" +
3 unrelated distractors; a period-4 question has 3 "other unit member"
(near-miss, wrong-position) distractors + only 1 unrelated one.

## Folder layout

```
repeating_patterns/
├── _shared/pattern_lib.py        engine: spec -> image/video/metadata
├── generate_bank.py              writes questions/*.json (25 files)
├── questions/
│   ├── K_q01.json                 one base question + its 5 variations (6 entries)
│   ├── K_q02.json
│   ├── ...                        25 files total (5 grades x 5 base questions)
│   └── 4_q05.json
├── question_image_scene.py       generic Scene, picks entry by QUESTION_ID
└── explanation_video_scene.py    generic VoiceoverScene, picks entry by QUESTION_ID
```

There are no per-question folders or per-question scene files. Each
file in `questions/` is named `<grade_label>_q<NN>.json` and holds one
base question's 6 entries (the base question plus its 5 palette
variations) as a list of plain dicts (metadata: category, skill,
subskill_attribute, difficulty 1–5, grade, correct answer letter, the
repeating unit, and the full explanation script). The two scene files
are the same code for all 150 questions — at render time they parse
the grade label and question number out of `QUESTION_ID` (e.g.
`pc_rp_2_q03_v4` -> `2_q03.json`) to find the right file in
`questions/`, look up the matching entry inside it, and hand its
`PatternSpec` to the shared renderer in `_shared/pattern_lib.py`. The
layout/animation/narration logic lives in
**one place** so bug fixes apply to all 150 items at once, instead of
being hand-duplicated 150 times.

## Regenerating the bank

`questions/*.json` is produced by `generate_bank.py`, which is safe to
re-run any time (it overwrites every file deterministically — nothing
in them is hand-edited):

```bash
cd question_bank/pattern_completion/repeating_patterns
python generate_bank.py
```

No rendering happens in this step — it only writes `questions/*.json`.

## Rendering

Pick any entry's `question_id` out of one of the files in `questions/`, then render it by
setting `QUESTION_ID` (same code every time -- only the parameters change):

```bash
cd <this subskill dir>
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

Omitting `QUESTION_ID` renders the first entry of the first file in `questions/` as a default.

## Known limits of this pilot

- Layout is verified by construction (the sequence row measures its own
  rendered width and uniformly scales down if it would overflow the
  frame — see `build_sequence_group` in `pattern_lib.py`) and spot-checked
  across the easiest and hardest cases (grade K and grade 4, every
  attribute). Not every one of the 150 images has been individually
  rendered and eyeballed.
- Distractor plausibility is rule-based (unit members first, then
  unrelated fillers) rather than hand-tuned per question — reasonable
  for a pilot, worth a pedagogical review pass before shipping to users.
- Narration lines are templated, not individually hand-written — fine
  for internal review, but worth a read-through before Azure-rendering
  the full batch (that step does cost Azure free-tier quota).
