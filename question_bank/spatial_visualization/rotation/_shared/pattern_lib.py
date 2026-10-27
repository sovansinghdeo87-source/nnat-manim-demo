"""
Shared content engine for Spatial Visualization -> Rotation.

A genuine mental-rotation task, distinct from Pattern Completion's
Rotation (a SEQUENCE of rotating arrows) and Reasoning by Analogy's
Rotation (A->B :: C->? transformation pairs). Here there is a single
snapshot: an intentionally asymmetric compound shape (a right triangle
with a dot marking one specific corner, so it has no rotational or
reflective symmetry) is shown in one orientation; the student must
identify which answer choice shows the SAME shape correctly rotated by
a given amount.

The headline distractor is the classic rotation-vs-reflection
confusion: a mirrored version of the correct answer looks deceptively
similar (same silhouette family) but is NOT reachable by any rotation
-- exactly the mistake this subskill targets.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

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
QUESTION_TEXT = "Which choice shows this shape rotated the matching amount?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

ATTRIBUTES = ["quarter_turn", "eighth_turn", "half_turn", "third_turn", "odd_turn"]
TURN_DEGREES = {"quarter_turn": 90, "eighth_turn": 45, "half_turn": 180,
                 "third_turn": 120, "odd_turn": 73}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}

START_STEP = 37  # non-aligning step so start orientation varies across variations


@dataclass(frozen=True)
class Orientation:
    angle: int
    mirrored: bool = False

    def __post_init__(self):
        object.__setattr__(self, "angle", self.angle % 360)


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
    def turn_degrees(self) -> int:
        return TURN_DEGREES[self.attribute]

    @property
    def question_id(self) -> str:
        base = f"sv_rot_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def start_orientation_for(spec: PatternSpec) -> Orientation:
    return Orientation(angle=spec.start_angle, mirrored=False)


def correct_orientation_for(spec: PatternSpec) -> Orientation:
    return Orientation(angle=spec.start_angle + spec.turn_degrees, mirrored=False)


def distractor_orientations_for(spec: PatternSpec, correct: Orientation) -> list[Orientation]:
    overshoot = Orientation(angle=correct.angle + 30, mirrored=False)
    undershoot = Orientation(angle=correct.angle - 30, mirrored=False)
    mirrored = Orientation(angle=correct.angle, mirrored=True)
    unrelated = Orientation(angle=correct.angle + 150, mirrored=False)

    candidates = [overshoot, undershoot, mirrored, unrelated]
    used = {correct}
    distractors: list[Orientation] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    step = 15
    while len(distractors) < 4 and step < 360:
        cand = Orientation(angle=correct.angle + step, mirrored=False)
        step += 15
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_orientations_for(spec: PatternSpec, correct: Orientation) -> tuple[list[Orientation], str]:
    distractors = distractor_orientations_for(spec, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def build_compound(orientation: Orientation, scale: float = 1.0, color: str = ACCENT):
    tri = Polygon(ORIGIN, RIGHT * 0.9 * scale, UP * 0.9 * scale,
                  color=color, fill_color=color, fill_opacity=0.85, stroke_width=4)
    dot = Dot(ORIGIN, radius=0.1 * scale, color=INK)
    group = VGroup(tri, dot)
    group.move_to(ORIGIN)
    if orientation.mirrored:
        group.flip(RIGHT)
    group.rotate(orientation.angle * DEGREES, about_point=ORIGIN)
    return group


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    q = Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)
    _max_w = min(11, config.frame_width - 1.0)
    if q.width > _max_w:
        q.scale(_max_w / q.width)
    return q


def build_choice_row(choices: list[Orientation], labels=("A", "B", "C", "D", "E"), buff=0.75):
    group = VGroup(*[build_compound(c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
    full = VGroup()
    for letter, mobj in zip(labels, group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(mobj, UP, buff=0.3)
        full.add(VGroup(letter_text, mobj))
    full.move_to(ORIGIN)
    return full


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.25, stroke_width=6, corner_radius=0.1)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": QUESTION_TEXT,
        "shape": f"Here is a shape. Imagine turning it by {spec.turn_degrees} degrees.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "A rotation just turns the shape -- a flipped mirror image is different.",
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

    start = start_orientation_for(spec)
    shown = build_compound(start, scale=1.4)
    _max_w = min(12, config.frame_width - 1.0)
    if shown.width > _max_w:
        shown.scale(_max_w / shown.width)
    shown.next_to(question, DOWN, buff=0.6)

    correct = correct_orientation_for(spec)
    choices, _ = choice_orientations_for(spec, correct)
    choice_group = build_choice_row(choices)
    choice_group.next_to(shown, DOWN, buff=0.9)

    _group = VGroup(title, question, shown, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class RotationVideoScene(VoiceoverScene):
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

        start = start_orientation_for(spec)
        shown = build_compound(start, scale=1.4)
        _max_w = min(12, config.frame_width - 1.0)
        if shown.width > _max_w:
            shown.scale(_max_w / shown.width)
        shown.move_to(ORIGIN).shift(UP * 0.8)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["shape"]) as tracker:
            self.play(FadeIn(shown, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        correct = correct_orientation_for(spec)
        choices, correct_letter = choice_orientations_for(spec, correct)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
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
    correct = correct_orientation_for(spec)
    choices, correct_letter = choice_orientations_for(spec, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "spatial_visualization",
        "skill": "rotation",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "start_angle": spec.start_angle,
        "turn_degrees": spec.turn_degrees,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sv_rot_{spec.grade_label}_q{spec.question_number:02d}"
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
