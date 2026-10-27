# NNAT3 Question Bank

Content bank for the NNAT3 preparation app, organized by the taxonomy
from the syllabus doc: **reasoning area → skill/subskill → grade →
question**. Each question stores its metadata, its Manim question-image
scene, and its Manim explanation-video scene (narrated with Azure TTS,
same pipeline as the 3 proof-of-concept demo videos in `manim/`).

## Status

| Reasoning area | Subskill | Status |
|---|---|---|
| Pattern Completion | Repeating Patterns | **Built** — 150 items. See `pattern_completion/repeating_patterns/README.md`. |
| Pattern Completion | Alternating Patterns | **Built** — 150 items. See `pattern_completion/alternating_patterns/README.md`. |
| Pattern Completion | Color/Shading Continuation | **Built** — 150 items. See `pattern_completion/color_shading_continuation/README.md`. |
| Pattern Completion | Line/Shape Continuation | **Built** — 150 items. See `pattern_completion/line_shape_continuation/README.md`. |
| Pattern Completion | Rotation | **Built** — 150 items. See `pattern_completion/rotation/README.md`. |
| Pattern Completion | Reflection | **Built** — 150 items. See `pattern_completion/reflection/README.md`. |
| Pattern Completion | Position and Orientation | **Built** — 150 items. See `pattern_completion/position_orientation/README.md`. |
| Pattern Completion | Overlapping Shapes | **Built** — 150 items. See `pattern_completion/overlapping_shapes/README.md`. |
| Pattern Completion | Multi-Rule Patterns | **Built** — 150 items. See `pattern_completion/multi_rule_patterns/README.md`. |
| Pattern Completion | Symmetry | **Built** — 150 items. See `pattern_completion/symmetry/README.md`. |
| Reasoning by Analogy | Rotation | **Built** — 150 items. See `reasoning_by_analogy/rotation/README.md`. |
| Reasoning by Analogy | Reflection | **Built** — 150 items. See `reasoning_by_analogy/reflection/README.md`. |
| Reasoning by Analogy | Size Change | **Built** — 150 items. See `reasoning_by_analogy/size_change/README.md`. |
| Reasoning by Analogy | Shape Change | **Built** — 150 items. See `reasoning_by_analogy/shape_change/README.md`. |
| Reasoning by Analogy | Color/Shading Change | **Built** — 150 items. See `reasoning_by_analogy/color_shading_change/README.md`. |
| Reasoning by Analogy | Addition/Removal of Elements | **Built** — 150 items. See `reasoning_by_analogy/addition_removal/README.md`. |
| Reasoning by Analogy | Movement/Position Change | **Built** — 150 items. See `reasoning_by_analogy/movement_position/README.md`. |
| Reasoning by Analogy | Count Change | **Built** — 150 items. See `reasoning_by_analogy/count_change/README.md`. |
| Reasoning by Analogy | Inside-Outside Transformation | **Built** — 150 items. See `reasoning_by_analogy/inside_outside/README.md`. |
| Reasoning by Analogy | Combined Transformations | **Built** — 150 items. See `reasoning_by_analogy/combined_transformations/README.md`. |
| Serial Reasoning | Row Sequences | **Built** — 150 items. See `serial_reasoning/row_sequences/README.md`. |
| Serial Reasoning | Column Sequences | **Built** — 150 items. See `serial_reasoning/column_sequences/README.md`. |
| Serial Reasoning | 2×2 Matrices | **Built** — 150 items. See `serial_reasoning/two_by_two_matrices/README.md`. |
| Serial Reasoning | 3×3 Matrices | **Built** — 150 items. See `serial_reasoning/three_by_three_matrices/README.md`. |
| Serial Reasoning | Shape Progression | **Built** — 150 items. See `serial_reasoning/shape_progression/README.md`. |
| Serial Reasoning | Rotation Sequence | **Built** — 150 items. See `serial_reasoning/rotation_sequence/README.md`. |
| Serial Reasoning | Position Sequence | **Built** — 150 items. See `serial_reasoning/position_sequence/README.md`. |
| Serial Reasoning | Count Progression | **Built** — 150 items. See `serial_reasoning/count_progression/README.md`. |
| Serial Reasoning | Alternation | **Built** — 150 items. See `serial_reasoning/alternation/README.md`. |
| Serial Reasoning | Addition/Subtraction of Elements | **Built** — 150 items. See `serial_reasoning/addition_subtraction/README.md`. |
| Serial Reasoning | Color/Shading Progression | **Built** — 150 items. See `serial_reasoning/color_shading_progression/README.md`. |
| Serial Reasoning | Distribution Rules | **Built** — 150 items. See `serial_reasoning/distribution_rules/README.md`. |
| Serial Reasoning | Overlay/Intersection Rules | **Built** — 150 items. See `serial_reasoning/overlay_intersection_rules/README.md`. |
| Serial Reasoning | Two Simultaneous Attributes | **Built** — 150 items. See `serial_reasoning/two_simultaneous_attributes/README.md`. |
| Serial Reasoning | Multi-Rule Matrices | **Built** — 150 items. See `serial_reasoning/multi_rule_matrices/README.md`. |
| Spatial Visualization | Shape Combination | **Built** — 150 items. See `spatial_visualization/shape_combination/README.md`. |
| Spatial Visualization | Shape Subtraction | **Built** — 150 items. See `spatial_visualization/shape_subtraction/README.md`. |
| Spatial Visualization | Overlay | **Built** — 150 items. See `spatial_visualization/overlay/README.md`. |
| Spatial Visualization | Rotation | **Built** — 150 items. See `spatial_visualization/rotation/README.md`. |
| Spatial Visualization | Reflection | **Built** — 150 items. See `spatial_visualization/reflection/README.md`. |
| Spatial Visualization | Folding and Unfolding | **Built** — 150 items. See `spatial_visualization/folding_and_unfolding/README.md`. |
| Spatial Visualization | Mental Transformation | **Built** — 150 items. See `spatial_visualization/mental_transformation/README.md`. |
| Spatial Visualization | Piece Assembly | **Built** — 150 items. See `spatial_visualization/piece_assembly/README.md`. |
| Spatial Visualization | Hidden/Overlapping Shapes | **Built** — 150 items. See `spatial_visualization/hidden_overlapping_shapes/README.md`. |
| Spatial Visualization | Multiple Spatial Operations | **Built** — 150 items. See `spatial_visualization/multiple_spatial_operations/README.md`. |

