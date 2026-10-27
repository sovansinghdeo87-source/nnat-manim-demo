"""
Shared content engine for Pattern Completion -> Overlapping Shapes.

Two fixed, overlapping shapes alternate which one is drawn on top
(z-order) every step -- period 2, like Alternating Patterns. Shape
identity, size, color, and overlap amount all stay constant; only the
front/back order changes. Z-order in Manim is draw-order within a
VGroup: whichever shape is added last renders on top.

Five base questions = five shape pairs (one per attribute).
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

SHAPE_PAIRS = {
    "circle_square": ("circle", "square"),
    "triangle_diamond": ("triangle", "diamond"),
    "star_hexagon": ("star", "hexagon"),
    "circle_triangle": ("circle", "triangle"),
    "square_star": ("square", "star"),
}
ATTRIBUTES = list(SHAPE_PAIRS.keys())
THIRD_SHAPE_FOR = {  # used only for the "swapped shape" distractor
    "circle_square": "star", "triangle_diamond": "circle",
    "star_hexagon": "triangle", "circle_triangle": "square",
    "square_star": "diamond",
}

COLOR_PAIRS = [
    ("#E4572E", "#3B2F5B"), ("#0D9488", "#7C3AED"),
    ("#F59E0B", "#1E3A8A"), ("#EC4899", "#1A1A2E"),
]

CYCLES_SHOWN_BY_GRADE = {0: 2, 1: 2, 2: 3, 3: 3, 4: 4}
DIFFICULTY_BY_GRADE = {0: 1, 1: 1, 2: 2, 3: 3, 4: 4}

NORMAL_OFFSET = 0.22
TIGHT_OFFSET = 0.08
LOOSE_OFFSET = 0.42  # effectively "no overlap"


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
    def shapes(self) -> tuple[str, str]:
        return SHAPE_PAIRS[self.attribute]

    @property
    def colors(self) -> tuple[str, str]:
        return COLOR_PAIRS[self.palette_offset % len(COLOR_PAIRS)]

    @property
    def displayed_count(self) -> int:
        return CYCLES_SHOWN_BY_GRADE[self.grade_rank] * 2

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_ov_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


@dataclass(frozen=True)
class Token:
    front: str  # "A" or "B"
    variant: str = "normal"  # normal | no_overlap | swapped | tight


def unit_tokens_for(spec: PatternSpec) -> list[Token]:
    start_b_front = bool(spec.palette_offset % 2)
    a = Token("B" if start_b_front else "A")
    b = Token("A" if start_b_front else "B")
    return [a, b]


def sequence_for(spec: PatternSpec) -> tuple[list[Token], Token, list[Token]]:
    unit = unit_tokens_for(spec)
    seq = [unit[i % 2] for i in range(spec.displayed_count)]
    correct = unit[spec.displayed_count % 2]
    return seq, correct, unit


def distractor_tokens_for(spec: PatternSpec, unit: list[Token], correct: Token) -> list[Token]:
    other = next(t for t in unit if t != correct)
    candidates = [
        other,
        Token(correct.front, "no_overlap"),
        Token(correct.front, "swapped"),
        Token(correct.front, "tight"),
    ]
    used = {correct, *unit}
    distractors: list[Token] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    i = 0
    fallback = [Token(other.front, "no_overlap"), Token(other.front, "swapped"), Token(other.front, "tight")]
    while len(distractors) < 4 and i < len(fallback):
        cand = fallback[i]
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, unit: list[Token], correct: Token) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, unit, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _plain_shape(shape: str, color: str, s: float = 0.5):
    if shape == "circle":
        return Circle(radius=s, color=color, stroke_width=5, fill_color=color, fill_opacity=1)
    if shape == "square":
        return Square(side_length=s * 1.7, color=color, stroke_width=5, fill_color=color, fill_opacity=1)
    if shape == "triangle":
        tri = Triangle(color=color, stroke_width=5, fill_color=color, fill_opacity=1)
        return tri.scale(s * 1.5)
    if shape == "diamond":
        d = Square(side_length=s * 1.7, color=color, stroke_width=5, fill_color=color, fill_opacity=1)
        return d.rotate(PI / 4)
    if shape == "star":
        return Star(n=5, outer_radius=s * 1.05, inner_radius=s * 0.48,
                     color=color, stroke_width=5, fill_color=color, fill_opacity=1)
    if shape == "hexagon":
        return RegularPolygon(n=6, color=color, stroke_width=5, fill_color=color, fill_opacity=1).scale(s)
    raise ValueError(shape)


def _build_pair(spec: PatternSpec, token: Token, scale: float = 1.0):
    shape_a, shape_b = spec.shapes
    color_a, color_b = spec.colors
    if token.variant == "swapped":
        shape_b = THIRD_SHAPE_FOR[spec.attribute]

    offset = {"normal": NORMAL_OFFSET, "no_overlap": LOOSE_OFFSET, "tight": TIGHT_OFFSET}[
        token.variant if token.variant != "swapped" else "normal"
    ] * scale

    mob_a = _plain_shape(shape_a, color_a, 0.5 * scale).move_to(LEFT * offset)
    mob_b = _plain_shape(shape_b, color_b, 0.5 * scale).move_to(RIGHT * offset)

    if token.front == "A":
        return VGroup(mob_b, mob_a)
    return VGroup(mob_a, mob_b)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    seq, correct, unit = sequence_for(spec)
    mobjs = [_build_pair(spec, t, 1.0) for t in seq] + [_qmark(1.0)]
    row = VGroup(*mobjs).arrange(RIGHT, buff=0.6)

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

    return row, arrows, mobjs, seq, correct, unit, item_scale


def build_choice_group(spec: PatternSpec, unit: list[Token], correct: Token):
    choices, correct_letter = choice_tokens_for(spec, unit, correct)
    pairs = [_build_pair(spec, t, 0.75) for t in choices]
    group = VGroup(*pairs).arrange(RIGHT, buff=1.0)

    full = VGroup()
    for letter, pair in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(pair, UP, buff=0.35)
        full.add(VGroup(letter_text, pair))
    full.move_to(ORIGIN)
    _max_w = min(12, config.frame_width - 1.0)
    if full.width > _max_w:
        full.scale(_max_w / full.width)
    return full, correct_letter


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.3, stroke_width=6, corner_radius=0.12)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    shape_a, shape_b = spec.shapes
    return {
        "intro": QUESTION_TEXT,
        "sequence": f"The {shape_a} and {shape_b} take turns being in front.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "It's the other one's turn to be in front.",
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

    row, arrows, _, seq, correct, unit, item_scale = build_sequence_group(spec)
    sequence_group = VGroup(row, arrows)
    sequence_group.move_to(ORIGIN).shift(UP * 0.6)

    choices, _ = build_choice_group(spec, unit, correct)
    choices.next_to(sequence_group, DOWN, buff=1.3)

    _group = VGroup(title, question, sequence_group, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class OverlappingShapesVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)

        row, arrows, mobjs, seq, correct, unit, item_scale = build_sequence_group(spec)
        sequence_group = VGroup(row, arrows)
        sequence_group.move_to(ORIGIN).shift(UP * 0.6)
        choices, correct_letter = build_choice_group(spec, unit, correct)
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

        resolved = _build_pair(spec, correct, item_scale)
        resolved.move_to(mobjs[-1].get_center())
        explain = Text(
            "they keep swapping places",
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
    seq, correct, unit = sequence_for(spec)
    choices, correct_letter = choice_tokens_for(spec, unit, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "overlapping_shapes",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_ov_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "shapes": spec.shapes,
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
