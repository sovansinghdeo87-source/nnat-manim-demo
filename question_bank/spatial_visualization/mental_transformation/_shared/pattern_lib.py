"""
Shared content engine for Spatial Visualization -> Mental Transformation.

Reuses the same asymmetric triangle+dot shape as Spatial
Visualization's Rotation/Reflection subskills, but now TWO operations
(always one rotation + one reflection, in a stated order) are applied
in sequence: "first do X, then do Y -- what does the shape look like?"

The headline distractor is applying the two steps in the REVERSE
order. This is mathematically guaranteed to differ from the correct
answer (not just "usually different"): composing a rotation with a
reflection is non-commutative whenever the rotation angle is not a
multiple of 180 degrees -- rotate-then-reflect and reflect-then-rotate
produce reflections about genuinely different axes. Every attribute
here pairs a rotation with a reflection (never two rotations, since
rotations alone commute and order would stop mattering), so this
distractor is always a real, distinct image.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import numpy as np
from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

INK = "#1A1A2E"
ACCENT = "#3B82F6"
CORRECT = "#22C55E"
BG = WHITE

TITLE_SIZE = 40
QUESTION_SIZE = 28
CHOICE_LETTER_SIZE = 24
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Spatial Visualization"
QUESTION_TEXT = "Apply both steps in order. Which choice is the result?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

AXIS_VECTORS = {"vertical": RIGHT, "horizontal": UP, "diag_up": np.array([1.0, 1.0, 0.0])}
DIFFICULTY_BY_GRADE = {0: 2, 1: 3, 2: 3, 3: 4, 4: 5}
START_STEP = 29


@dataclass(frozen=True)
class Step:
    kind: str  # "rotate" | "flip" | "none"
    param: float = 0.0
    axis: Optional[str] = None


ATTRIBUTES = ["rotate_then_flip_v", "flip_then_rotate_v", "rotate_then_flip_h",
              "flip_then_rotate_h", "rotate_then_flip_diag"]
ATTR_STEPS = {
    "rotate_then_flip_v": (Step("rotate", 90), Step("flip", axis="vertical")),
    "flip_then_rotate_v": (Step("flip", axis="vertical"), Step("rotate", 90)),
    "rotate_then_flip_h": (Step("rotate", 135), Step("flip", axis="horizontal")),
    "flip_then_rotate_h": (Step("flip", axis="horizontal"), Step("rotate", 135)),
    "rotate_then_flip_diag": (Step("rotate", 60), Step("flip", axis="diag_up")),
}

NONE_STEP = Step("none")


@dataclass(frozen=True)
class PatternSpec:
    grade_rank: int
    question_number: int
    attribute: str
    variation_index: int = 0
    palette_offset: int = 0

    @property
    def grade_label(self) -> str:
        return GRADE_LABELS[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def start_angle(self) -> int:
        return (self.palette_offset * START_STEP) % 360

    @property
    def steps(self) -> tuple[Step, Step]:
        return ATTR_STEPS[self.attribute]

    @property
    def question_id(self) -> str:
        base = f"sv_mxf_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def _perturb_rotate(steps: tuple[Step, Step]) -> tuple[Step, Step]:
    new = []
    for s in steps:
        if s.kind == "rotate":
            new.append(Step("rotate", (s.param + 40) % 360))
        else:
            new.append(s)
    return tuple(new)


def distractor_step_pairs_for(spec: PatternSpec, correct: tuple[Step, Step]) -> list[tuple[Step, Step]]:
    s1, s2 = correct
    reversed_order = (s2, s1)
    only_step1 = (s1, NONE_STEP)
    only_step2 = (NONE_STEP, s2)
    wrong_param = _perturb_rotate(correct)

    candidates = [reversed_order, only_step1, only_step2, wrong_param]
    used = {correct}
    distractors: list[tuple[Step, Step]] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    bump = 80
    while len(distractors) < 4 and bump < 360:
        cand = _perturb_rotate(correct)
        cand = tuple(Step(s.kind, (s.param + bump) % 360, s.axis) if s.kind == "rotate" else s for s in cand)
        bump += 40
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_step_pairs_for(spec: PatternSpec, correct: tuple[Step, Step]) -> tuple[list[tuple[Step, Step]], str]:
    distractors = distractor_step_pairs_for(spec, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _apply_step(group: VGroup, step: Step) -> None:
    if step.kind == "rotate":
        group.rotate(step.param * DEGREES, about_point=ORIGIN)
    elif step.kind == "flip":
        group.flip(axis=AXIS_VECTORS[step.axis], about_point=ORIGIN)


def build_compound(start_angle: int, steps: tuple[Step, ...], scale: float = 1.0, color: str = ACCENT):
    tri = Polygon(ORIGIN, RIGHT * 0.9 * scale, UP * 0.9 * scale,
                  color=color, fill_color=color, fill_opacity=0.85, stroke_width=4)
    dot = Dot(ORIGIN, radius=0.1 * scale, color=INK)
    group = VGroup(tri, dot)
    group.move_to(ORIGIN)
    group.rotate(start_angle * DEGREES, about_point=ORIGIN)
    for step in steps:
        _apply_step(group, step)
    return group


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    q = Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)
    _max_w = min(11, config.frame_width - 1.0)
    if q.width > _max_w:
        q.scale(_max_w / q.width)
    return q


def build_choice_row(start_angle: int, choices: list[tuple[Step, Step]], labels=("A", "B", "C", "D", "E"), buff=0.75):
    group = VGroup(*[build_compound(start_angle, c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
    full = VGroup()
    for letter, mobj in zip(labels, group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(mobj, UP, buff=0.3)
        full.add(VGroup(letter_text, mobj))
    full.move_to(ORIGIN)
    return full


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.25, stroke_width=6, corner_radius=0.1)


_AXIS_WORD = {"vertical": "vertical", "horizontal": "horizontal", "diag_up": "diagonal"}
_STEP_WORD = {"rotate": lambda s: f"turn it {int(s.param)} degrees",
              "flip": lambda s: f"mirror it across the {_AXIS_WORD[s.axis]} line",
              "none": lambda s: "do nothing"}


def _describe(step: Step) -> str:
    return _STEP_WORD[step.kind](step)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    s1, s2 = spec.steps
    return {
        "intro": QUESTION_TEXT,
        "shape": f"Here is a shape. First {_describe(s1)}. Then {_describe(s2)}.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Order matters here -- the opposite order gives a different result.",
        "final": f"So the answer is {correct_letter}.",
    }


def _spread_group_vertically(group, margin: float = 0.6, min_gap: float = 0.5,
                               max_gap: float = 1.6) -> None:
    """Re-stack a VGroup's top-level children (title, question, content,
    choices, ...) top-to-bottom with equal gaps sized to use the full 9:16
    frame, instead of trusting each child's original absolute placement --
    some of which was tuned for a shorter 16:9 frame and left huge or
    lopsided dead space when rendered tall. Children keep their own size
    and internal layout; only the vertical gap between them changes."""
    children = sorted(group.submobjects, key=lambda c: -c.get_center()[1])
    if len(children) < 2:
        return
    content_h = sum(c.height for c in children)
    available = config.frame_height - 2 * margin
    n_gaps = len(children) - 1
    gap = (available - content_h) / n_gaps if n_gaps else 0.0
    gap = max(min_gap, min(max_gap, gap))
    cursor = children[0].get_top()[1]
    for c in children:
        c.shift(UP * (cursor - c.get_top()[1]))
        cursor = c.get_bottom()[1] - gap


def render_question_image(scene: Scene, spec: PatternSpec) -> None:
    scene.camera.background_color = BG
    title = make_title()
    question = make_question().next_to(title, DOWN, buff=0.35)

    shown = build_compound(spec.start_angle, (), scale=1.4)
    _max_w = min(12, config.frame_width - 1.0)
    if shown.width > _max_w:
        shown.scale(_max_w / shown.width)
    shown.next_to(question, DOWN, buff=0.6)

    correct = spec.steps
    choices, _ = choice_step_pairs_for(spec, correct)
    choice_group = build_choice_row(spec.start_angle, choices)
    choice_group.next_to(shown, DOWN, buff=0.9)

    _group = VGroup(title, question, shown, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class MentalTransformationVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)

        with self.voiceover(text=narration_lines(spec, "")["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        shown = build_compound(spec.start_angle, (), scale=1.4)
        _max_w = min(12, config.frame_width - 1.0)
        if shown.width > _max_w:
            shown.scale(_max_w / shown.width)
        shown.move_to(ORIGIN).shift(UP * 0.8)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["shape"]) as tracker:
            self.play(FadeIn(shown, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        correct = spec.steps
        choices, correct_letter = choice_step_pairs_for(spec, correct)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(spec.start_angle, choices)
        choice_group.next_to(shown, DOWN, buff=0.9)

        with self.voiceover(text=lines["choices"]) as tracker:
            self.play(FadeIn(choice_group, shift=UP * 0.3), run_time=0.9)
            self.wait(tracker.get_remaining_duration())

        correct_index = "ABCDE".index(correct_letter)
        choice_correct = choice_group[correct_index]
        box = surround(choice_correct)
        with self.voiceover(text=lines["reveal"]) as tracker:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(choice_correct, color=CORRECT, scale_factor=1.15), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(choice_group), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(shown, DOWN, buff=0.7)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, shown, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    correct = spec.steps
    choices, correct_letter = choice_step_pairs_for(spec, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "spatial_visualization",
        "skill": "mental_transformation",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "start_angle": spec.start_angle,
        "steps": [f"{s.kind}:{s.param}:{s.axis}" for s in spec.steps],
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sv_mxf_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["shape"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
