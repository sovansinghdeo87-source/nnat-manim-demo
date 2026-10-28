"""
Shared content engine for Pattern Completion -> Line and Shape
Continuation.

Each sequence item is a small cluster of N identical marks (dots,
ticks, squares, triangles, or stars), and N grows by a constant step
every position: e.g. 1, 2, 3, 4 -> ?. The answer continues the count by
one more step. Mark type is fixed within a question -- only the COUNT
varies -- so this is a counting/quantity-growth task, distinct from the
shape/color/size attribute patterns in the other subskills.
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

MARK_TYPES = ["dot", "tick", "square", "triangle", "star"]
GRADE_LABELS = ["K", "1", "2", "3", "4"]
ATTRIBUTES = MARK_TYPES  # one base question per mark type

STEP_BY_GRADE = {0: 1, 1: 1, 2: 1, 3: 2, 4: 2}
DISPLAYED_COUNT_BY_GRADE = {0: 3, 1: 3, 2: 4, 3: 4, 4: 5}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}


@dataclass(frozen=True)
class PatternSpec:
    grade_rank: int
    question_number: int
    attribute: str  # mark type
    variation_index: int = 0
    palette_offset: int = 0

    @property
    def grade_label(self) -> str:
        return GRADE_LABELS[self.grade_rank]

    @property
    def step(self) -> int:
        return STEP_BY_GRADE[self.grade_rank]

    @property
    def start(self) -> int:
        return 1 + (self.palette_offset % 3)

    @property
    def displayed_count(self) -> int:
        return DISPLAYED_COUNT_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_lsc_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def counts_for(spec: PatternSpec) -> tuple[list[int], int]:
    shown = [spec.start + i * spec.step for i in range(spec.displayed_count)]
    correct = spec.start + spec.displayed_count * spec.step
    return shown, correct


def distractor_counts_for(spec: PatternSpec, shown: list[int], correct: int) -> list[int]:
    step = spec.step
    overshoot = correct + step
    undershoot = shown[-1]
    wrong_step_delta = step + 1 if step == 1 else step - 1
    wrong_step = spec.start + spec.displayed_count * wrong_step_delta
    far_away = max(1, correct - 2 * step - 1)

    hard = spec.grade_rank >= 3
    candidates = [overshoot, undershoot, wrong_step, overshoot + step if hard else far_away]

    used = {correct, *shown}
    distractors: list[int] = []
    for cand in candidates:
        if cand not in used and cand not in distractors and cand >= 1:
            distractors.append(cand)

    salt = 1
    while len(distractors) < 4:
        cand = correct + salt if salt % 2 else max(1, correct - salt)
        salt += 1
        if cand not in used and cand not in distractors and cand >= 1:
            distractors.append(cand)
    return distractors[:4]


def choice_counts_for(spec: PatternSpec, shown: list[int], correct: int) -> tuple[list[int], str]:
    distractors = distractor_counts_for(spec, shown, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _mark(mark_type: str, scale: float = 1.0):
    s = 0.14 * scale
    if mark_type == "dot":
        return Circle(radius=s, color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
    if mark_type == "tick":
        return Line(UP * s * 1.6, DOWN * s * 1.6, color=INK, stroke_width=5 * scale)
    if mark_type == "square":
        return Square(side_length=s * 1.8, color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
    if mark_type == "triangle":
        tri = Triangle(color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
        return tri.scale(s * 1.6)
    if mark_type == "star":
        return Star(n=5, outer_radius=s * 1.3, inner_radius=s * 0.6,
                     color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
    raise ValueError(mark_type)


def _build_cluster(mark_type: str, count: int, item_scale: float = 1.0):
    marks = [_mark(mark_type, item_scale) for _ in range(count)]
    cols = min(4, max(1, count))
    grid = VGroup(*marks).arrange_in_grid(rows=None, cols=cols, buff=0.14 * item_scale)
    box = Square(side_length=1.0, stroke_opacity=0, fill_opacity=0)
    box.scale(max(grid.width, grid.height, 0.6) / 1.0 + 0.1)
    return VGroup(box, grid)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    shown, correct = counts_for(spec)
    clusters = [_build_cluster(spec.attribute, c, 1.0) for c in shown]
    mobjs = clusters + [_qmark(1.0)]
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

    return row, arrows, mobjs, shown, correct, item_scale


def build_choice_group(spec: PatternSpec, shown: list[int], correct: int):
    choices, correct_letter = choice_counts_for(spec, shown, correct)
    clusters = [_build_cluster(spec.attribute, c, 0.75) for c in choices]
    group = VGroup(*clusters).arrange(RIGHT, buff=0.9)

    full = VGroup()
    for letter, cluster in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(cluster, UP, buff=0.3)
        full.add(VGroup(letter_text, cluster))
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


def narration_lines(spec: PatternSpec, correct: int, correct_letter: str) -> dict:
    step_word = "one" if spec.step == 1 else str(spec.step)
    return {
        "intro": QUESTION_TEXT,
        "sequence": f"Each group has {step_word} more than before.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"It keeps growing by {step_word}. Next is {correct} marks.",
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


class LineShapeVideoScene(VoiceoverScene):
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
        lines = narration_lines(spec, correct, correct_letter)

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

        resolved = _build_cluster(spec.attribute, correct, item_scale)
        resolved.move_to(mobjs[-1].get_center())
        _edge = config.frame_width / 2 - 0.3
        if resolved.get_right()[0] > _edge:
            resolved.shift(LEFT * (resolved.get_right()[0] - _edge))
        explain = Text(
            "the count keeps growing",
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
    shown, correct = counts_for(spec)
    choices, correct_letter = choice_counts_for(spec, shown, correct)
    lines = narration_lines(spec, correct, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "line_shape_continuation",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_lsc_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "counts_shown": shown,
        "correct_count": correct,
        "step": spec.step,
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
