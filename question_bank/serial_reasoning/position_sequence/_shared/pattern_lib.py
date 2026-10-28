"""
Shared content engine for Serial Reasoning -> Position Sequence.

Reuses the position-cycle content model from Pattern Completion's
Position and Orientation subskill (a dot cycling through positions in
a frame: left/right, corners clockwise/counter-clockwise, perimeter),
but in the "row of boxed cells" format with only 3 cells shown and the
blank position varying by grade -- not a long arrow-chained sequence
always asking "what's next".
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
TITLE_TEXT = "Serial Reasoning"
QUESTION_TEXT = "Which figure completes the row?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

D = 0.32
POSITION_SETS: dict[str, list[tuple[float, float]]] = {
    "two_lr": [(-D, 0.0), (D, 0.0)],
    "two_tb": [(0.0, D), (0.0, -D)],
    "four_corners_cw": [(-D, D), (D, D), (D, -D), (-D, -D)],
    "four_corners_ccw": [(-D, D), (-D, -D), (D, -D), (D, D)],
    "eight_perimeter_cw": [
        (-D, D), (0.0, D), (D, D), (D, 0.0),
        (D, -D), (0.0, -D), (-D, -D), (-D, 0.0),
    ],
}
ATTRIBUTES = list(POSITION_SETS.keys())
OFF_CYCLE_POSITION = (0.0, 0.0)

BLANK_POS_BY_GRADE = {0: 2, 1: 2, 2: 0, 3: 2, 4: 1}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 3, 3: 3, 4: 4}

Token = tuple


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
    def positions(self) -> list[tuple[float, float]]:
        return POSITION_SETS[self.attribute]

    @property
    def period(self) -> int:
        return len(self.positions)

    @property
    def blank_pos(self) -> int:
        return BLANK_POS_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"sr_pos_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def row_values_for(spec: PatternSpec) -> dict:
    positions = spec.positions
    period = spec.period
    start = spec.palette_offset % period
    cells = [positions[(start + i) % period] for i in range(3)]
    return {"cells": cells, "correct": cells[spec.blank_pos], "positions": positions}


def distractor_tokens_for(spec: PatternSpec, row: dict) -> list[Token]:
    positions = row["positions"]
    correct = row["correct"]
    others = [p for p in positions if p != correct]
    distractors = list(others)
    used = {*positions}
    if len(distractors) < 4:
        distractors.append(OFF_CYCLE_POSITION)
        used.add(OFF_CYCLE_POSITION)
    salt = 0.08
    while len(distractors) < 4:
        cand = (OFF_CYCLE_POSITION[0] + salt, OFF_CYCLE_POSITION[1] - salt)
        salt += 0.08
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, row: dict) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, row)
    choices = distractors + [row["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(row["correct"])]
    return choices, correct_letter


def _build_frame_dot(pos: Token, scale: float = 1.0):
    frame = Square(side_length=0.85 * scale, color=INK, stroke_width=5, fill_opacity=0)
    dot = Circle(radius=0.1 * scale, color=INK, stroke_width=0, fill_color=ACCENT, fill_opacity=1)
    dot.move_to(frame.get_center() + RIGHT * pos[0] * scale * (0.85 / (2 * D)) + UP * pos[1] * scale * (0.85 / (2 * D)))
    return VGroup(frame, dot)


def _build_cell(pos: Optional[Token], scale: float = 1.0, is_blank: bool = False):
    if is_blank:
        box = Square(side_length=0.85 * scale, color=INK, stroke_width=5, fill_opacity=0)
        content = Text("?", font_size=int(44 * scale), color=ACCENT, weight=BOLD)
        content.move_to(box.get_center())
        return VGroup(box, content)
    return _build_frame_dot(pos, scale)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_row(spec: PatternSpec, row: dict, scale: float = 1.0):
    cells = [_build_cell(row["cells"][i], scale, i == spec.blank_pos) for i in range(3)]
    return VGroup(*cells).arrange(RIGHT, buff=0.45 * scale)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=0.55):
    group = VGroup(*[_build_frame_dot(c, 0.75) for c in choices]).arrange(RIGHT, buff=buff)
    full = VGroup()
    for letter, mobj in zip(labels, group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(mobj, UP, buff=0.3)
        full.add(VGroup(letter_text, mobj))
    full.move_to(ORIGIN)
    _max_w = min(12, config.frame_width - 1.0)
    if full.width > _max_w:
        full.scale(_max_w / full.width)
    return full


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.25, stroke_width=6, corner_radius=0.1)


_POS_WORD = {0: "first", 1: "middle", 2: "last"}
_DIRECTION_PHRASE = {
    "two_lr": "hops between left and right",
    "two_tb": "hops between top and bottom",
    "four_corners_cw": "moves clockwise around the corners",
    "four_corners_ccw": "moves counter-clockwise around the corners",
    "eight_perimeter_cw": "moves clockwise around the edge",
}


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    pos_word = _POS_WORD[spec.blank_pos]
    trend = _DIRECTION_PHRASE[spec.attribute]
    return {
        "intro": QUESTION_TEXT,
        "row": f"Watch the dot -- it {trend}. The {pos_word} box is missing.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"The dot {trend} the whole way through.",
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

    row = row_values_for(spec)
    row_group = build_row(spec, row)
    row_group.next_to(question, DOWN, buff=0.7)

    choices, _ = choice_tokens_for(spec, row)
    choice_group = build_choice_row(choices)
    choice_group.next_to(row_group, DOWN, buff=2.8)

    _group = VGroup(title, question, row_group, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class PositionSequenceVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.55)

        with self.voiceover(text=narration_lines(spec, "")["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        row = row_values_for(spec)
        row_group = build_row(spec, row)
        row_group.next_to(question, DOWN, buff=2.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["row"]) as tracker:
            self.play(FadeIn(row_group, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        choices, correct_letter = choice_tokens_for(spec, row)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(row_group, DOWN, buff=2.8)

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

        blank_cell = row_group[spec.blank_pos]
        resolved = _build_frame_dot(row["correct"], 1.0).move_to(blank_cell.get_center())
        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(blank_cell), FadeIn(resolved, scale=0.6), run_time=0.8)
            blank_cell.set_opacity(0)
            self.play(FadeOut(choice_group), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(row_group, DOWN, buff=2.8)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, row_group, resolved, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    row = row_values_for(spec)
    choices, correct_letter = choice_tokens_for(spec, row)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "serial_reasoning",
        "skill": "position_sequence",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "blank_position": spec.blank_pos,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sr_pos_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["row"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