**All 45 subskills across all 4 reasoning areas are built: 6,750
question items** (5 grades × 5 base questions × 6 variants — 1 base +
5 palette variations — each subskill = 150 items). Pattern Completion
(10 subskills) uses a "sequence of items → 5 choices" format;
Reasoning by Analogy (10) uses a "two shape-pairs → 5 choices" format
(first pair demonstrates a transformation rule, second pair applies
it); Serial Reasoning (15) uses row/column/matrix layouts with one
blank cell to fill; Spatial Visualization (10) uses piece-based
formats with no sequence and no blank cell (combine/subtract/overlay
pieces, rotate/reflect a shape, fold-and-punch a grid, assemble pieces
to a target, find a hidden shape, or chain multiple operations). Each
subskill gets its own `_shared/pattern_lib.py`. Every subskill was
validated programmatically — choice uniqueness/correctness across all
specs, plus subskill-specific invariants where relevant (e.g. real
geometric reflection-closure checks for Folding and Unfolding, exact
arithmetic tiling checks for Piece Assembly, ambiguity checks for
Hidden/Overlapping Shapes) — and spot-rendered (easiest + hardest
cases) before being accepted. Several real bugs were caught and fixed
this way (including recurring unbounded-loop distractor-search bugs),
see each subskill's README for specifics.

## Folder structure

```
question_bank/
└── <reasoning_area>/                e.g. pattern_completion
    └── <skill>/                     e.g. repeating_patterns
        ├── README.md                 how this subskill's questions are generated
        ├── generate_bank.py           writes questions/*.json (does not render anything)
        ├── questions/
        │   ├── K_q01.json              one base question + its 5 variations (6 entries)
        │   ├── K_q02.json
        │   ├── ...                     25 files total (5 grades x 5 base questions)
        │   └── 4_q05.json
        ├── question_image_scene.py    generic Manim Scene -> picks one entry via QUESTION_ID env var
        ├── explanation_video_scene.py generic Manim VoiceoverScene -> same, for the narrated video
        └── _shared/
            └── pattern_lib.py         ALL layout/animation/narration logic lives here
```

There are no per-question folders and no per-question scene files. Each
file in `questions/` is named `<grade_label>_q<NN>.json` (e.g.
`K_q01.json`, `2_q03.json`) and holds that one base question's 6
entries (the base question plus its 5 palette variations, grouped
together because they test the exact same rule). The two scene files
are identical code across all 150 questions in a subskill — at render
time they parse the grade label and question number out of the
`QUESTION_ID` environment variable (e.g. `pc_rp_2_q03_v4` ->
`2_q03.json`) to find the right file in `questions/`, look up the
matching entry inside it, and hand its parameters to the shared
renderer in `_shared/pattern_lib.py`. The same question (5 variations +
1 base) differs only in parameters — shape, color, grade, etc. — never
in code.

## Design principle: one shared engine per subskill, not 150+ hand-written files

Every subskill gets its own `_shared/` library that turns a small spec
(grade, rule, which concrete shapes/colors) into the full question:
sequence, distractors, layout, and narration script. The two scene
files are thin — they just look up a spec from `questions/*.json` and
hand it to the shared renderer. This keeps the bank consistent (one bug
fix applies everywhere) and makes "5 questions + 5 variations per
grade" a matter of generating JSON entries, not hand-authoring Manim
scenes one at a time.

## Metadata schema (one entry inside a `questions/*.json` file)

Matches the "Recommended question metadata example" from the syllabus
doc, plus the fields needed to actually render/explain the question:

```json
{
  "question_id": "pc_rp_2_q01",
  "category": "pattern_completion",
  "skill": "repeating_patterns",
  "subskill_attribute": "shape",
  "difficulty": 3,
  "grade_label": "2",
  "minimum_grade": 2,
  "maximum_grade": 2,
  "variation_of": null,
  "variation_index": 0,
  "correct_answer": "B",
  "format": "multiple_choice_5",
  "unit_pattern": ["circle", "square", "triangle"],
  "explanation_script": ["...", "..."]
}
```

## Content-authoring principle

All content here is originally generated (no reproduction of secure
NNAT test items) — consistent with the syllabus doc's note that the app
should teach reasoning patterns and question-format familiarity, not
reproduce live test content.

## Rendering

Nothing in this bank is pre-rendered. Every subskill has the same two
generic scene files; pick a `question_id` from any file in that
subskill's `questions/` folder and render it with the `QUESTION_ID`
environment variable:

```bash
cd question_bank/<reasoning_area>/<skill>
QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo   # needs Azure creds
```

See the subskill README for subskill-specific notes.
