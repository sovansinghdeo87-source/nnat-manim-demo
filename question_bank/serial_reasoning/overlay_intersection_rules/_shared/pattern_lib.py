"""
Shared content engine for Serial Reasoning -> Overlay/Intersection Rules.

Each cell in a 3x3 grid shows TWO overlapping shapes: a larger "back"
shape and a smaller, shifted "front" shape drawn on top of it with
partial opacity so the overlap region is visibly blended (a literal
overlay). The back shape follows a rule down each ROW; the front shape
follows a different rule down each COLUMN (or vice versa for the
"_rev" variant) -- the same "independent row/column attribute" idea as
2x2/3x3 Matrices, but here both attributes are visually layered into
one cell instead of being separate cells, so the reasoning skill is
specifically about pulling two independent rules out of one combined
image.

Natural distractors (all genuinely plausible mistakes): swapping the
back/front roles, copying the back shape from the wrong row, copying
the front shape from the wrong column, or getting both wrong.
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
FRONT_COLOR = "#F59E0B"
CORRECT = "#22C55E"
BG = WHITE

TITLE_SIZE = 40
QUESTION_SIZE = 28
CHOICE_LETTER_SIZE = 24
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Serial Reasoning"
QUESTION_TEXT = "Which two overlapping shapes complete the matrix?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]
SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]
SIZE_LEVELS = [0.7, 0.9, 1.1, 1.3]

ATTRIBUTES = ["shape_overlay", "color_overlay", "size_overlay", "combo_overlay", "shape_overlay_rev"]
BLANK_BY_GRADE = {0: 8, 1: 8, 2: 6, 3: 2, 4: 4}
DIFFICULTY_BY_GRADE = {0: 2, 1: 3, 2: 3, 3: 4, 4: 5}

FRONT_DRAW_SCALE = 0.72
FRONT_SHIFT = RIGHT * 0.22 + DOWN * 0.22


@dataclass(frozen=True)
class Token:
    shape: str = "circle"
    color: str = INK
    size_scale: float = 1.0


@dataclass(frozen=True)
class OverlayToken:
    back: Token
    front: Token


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
    def reverse(self) -> bool:
        return self.attribute.endswith("_rev")

    @property
    def base_attribute(self) -> str:
        return self.attribute.replace("_overlay_rev", "").replace("_overlay", "")

    @property
    def blank_index(self) -> int:
        return BLANK_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"sr_ovl_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def _value_for_role(spec: PatternSpec, idx: int, role: str) -> Token:
    off = spec.palette_offset
    base = spec.base_attribute
    is_front = role == "front"
    if base == "shape":
        shape = SHAPE_CYCLE[(idx + off + (3 if is_front else 0)) % len(SHAPE_CYCLE)]
        color = FRONT_COLOR if is_front else ACCENT
        return Token(shape=shape, color=color)
    if base == "color":
        shape = "square" if is_front else "circle"
        color = COLOR_CYCLE[(idx + off + (3 if is_front else 0)) % len(COLOR_CYCLE)][1]
        return Token(shape=shape, color=color)
    if base == "size":
        shape = "square" if is_front else "circle"
        color = FRONT_COLOR if is_front else ACCENT
        size = SIZE_LEVELS[(idx + off + (2 if is_front else 0)) % len(SIZE_LEVELS)]
        return Token(shape=shape, color=color, size_scale=size)
    if base == "combo":
        shape = SHAPE_CYCLE[(idx + off + (3 if is_front else 0)) % len(SHAPE_CYCLE)]
        color = COLOR_CYCLE[(idx + off + (4 if is_front else 0)) % len(COLOR_CYCLE)][1]
        return Token(shape=shape, color=color)
    raise ValueError(base)


def _axes(spec: PatternSpec, row: int, col: int) -> tuple[int, int]:
    return (col, row) if spec.reverse else (row, col)


def cell_at(spec: PatternSpec, row: int, col: int) -> OverlayToken:
    back_axis, front_axis = _axes(spec, row, col)
    return OverlayToken(
        back=_value_for_role(spec, back_axis, "back"),
        front=_value_for_role(spec, front_axis, "front"),
    )


def matrix_for(spec: PatternSpec) -> dict:
    cells = [cell_at(spec, r, c) for r in range(3) for c in range(3)]
    return {"cells": cells, "correct": cells[spec.blank_index]}


def distractor_tokens_for(spec: PatternSpec, matrix: dict) -> list[OverlayToken]:
    blank = spec.blank_index
    row, col = blank // 3, blank % 3
    back_axis, front_axis = _axes(spec, row, col)
    correct = matrix["correct"]

    swapped = OverlayToken(back=correct.front, front=correct.back)
    wrong_row = OverlayToken(back=_value_for_role(spec, (back_axis + 1) % 3, "back"), front=correct.front)
    wrong_col = OverlayToken(back=correct.back, front=_value_for_role(spec, (front_axis + 1) % 3, "front"))
    wrong_both = OverlayToken(
        back=_value_for_role(spec, (back_axis + 2) % 3, "back"),
        front=_value_for_role(spec, (front_axis + 2) % 3, "front"),
    )
    other_visible = [matrix["cells"][i] for i in range(9) if i != blank]

    candidates = [swapped, wrong_row, wrong_col, wrong_both] + other_visible
    used = {correct}
    distractors: list[OverlayToken] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    i = 0
    while len(distractors) < 4 and i < len(SHAPE_CYCLE):
        cand = OverlayToken(
            back=Token(SHAPE_CYCLE[i], ACCENT),
            front=Token(SHAPE_CYCLE[(i + 1) % len(SHAPE_CYCLE)], FRONT_COLOR),
        )
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, matrix: dict) -> tuple[list[OverlayToken], str]:
    distractors = distractor_tokens_for(spec, matrix)
    choices = distractors + [matrix["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(matrix["correct"])]
    return choices, correct_letter


def _build_single_marker(token: Token, scale: float = 1.0, opacity: float = 1.0):
    s = 0.42 * scale * token.size_scale
    shape, color = token.shape, token.color
    kwargs = dict(color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
    if shape == "circle":
        return Circle(radius=s, **kwargs)
    if shape == "square":
        return Square(side_length=s * 1.8, **kwargs)
    if shape == "triangle":
        return Triangle(**kwargs).scale(s * 1.10)
    if shape == "diamond":
        return Square(side_length=s * 1.35, **kwargs).rotate(PI / 4)
    if shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5, **kwargs)
    if shape == "hexagon":
        return RegularPolygon(n=6, **kwargs).scale(s * 1.05)
    raise ValueError(shape)


def _build_overlay_marker(token: OverlayToken, scale: float = 1.0):
    back = _build_single_marker(token.back, scale, opacity=0.75)
    front = _build_single_marker(token.front, scale * FRONT_DRAW_SCALE, opacity=0.75)
    front.shift(FRONT_SHIFT * scale)
    return VGroup(back, front)


def _build_cell(token: Optional[OverlayToken], scale: float = 1.0, is_blank: bool = False):
    box = Square(side_length=1.1 * scale, color=INK, stroke_width=5, fill_opacity=0)
    content = Text("?", font_size=int(44 * scale), color=ACCENT, weight=BOLD) if is_blank else _build_overlay_marker(token, scale)
    content.move_to(box.get_center())
    return VGroup(box, content)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    q = Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)
    _max_w = min(11, config.frame_width - 1.0)
    if q.width > _max_w:
        q.scale(_max_w / q.width)
    return q


def build_matrix(spec: PatternSpec, matrix: dict, scale: float = 1.0):
    cells = [_build_cell(matrix["cells"][i], scale, i == spec.blank_index) for i in range(9)]
    rows = [VGroup(cells[r * 3], cells[r * 3 + 1], cells[r * 3 + 2]).arrange(RIGHT, buff=0.35 * scale)
            for r in range(3)]
    grid = VGroup(*rows).arrange(DOWN, buff=0.35 * scale)
    return grid, cells


def build_choice_row(choices: list[OverlayToken], labels=("A", "B", "C", "D", "E"), buff=0.75):
    group = VGroup(*[_build_overlay_marker(c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
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


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": QUESTION_TEXT,
        "matrix": "Each box has two overlapping shapes, each with its own rule.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Both the back shape and front shape must match their own rule.",
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

    matrix = matrix_for(spec)
    grid, _ = build_matrix(spec, matrix, scale=0.65)
    _max_w = min(12, config.frame_width - 1.0)
    if grid.width > _max_w:
        grid.scale(_max_w / grid.width)
    grid.next_to(question, DOWN, buff=0.5)

    choices, _ = choice_tokens_for(spec, matrix)
    choice_group = build_choice_row(choices)
    choice_group.next_to(grid, DOWN, buff=2.6)

    _group = VGroup(title, question, grid, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class OverlayIntersectionVideoScene(VoiceoverScene):
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

        matrix = matrix_for(spec)
        grid, cells = build_matrix(spec, matrix, scale=0.65)
        _max_w = min(12, config.frame_width - 1.0)
        if grid.width > _max_w:
            grid.scale(_max_w / grid.width)
        grid.next_to(question, DOWN, buff=2.0)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["matrix"]) as tracker:
            self.play(FadeIn(grid, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        choices, correct_letter = choice_tokens_for(spec, matrix)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(grid, DOWN, buff=2.6)

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

        blank_cell = cells[spec.blank_index]
        resolved = _build_overlay_marker(matrix["correct"], 0.65).move_to(blank_cell.get_center())
        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(blank_cell[1], scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.8)
            blank_cell[1].set_opacity(0)
            blank_cell.set_opacity(0)
            self.play(FadeOut(choice_group), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(grid, DOWN, buff=2.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, grid, resolved, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    matrix = matrix_for(spec)
    choices, correct_letter = choice_tokens_for(spec, matrix)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "serial_reasoning",
        "skill": "overlay_intersection_rules",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "blank_index": spec.blank_index,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sr_ovl_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["matrix"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
