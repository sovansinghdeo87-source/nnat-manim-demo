"""
Shared content engine for Reasoning by Analogy -> Movement or Position
Change.

Two-pair analogy format: first pair (A -> B) demonstrates "move the
dot by a fixed (dcol, drow) step within a 3x3 grid, wrapping around
the edges"; apply the same movement to a second pair's starting
position (C -> ?). A and C start at different grid cells so the
question can't be answered by copying B.
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
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Visual Analogy"
QUESTION_TEXT = "Complete the analogy."

GRADE_LABELS = ["K", "1", "2", "3", "4"]

MOVE_BY_ATTR = {
    "right_1": (1, 0), "down_1": (0, 1), "diag_1": (1, 1),
    "antidiag_1": (1, -1), "down_2": (0, 2),
}
ATTRIBUTES = list(MOVE_BY_ATTR.keys())
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}

GRID_STEP = 0.35


def _idx_to_colrow(idx: int) -> tuple[int, int]:
    return idx % 3, idx // 3


def _move(colrow: tuple[int, int], delta: tuple[int, int]) -> tuple[int, int]:
    col, row = colrow
    dcol, drow = delta
    return (col + dcol) % 3, (row + drow) % 3


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
    def delta(self) -> tuple[int, int]:
        return MOVE_BY_ATTR[self.attribute]

    @property
    def pos_a(self) -> tuple[int, int]:
        return _idx_to_colrow(self.palette_offset % 9)

    @property
    def pos_c(self) -> tuple[int, int]:
        return _idx_to_colrow((self.palette_offset + 4) % 9)

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_mov_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def positions_for(spec: PatternSpec) -> dict:
    pos_b = _move(spec.pos_a, spec.delta)
    correct = _move(spec.pos_c, spec.delta)
    return {"a": spec.pos_a, "b": pos_b, "c": spec.pos_c, "correct": correct}


def distractor_positions_for(spec: PatternSpec, positions: dict) -> list[tuple[int, int]]:
    same_as_c = positions["c"]
    same_as_b = positions["b"]
    dcol, drow = spec.delta
    wrong_direction = _move(positions["c"], (-dcol, -drow))
    wrong_axis = _move(positions["c"], (drow, dcol))

    candidates = [same_as_c, same_as_b, wrong_direction, wrong_axis]
    used = {positions["correct"]}
    distractors: list[tuple[int, int]] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    # Bounded fallback: every (dcol, drow) in the 3x3 grid, fixed list so this
    # always terminates (a previous version used an open-ended salt-based
    # search over only 3 distinct deltas, which could spin forever if all 3
    # were already used -- exactly the Multi-Rule Patterns bug, recurring).
    all_deltas = [(dc, dr) for dc in range(3) for dr in range(3)]
    i = 0
    while len(distractors) < 4 and i < len(all_deltas):
        cand = _move(positions["correct"], all_deltas[i])
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_positions_for(spec: PatternSpec, positions: dict) -> tuple[list[tuple[int, int]], str]:
    distractors = distractor_positions_for(spec, positions)
    choices = distractors + [positions["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(positions["correct"])]
    return choices, correct_letter


def _build_frame_dot(colrow: tuple[int, int], scale: float = 1.0):
    frame = Square(side_length=1.0 * scale, color=INK, stroke_width=5, fill_opacity=0)
    dot = Circle(radius=0.11 * scale, color=INK, stroke_width=0, fill_color=ACCENT, fill_opacity=1)
    col, row = colrow
    x = (col - 1) * GRID_STEP * scale
    y = (1 - row) * GRID_STEP * scale
    dot.move_to(frame.get_center() + RIGHT * x + UP * y)
    return VGroup(frame, dot)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_pair(left_mobj, right_mobj, buff=0.6):
    arrow = Arrow(LEFT * 0.9, RIGHT * 0.9, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.3)
    return VGroup(left_mobj, arrow, right_mobj).arrange(RIGHT, buff=buff)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=0.6):
    group = VGroup(*choices).arrange(RIGHT, buff=buff)
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
        "first_pair": "In the first pair, the dot moves to a new spot in the box.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "The same rule applies: the dot moves the same way again.",
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

    positions = positions_for(spec)
    pair1 = build_pair(_build_frame_dot(positions["a"]), _build_frame_dot(positions["b"]))
    pair2 = build_pair(_build_frame_dot(positions["c"]), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.5)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_positions, _ = choice_positions_for(spec, positions)
    choices = build_choice_row([_build_frame_dot(p, 0.8) for p in choice_positions])
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(pairs.width, choices.width))
    if _choice_fit < 1.0:
        pairs.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(pairs, DOWN, buff=0.9)

    _group = VGroup(title, question, pairs, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class AnalogyMovementVideoScene(VoiceoverScene):
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

        positions = positions_for(spec)
        frame_a = _build_frame_dot(positions["a"])
        frame_b = _build_frame_dot(positions["b"])
        pair1 = build_pair(frame_a, frame_b)
        pair1.move_to(ORIGIN).shift(UP * 1.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(frame_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(frame_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        frame_c = _build_frame_dot(positions["c"])
        qmark = _qmark()
        pair2 = build_pair(frame_c, qmark)
        pair2.move_to(ORIGIN).shift(DOWN * 0.6)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_positions, correct_letter = choice_positions_for(spec, positions)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_build_frame_dot(p, 0.8) for p in choice_positions])
        _choice_fit = min(1.0, (config.frame_width - 1.0) / max(VGroup(pair1, pair2).width, choices.width))
        if _choice_fit < 1.0:
            self.play(pair1.animate.scale(_choice_fit), pair2.animate.scale(_choice_fit), run_time=0.3)
            choices.scale(_choice_fit)
        choices.next_to(VGroup(pair1, pair2), DOWN, buff=0.9)

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

        resolved = _build_frame_dot(positions["correct"]).move_to(qmark.get_center())
        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(qmark, scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.8)
            qmark.set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(VGroup(pair1, pair2), DOWN, buff=0.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, pair1, pair2, resolved, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    positions = positions_for(spec)
    choice_positions, correct_letter = choice_positions_for(spec, positions)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "reasoning_by_analogy",
        "skill": "movement_position",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_mov_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "delta": spec.delta,
        "positions": positions,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
