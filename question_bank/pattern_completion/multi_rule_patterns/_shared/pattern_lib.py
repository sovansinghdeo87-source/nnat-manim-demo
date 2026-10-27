"""
Shared content engine for Pattern Completion -> Multi-Rule Patterns.

TWO independent attribute cycles run simultaneously on the same
sequence -- e.g. shape cycles every 2 steps while color independently
cycles every 3 steps. Both cycles share the same global step index, so
the combined pattern has period lcm(2, 3) = 6. This is the natural
generalization of Repeating Patterns' single-attribute cycle into two
independent rules the student must track at once.

Five base questions = five attribute pairs, each one period-2 + one
period-3 sub-cycle (so every pair has a genuinely different combined
rhythm, not two coincidentally-matching cycles):

    shape_color  -- shape period 2, color period 3
    shape_fill   -- shape period 3, fill period 2
    color_size   -- color period 2, size period 3
    shape_size   -- shape period 2, size period 3
    fill_color   -- fill period 2, color period 3
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
EXPLAIN_SIZE = 24
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Pattern Completion"
QUESTION_TEXT = "Which figure comes next?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]
SIZE_CYCLE = [
    ("tiny", 0.55), ("small", 0.7), ("medium", 0.9),
    ("large", 1.1), ("extra-large", 1.3), ("huge", 1.5),
]

ATTR_PAIRS: dict[str, tuple[tuple[str, int], tuple[str, int]]] = {
    "shape_color": (("shape", 2), ("color", 3)),
    "shape_fill": (("shape", 3), ("fill", 2)),
    "color_size": (("color", 2), ("size", 3)),
    "shape_size": (("shape", 2), ("size", 3)),
    "fill_color": (("fill", 2), ("color", 3)),
}
ATTRIBUTES = list(ATTR_PAIRS.keys())

DISPLAYED_COUNT_BY_GRADE = {0: 6, 1: 6, 2: 7, 3: 7, 4: 8}
DIFFICULTY_BY_GRADE = {0: 2, 1: 2, 2: 3, 3: 4, 4: 5}  # inherently harder: 2 rules at once


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
    def rule_a(self) -> tuple[str, int]:
        return ATTR_PAIRS[self.attribute][0]

    @property
    def rule_b(self) -> tuple[str, int]:
        return ATTR_PAIRS[self.attribute][1]

    @property
    def displayed_count(self) -> int:
        return DISPLAYED_COUNT_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_mr_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


@dataclass(frozen=True)
class Token:
    shape: str = "circle"
    color: str = INK
    fill: bool = True
    size_scale: float = 1.0

    def label(self, spec: "PatternSpec") -> str:
        active = {spec.rule_a[0], spec.rule_b[0]}
        parts = []
        if "size" in active:
            name = next(n for n, v in SIZE_CYCLE if v == self.size_scale)
            parts.append(name)
        if "color" in active:
            name = next(n for n, hexv in COLOR_CYCLE if hexv == self.color)
            parts.append(name)
        if "fill" in active:
            parts.append("filled" if self.fill else "empty")
        parts.append(self.shape)
        return " ".join(parts)


def _value_for(attr: str, period: int, offset: int, index: int):
    i = (offset + index) % period
    if attr == "shape":
        return SHAPE_CYCLE[i % len(SHAPE_CYCLE)]
    if attr == "color":
        return COLOR_CYCLE[i % len(COLOR_CYCLE)][1]
    if attr == "fill":
        return i == 0
    if attr == "size":
        return SIZE_CYCLE[i % len(SIZE_CYCLE)][1]
    raise ValueError(attr)


def token_at(spec: PatternSpec, combined_index: int) -> Token:
    attr_a, period_a = spec.rule_a
    attr_b, period_b = spec.rule_b
    kwargs = {}
    for attr, period in (spec.rule_a, spec.rule_b):
        value = _value_for(attr, period, spec.palette_offset, combined_index)
        field = "size_scale" if attr == "size" else attr
        kwargs[field] = value
    return Token(**kwargs)


def sequence_for(spec: PatternSpec) -> tuple[list[Token], Token]:
    shown = [token_at(spec, i) for i in range(spec.displayed_count)]
    correct = token_at(spec, spec.displayed_count)
    return shown, correct


def _token_at_deltas(spec: PatternSpec, combined_index: int, delta_a: int, delta_b: int) -> Token:
    """Token where rule A is evaluated `delta_a` steps off and rule B `delta_b` steps off
    from `combined_index` -- independently, so (0, 0) reproduces the true trajectory
    token but any other combo is an "off-trajectory" (wrong on one or both rules) token."""
    attr_a, period_a = spec.rule_a
    attr_b, period_b = spec.rule_b
    kwargs = {}
    for attr, period, delta in ((attr_a, period_a, delta_a), (attr_b, period_b, delta_b)):
        value = _value_for(attr, period, spec.palette_offset, combined_index + delta)
        field = "size_scale" if attr == "size" else attr
        kwargs[field] = value
    return Token(**kwargs)


def distractor_tokens_for(spec: PatternSpec, shown: list[Token], correct: Token) -> list[Token]:
    n = spec.displayed_count

    # Priority order: rule A wrong only, rule B wrong only, both wrong, then a
    # repeat of the last shown item ("didn't progress"), then more off-trajectory
    # combos as filler. Bounded list -- no unbounded search, so this always terminates.
    deltas = [(1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (2, 0), (0, 2), (2, 1), (1, 2), (-1, -1)]
    distractors: list[Token] = []
    for da, db in deltas:
        cand = _token_at_deltas(spec, n, da, db)
        if cand != correct and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    if len(distractors) < 4 and shown[-1] != correct and shown[-1] not in distractors:
        distractors.append(shown[-1])

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, shown: list[Token], correct: Token) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, shown, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _build_shape(token: Token, base_scale: float = 1.0):
    s = 0.55 * token.size_scale * base_scale
    if token.shape == "circle":
        return Circle(radius=s, color=token.color, stroke_width=7,
                       fill_color=token.color, fill_opacity=1 if token.fill else 0)
    if token.shape == "square":
        return Square(side_length=s * 1.8, color=token.color, stroke_width=6,
                       fill_color=token.color, fill_opacity=1 if token.fill else 0)
    if token.shape == "triangle":
        tri = Triangle(color=token.color, stroke_width=6)
        tri.set_fill(token.color, opacity=1 if token.fill else 0)
        return tri.scale(s * 1.55)
    if token.shape == "diamond":
        d = Square(side_length=s * 1.8, color=token.color, stroke_width=6,
                    fill_color=token.color, fill_opacity=1 if token.fill else 0)
        return d.rotate(PI / 4)
    if token.shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                     color=token.color, stroke_width=5,
                     fill_color=token.color, fill_opacity=1 if token.fill else 0)
    if token.shape == "hexagon":
        return RegularPolygon(n=6, color=token.color, stroke_width=6,
                               fill_color=token.color, fill_opacity=1 if token.fill else 0).scale(s * 1.05)
    raise ValueError(token.shape)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    shown, correct = sequence_for(spec)
    mobjs = [_build_shape(t, 1.0) for t in shown] + [_qmark(1.0)]
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

    return row, arrows, mobjs, shown, correct, item_scale


def build_choice_group(spec: PatternSpec, shown: list[Token], correct: Token, base_scale: float = 1.0):
    choices, correct_letter = choice_tokens_for(spec, shown, correct)
    shapes = [_build_shape(t, base_scale) for t in choices]
    group = VGroup(*shapes).arrange(RIGHT, buff=1.1)

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


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    attr_a, period_a = spec.rule_a
    attr_b, period_b = spec.rule_b
    return {
        "intro": QUESTION_TEXT,
        "sequence": f"Two rules at once: {attr_a} and {attr_b} each repeat on their own cycle.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Both rules must line up together.",
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

    row, arrows, _, shown, correct, item_scale = build_sequence_group(spec)
    sequence_group = VGroup(row, arrows)
    sequence_group.move_to(ORIGIN).shift(UP * 0.6)

    choices, _ = build_choice_group(spec, shown, correct, base_scale=item_scale)
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(sequence_group.width, choices.width))
    if _choice_fit < 1.0:
        sequence_group.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(sequence_group, DOWN, buff=1.3)

    _group = VGroup(title, question, sequence_group, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class MultiRuleVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)

        row, arrows, mobjs, shown, correct, item_scale = build_sequence_group(spec)
        sequence_group = VGroup(row, arrows)
        sequence_group.move_to(ORIGIN).shift(UP * 0.6)
        choices, correct_letter = build_choice_group(spec, shown, correct, base_scale=item_scale)
        _choice_fit = min(1.0, (config.frame_width - 1.0) / max(sequence_group.width, choices.width))
        lines = narration_lines(spec, correct_letter)

        with self.voiceover(text=lines["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        with self.voiceover(text=lines["sequence"]) as tracker:
            run_time_each = max(0.2, min(1.0, tracker.duration / max(len(mobjs), 1)))
            self.play(FadeIn(mobjs[0], scale=0.7), run_time=run_time_each)
            for arrow, mobj in zip(arrows, mobjs[1:]):
                self.play(GrowArrow(arrow), FadeIn(mobj, scale=0.7), run_time=run_time_each)
            self.wait(tracker.get_remaining_duration())

        if _choice_fit < 1.0:
            self.play(sequence_group.animate.scale(_choice_fit), run_time=0.3)
            choices.scale(_choice_fit)
        choices.next_to(sequence_group, DOWN, buff=1.3)
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
            "two rules at once",
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
    shown, correct = sequence_for(spec)
    choices, correct_letter = choice_tokens_for(spec, shown, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "multi_rule_patterns",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "rule_a": {"attribute": spec.rule_a[0], "period": spec.rule_a[1]},
        "rule_b": {"attribute": spec.rule_b[0], "period": spec.rule_b[1]},
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_mr_{spec.grade_label}_q{spec.question_number:02d}"
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
