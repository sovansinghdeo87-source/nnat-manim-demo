"""
Shared content engine for Pattern Completion -> Rotation.

A directional arrow marker rotates by a constant angle increment every
step (e.g. 0, 90, 180, 270 degrees -> ?). An arrow is used specifically
because it has NO rotational symmetry -- unlike an equilateral triangle
(which maps onto itself every 120 degrees and would make a 120-degree
increment invisible), every rotation of an arrow looks different until
a full 360-degree turn.

Five base questions = five increments (one per attribute):
    half_turn  -- 180 degrees (period 2, easiest)
    third_turn -- 120 degrees (period 3)
    quarter_turn -- 90 degrees (period 4)
    sixth_turn -- 60 degrees (period 6)
    eighth_turn -- 45 degrees (period 8, hardest)
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
QUESTION_SIZE = 30
CHOICE_LETTER_SIZE = 24
EXPLAIN_SIZE = 26
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Pattern Completion"
QUESTION_TEXT = "Which figure comes next?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

INCREMENT_BY_ATTR = {
    "half_turn": 180,
    "third_turn": 120,
    "quarter_turn": 90,
    "sixth_turn": 60,
    "eighth_turn": 45,
}
ATTRIBUTES = list(INCREMENT_BY_ATTR.keys())

DISPLAYED_COUNT_BY_GRADE = {0: 3, 1: 3, 2: 4, 3: 4, 4: 5}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}

START_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]


@dataclass(frozen=True)
class PatternSpec:
    grade_rank: int
    question_number: int
    attribute: str  # increment name
    variation_index: int = 0
    palette_offset: int = 0

    @property
    def grade_label(self) -> str:
        return GRADE_LABELS[self.grade_rank]

    @property
    def increment(self) -> int:
        return INCREMENT_BY_ATTR[self.attribute]

    @property
    def start_angle(self) -> int:
        return START_ANGLES[self.palette_offset % len(START_ANGLES)]

    @property
    def displayed_count(self) -> int:
        return DISPLAYED_COUNT_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_rot_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def angles_for(spec: PatternSpec) -> tuple[list[int], int]:
    shown = [(spec.start_angle + i * spec.increment) % 360 for i in range(spec.displayed_count)]
    correct = (spec.start_angle + spec.displayed_count * spec.increment) % 360
    return shown, correct


def distractor_angles_for(spec: PatternSpec, shown: list[int], correct: int) -> list[int]:
    inc = spec.increment
    overshoot = (correct + inc) % 360
    undershoot = shown[-1]
    wrong_direction = (shown[-1] - inc) % 360  # rotated the "wrong way"
    overshoot2 = (correct + 2 * inc) % 360
    far_away = (correct + 180) % 360

    hard = spec.grade_rank >= 3
    candidates = [overshoot, wrong_direction, overshoot2 if hard else far_away, undershoot]

    used = {correct, *shown}
    distractors: list[int] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    salt = 1
    while len(distractors) < 4:
        cand = (correct + salt * 30) % 360
        salt += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_angles_for(spec: PatternSpec, shown: list[int], correct: int) -> tuple[list[int], str]:
    distractors = distractor_angles_for(spec, shown, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _arrow_marker(angle_deg: float, scale: float = 1.0):
    arrow = Arrow(
        ORIGIN, RIGHT * 0.95 * scale, buff=0, color=INK, stroke_width=8,
        max_tip_length_to_length_ratio=0.4,
    )
    arrow.rotate(angle_deg * DEGREES, about_point=arrow.get_start())
    return arrow


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    shown, correct = angles_for(spec)
    mobjs = [_arrow_marker(a, 1.0) for a in shown] + [_qmark(1.0)]
    row = VGroup(*mobjs).arrange(RIGHT, buff=0.7)

    arrows = VGroup()
    for a, b in zip(mobjs[:-1], mobjs[1:]):
        arrows.add(Arrow(a.get_right(), b.get_left(), buff=0.08, color=ACCENT,
                          stroke_width=4, max_tip_length_to_length_ratio=0.25))

    full = VGroup(row, arrows)
    item_scale = 1.0
    max_width = min(MAX_SEQUENCE_WIDTH, config.frame_width - 1.0)
    if full.width > max_width:
        item_scale = max_width / full.width
        full.scale(item_scale)

    return row, arrows, mobjs, shown, correct, item_scale


def build_choice_group(spec: PatternSpec, shown: list[int], correct: int):
    choices, correct_letter = choice_angles_for(spec, shown, correct)
    markers = [_arrow_marker(a, 0.85) for a in choices]
    group = VGroup(*markers).arrange(RIGHT, buff=1.1)

    full = VGroup()
    for letter, marker in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(marker, UP, buff=0.35)
        full.add(VGroup(letter_text, marker))
    full.move_to(ORIGIN)
    _max_w = min(12, config.frame_width - 1.0)
    if full.width > _max_w:
        full.scale(_max_w / full.width)
    return full, correct_letter


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.32, stroke_width=6, corner_radius=0.12)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": "Which figure comes next?",
        "sequence": f"Watch the arrow. Every step, it turns {spec.increment} degrees.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"It keeps turning {spec.increment} degrees. One more turn.",
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
    question = make_question().next_to(title, DOWN, buff=0.55)

    row, arrows, _, shown, correct, item_scale = build_sequence_group(spec)
    sequence_group = VGroup(row, arrows)
    sequence_group.move_to(ORIGIN).shift(UP * 0.6)

    choices, _ = build_choice_group(spec, shown, correct)
    choices.next_to(sequence_group, DOWN, buff=1.3)

    _group = VGroup(title, question, sequence_group, choices)
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
        question = make_question().next_to(title, DOWN, buff=0.55)

        row, arrows, mobjs, shown, correct, item_scale = build_sequence_group(spec)
        sequence_group = VGroup(row, arrows)
        sequence_group.next_to(question, DOWN, buff=2.4)
        choices, correct_letter = build_choice_group(spec, shown, correct)
        choices.next_to(sequence_group, DOWN, buff=2.8)
        lines = narration_lines(spec, correct_letter)

        with self.voiceover(text=lines["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        with self.voiceover(text=lines["sequence"]) as tracker:
            run_time_each = max(0.3, min(1.0, tracker.duration / max(len(mobjs), 1)))
            self.play(FadeIn(mobjs[0], scale=0.7), run_time=run_time_each)
            for arrow, mobj in zip(arrows, mobjs[1:]):
                self.play(GrowArrow(arrow), FadeIn(mobj, scale=0.7), run_time=run_time_each)
            self.wait(tracker.get_remaining_duration())

        with self.voiceover(text=lines["choices"]) as tracker:
            self.play(FadeIn(choices, shift=UP * 0.3), run_time=0.9)
            self.wait(tracker.get_remaining_duration())

        correct_index = "ABCDE".index(correct_letter)
        choice_correct = choices[correct_index]
        box = surround(choice_correct)
        with self.voiceover(text=lines["reveal"]) as tracker:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(choice_correct, color=CORRECT, scale_factor=1.15), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        resolved = _arrow_marker(correct, item_scale)
        resolved.move_to(mobjs[-1].get_center())
        explain = Text(
            f"turns {spec.increment} degrees each step",
            font_size=EXPLAIN_SIZE, color=INK,
        ).next_to(sequence_group, DOWN, buff=2.8)

        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(mobjs[-1], scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.6)
            mobjs[-1].set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.play(Write(explain), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(explain, DOWN, buff=0.8)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, row, arrows, resolved, explain, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    shown, correct = angles_for(spec)
    choices, correct_letter = choice_angles_for(spec, shown, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "rotation",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_rot_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "increment_degrees": spec.increment,
        "angles_shown": shown,
        "correct_angle": correct,
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
