"""
Shared content engine for Pattern Completion -> Position and Orientation.

Each sequence item is a small square frame with a dot at one position
inside it. The dot cycles through a fixed set of positions (left/right,
top/bottom, around the 4 corners, or around all 8 perimeter spots),
clockwise or counter-clockwise, and the answer continues that cycle.
This is the same cyclic math as Repeating Patterns, but the "token" is
a position-in-a-frame instead of a shape attribute.

Five base questions = five position cycles:
    two_lr              -- left <-> right (period 2)
    two_tb              -- top <-> bottom (period 2)
    four_corners_cw      -- 4 corners, clockwise (period 4)
    four_corners_ccw     -- 4 corners, counter-clockwise (period 4)
    eight_perimeter_cw   -- all 8 perimeter spots, clockwise (period 8)
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

# Target roughly this many total items shown, regardless of period --
# showing 3 full cycles of an 8-position loop (24 items) would be
# illegible, so cycles-shown scales DOWN as period grows.
TARGET_ITEMS_BY_GRADE = {0: 4, 1: 4, 2: 6, 3: 6, 4: 8}
DIFFICULTY_BY_GRADE = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4}


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
    def displayed_count(self) -> int:
        period = self.period
        target = TARGET_ITEMS_BY_GRADE[self.grade_rank]
        cycles = max(1, round(target / period))
        return period * cycles

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_po_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


Token = tuple  # a position is just an (x, y) tuple -- already hashable/comparable


def sequence_for(spec: PatternSpec) -> tuple[list[Token], Token, list[Token]]:
    positions = spec.positions
    period = spec.period
    start = spec.palette_offset % period
    shown = [positions[(start + i) % period] for i in range(spec.displayed_count)]
    correct = positions[(start + spec.displayed_count) % period]
    return shown, correct, positions


def distractor_tokens_for(spec: PatternSpec, positions: list[Token], correct: Token, shown: list[Token]) -> list[Token]:
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


def choice_tokens_for(spec: PatternSpec, positions: list[Token], correct: Token, shown: list[Token]) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, positions, correct, shown)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _build_frame_dot(pos: Token, scale: float = 1.0):
    frame = Square(side_length=0.9 * scale, color=INK, stroke_width=5, fill_opacity=0)
    dot = Circle(radius=0.11 * scale, color=INK, stroke_width=0, fill_color=ACCENT, fill_opacity=1)
    dot.move_to(frame.get_center() + RIGHT * pos[0] * scale * (0.9 / (2 * D)) + UP * pos[1] * scale * (0.9 / (2 * D)))
    return VGroup(frame, dot)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    shown, correct, positions = sequence_for(spec)
    mobjs = [_build_frame_dot(p, 1.0) for p in shown] + [_qmark(1.0)]
    row = VGroup(*mobjs).arrange(RIGHT, buff=0.55)

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

    return row, arrows, mobjs, shown, correct, positions, item_scale


def build_choice_group(spec: PatternSpec, positions: list[Token], correct: Token, shown: list[Token]):
    choices, correct_letter = choice_tokens_for(spec, positions, correct, shown)
    frames = [_build_frame_dot(p, 0.75) for p in choices]
    group = VGroup(*frames).arrange(RIGHT, buff=0.9)

    full = VGroup()
    for letter, frame in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(frame, UP, buff=0.3)
        full.add(VGroup(letter_text, frame))
    full.move_to(ORIGIN)
    max_width = min(MAX_SEQUENCE_WIDTH, config.frame_width - 1.0)
    if full.width > max_width:
        full.scale(max_width / full.width)
    return full, correct_letter


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.28, stroke_width=6, corner_radius=0.12)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


_DIRECTION_PHRASES = {
    "two_lr": "hops back and forth between left and right",
    "two_tb": "hops back and forth between top and bottom",
    "four_corners_cw": "moves clockwise around the four corners",
    "four_corners_ccw": "moves counter-clockwise around the four corners",
    "eight_perimeter_cw": "moves clockwise around the edge",
}


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    trend = _DIRECTION_PHRASES[spec.attribute]
    return {
        "intro": QUESTION_TEXT,
        "sequence": f"Watch the dot. It {trend}, step by step.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "One more step the same way.",
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

    row, arrows, _, shown, correct, positions, item_scale = build_sequence_group(spec)
    sequence_group = VGroup(row, arrows)
    sequence_group.move_to(ORIGIN).shift(UP * 0.6)

    choices, _ = build_choice_group(spec, positions, correct, shown)
    choices.next_to(sequence_group, DOWN, buff=1.3)

    _group = VGroup(title, question, sequence_group, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class PositionOrientationVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)

        row, arrows, mobjs, shown, correct, positions, item_scale = build_sequence_group(spec)
        sequence_group = VGroup(row, arrows)
        sequence_group.move_to(ORIGIN).shift(UP * 0.6)
        choices, correct_letter = build_choice_group(spec, positions, correct, shown)
        choices.next_to(sequence_group, DOWN, buff=1.3)
        lines = narration_lines(spec, correct_letter)

        with self.voiceover(text=lines["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        with self.voiceover(text=lines["sequence"]) as tracker:
            run_time_each = max(0.25, min(0.5, tracker.duration / max(len(mobjs), 1)))
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

        resolved = _build_frame_dot(correct, item_scale)
        resolved.move_to(mobjs[-1].get_center())
        explain = Text(
            "keeps moving the same way",
            font_size=EXPLAIN_SIZE, color=INK,
        ).next_to(sequence_group, DOWN, buff=0.9)

        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(mobjs[-1], scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.6)
            mobjs[-1].set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.play(Write(explain), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(explain, DOWN, buff=0.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, row, arrows, resolved, explain, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    shown, correct, positions = sequence_for(spec)
    choices, correct_letter = choice_tokens_for(spec, positions, correct, shown)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "position_orientation",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "period": spec.period,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_po_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
