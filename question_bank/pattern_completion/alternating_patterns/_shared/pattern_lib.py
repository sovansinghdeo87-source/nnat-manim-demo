"""
Shared content engine for Pattern Completion -> Alternating Patterns.

Alternating Patterns is the "pure ABAB" special case: the repeating unit
is always exactly 2 items (unlike the general Repeating Patterns
subskill, where period grows with grade). Difficulty instead scales via
how many cycles are shown and how close the distractors are.

Adapted from ../../repeating_patterns/_shared/pattern_lib.py -- same
proven rendering/animation skeleton (actual-width measurement, moving
row+arrows as one rigid group), different difficulty model.
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

SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]

COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]

SIZE_CYCLE = [
    ("tiny", 0.55), ("small", 0.7), ("medium", 0.9),
    ("large", 1.1), ("extra-large", 1.3), ("huge", 1.5),
]

GRADE_LABELS = ["K", "1", "2", "3", "4"]
ATTRIBUTES = ["shape", "fill", "color", "size", "combo"]

# Alternating Patterns is always period 2; difficulty comes from how many
# cycles are shown and (for grade >= 3) a tougher distractor mix.
CYCLES_SHOWN_BY_GRADE = {0: 2, 1: 2, 2: 3, 3: 3, 4: 4}
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
    def period(self) -> int:
        return 2

    @property
    def displayed_count(self) -> int:
        return CYCLES_SHOWN_BY_GRADE[self.grade_rank] * 2

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_ap_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


@dataclass(frozen=True)
class Token:
    shape: str
    color: str = INK
    fill: bool = True
    size_scale: float = 1.0

    def label(self, attribute: str) -> str:
        shape_name = self.shape
        if attribute == "fill":
            return f"{'filled' if self.fill else 'empty'} {shape_name}"
        if attribute == "color":
            name = next(n for n, hexv in COLOR_CYCLE if hexv == self.color)
            return f"{name} {shape_name}"
        if attribute == "size":
            name = next(n for n, v in SIZE_CYCLE if v == self.size_scale)
            return f"{name} {shape_name}"
        if attribute == "combo":
            name = next(n for n, hexv in COLOR_CYCLE if hexv == self.color)
            return f"{name} {shape_name}"
        return shape_name


def unit_tokens_for(spec: PatternSpec) -> list[Token]:
    off = spec.palette_offset
    if spec.attribute == "shape":
        return [Token(shape=SHAPE_CYCLE[off % len(SHAPE_CYCLE)]),
                Token(shape=SHAPE_CYCLE[(off + 1) % len(SHAPE_CYCLE)])]
    if spec.attribute == "fill":
        shape = SHAPE_CYCLE[off % len(SHAPE_CYCLE)]
        return [Token(shape=shape, fill=True), Token(shape=shape, fill=False)]
    if spec.attribute == "color":
        shape = SHAPE_CYCLE[off % len(SHAPE_CYCLE)]
        return [Token(shape=shape, color=COLOR_CYCLE[off % len(COLOR_CYCLE)][1]),
                Token(shape=shape, color=COLOR_CYCLE[(off + 1) % len(COLOR_CYCLE)][1])]
    if spec.attribute == "size":
        shape = SHAPE_CYCLE[off % len(SHAPE_CYCLE)]
        return [Token(shape=shape, size_scale=SIZE_CYCLE[off % len(SIZE_CYCLE)][1]),
                Token(shape=shape, size_scale=SIZE_CYCLE[(off + 1) % len(SIZE_CYCLE)][1])]
    if spec.attribute == "combo":
        return [Token(shape=SHAPE_CYCLE[off % len(SHAPE_CYCLE)],
                       color=COLOR_CYCLE[off % len(COLOR_CYCLE)][1]),
                Token(shape=SHAPE_CYCLE[(off + 1) % len(SHAPE_CYCLE)],
                       color=COLOR_CYCLE[(off + 1) % len(COLOR_CYCLE)][1])]
    raise ValueError(spec.attribute)


def sequence_for(spec: PatternSpec) -> tuple[list[Token], Token, list[Token]]:
    unit = unit_tokens_for(spec)
    seq = [unit[i % 2] for i in range(spec.displayed_count)]
    correct = unit[spec.displayed_count % 2]
    return seq, correct, unit


def _unrelated_token(spec: PatternSpec, unit: list[Token], salt: int) -> Token:
    idx = 2 + salt
    shape = SHAPE_CYCLE[(spec.palette_offset + idx) % len(SHAPE_CYCLE)]
    if spec.attribute == "shape":
        return Token(shape=shape)
    if spec.attribute == "fill":
        return Token(shape=shape, fill=unit[0].fill)
    if spec.attribute == "color":
        color = COLOR_CYCLE[(spec.palette_offset + idx) % len(COLOR_CYCLE)][1]
        return Token(shape=unit[0].shape, color=color)
    if spec.attribute == "size":
        size = SIZE_CYCLE[(spec.palette_offset + idx) % len(SIZE_CYCLE)][1]
        return Token(shape=unit[0].shape, size_scale=size)
    if spec.attribute == "combo":
        color = COLOR_CYCLE[(spec.palette_offset + idx) % len(COLOR_CYCLE)][1]
        return Token(shape=shape, color=color)
    raise ValueError(spec.attribute)


def distractor_tokens_for(spec: PatternSpec, unit: list[Token], correct: Token) -> list[Token]:
    others = [t for t in unit if t != correct]
    distractors = list(others)
    used = set(unit)
    salt = 0
    max_attempts = 200
    while len(distractors) < 4 and max_attempts > 0:
        candidate = _unrelated_token(spec, unit, salt)
        salt += 1
        max_attempts -= 1
        if candidate in used:
            continue
        distractors.append(candidate)
        used.add(candidate)
    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, unit: list[Token], correct: Token) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, unit, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _build_shape(token: Token, base_scale: float = 1.0):
    s = 0.55 * token.size_scale * base_scale
    if token.shape == "circle":
        return Circle(radius=s, color=token.color, stroke_width=8,
                       fill_color=token.color, fill_opacity=1 if token.fill else 0)
    if token.shape == "square":
        return Square(side_length=s * 1.8, color=token.color, stroke_width=7,
                       fill_color=token.color, fill_opacity=1 if token.fill else 0)
    if token.shape == "triangle":
        tri = Triangle(color=token.color, stroke_width=7)
        tri.set_fill(token.color, opacity=1 if token.fill else 0)
        return tri.scale(s * 1.55)
    if token.shape == "diamond":
        d = Square(side_length=s * 1.8, color=token.color, stroke_width=7,
                    fill_color=token.color, fill_opacity=1 if token.fill else 0)
        return d.rotate(PI / 4)
    if token.shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                     color=token.color, stroke_width=6,
                     fill_color=token.color, fill_opacity=1 if token.fill else 0)
    if token.shape == "hexagon":
        return RegularPolygon(n=6, color=token.color, stroke_width=7,
                               fill_color=token.color, fill_opacity=1 if token.fill else 0).scale(s * 1.05)
    raise ValueError(token.shape)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    seq, correct, unit = sequence_for(spec)
    mobjs = [_build_shape(t, 1.0) for t in seq] + [_qmark(1.0)]
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

    return row, arrows, mobjs, seq, correct, unit, item_scale


def build_choice_group(spec: PatternSpec, unit: list[Token], correct: Token, base_scale: float = 1.0):
    choices, correct_letter = choice_tokens_for(spec, unit, correct)
    shapes = [_build_shape(t, base_scale) for t in choices]
    group = VGroup(*shapes).arrange(RIGHT, buff=1.3)

    full = VGroup()
    for letter, shape in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(shape, UP, buff=0.35)
        full.add(VGroup(letter_text, shape))
    full.move_to(ORIGIN)
    return full, correct_letter


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.28, stroke_width=6, corner_radius=0.12)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def narration_lines(spec: PatternSpec, unit: list[Token], correct: Token, correct_letter: str) -> dict:
    a_label, b_label = unit[0].label(spec.attribute), unit[1].label(spec.attribute)
    return {
        "intro": QUESTION_TEXT,
        "sequence": f"It alternates: {a_label}, then {b_label}.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"It keeps swapping. Next is the {correct.label(spec.attribute)}.",
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

    choices, _ = build_choice_group(spec, unit, correct, base_scale=item_scale)
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(sequence_group.width, choices.width))
    if _choice_fit < 1.0:
        sequence_group.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(sequence_group, DOWN, buff=2.8)

    _group = VGroup(title, question, sequence_group, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)
    scene.choice_regions = {letter: _group[-1][i] for i, letter in enumerate("ABCDE")}


class AlternatingPatternVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.55)

        row, arrows, mobjs, seq, correct, unit, item_scale = build_sequence_group(spec)
        sequence_group = VGroup(row, arrows)
        sequence_group.next_to(question, DOWN, buff=2.4)
        choices, correct_letter = build_choice_group(spec, unit, correct, base_scale=item_scale)
        _choice_fit = min(1.0, (config.frame_width - 1.0) / max(sequence_group.width, choices.width))
        lines = narration_lines(spec, unit, correct, correct_letter)

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

        if _choice_fit < 1.0:
            self.play(sequence_group.animate.scale(_choice_fit), run_time=0.3)
            choices.scale(_choice_fit)
        choices.next_to(sequence_group, DOWN, buff=2.8)
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

        resolved = _build_shape(correct, item_scale * _choice_fit)
        resolved.move_to(mobjs[-1].get_center())
        explain = Text(
            "alternates back and forth",
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
    _, correct, unit = sequence_for(spec)
    choices, correct_letter = choice_tokens_for(spec, unit, correct)
    lines = narration_lines(spec, unit, correct, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "alternating_patterns",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "period": spec.period,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_ap_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "unit_pattern": [t.label(spec.attribute) for t in unit],
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
