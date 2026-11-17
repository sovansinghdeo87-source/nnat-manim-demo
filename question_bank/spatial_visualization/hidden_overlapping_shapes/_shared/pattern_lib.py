"""
Shared content engine for Spatial Visualization -> Hidden/Overlapping Shapes.

2 or 3 shapes are drawn OUTLINE-ONLY (fill_opacity=0) at scattered,
overlapping positions, so their boundaries interweave into one
cluttered line figure -- genuine figure-ground segregation, distinct
from the Overlay subskill (which stacks FILLED pieces concentrically
and asks about depth/z-order, not about tracing a shape out of
line clutter). The question asks which single shape is actually
hidden in the figure.

Critical correctness invariant: every distractor must be a
(shape, color) combination that is NOT any of the pieces actually in
the figure -- otherwise the question would have more than one
"correct" answer. Distractors are built by explicitly excluding every
shape and color already used, not just avoiding the literal target
piece.
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
THIRD_COLOR = "#0D9488"
CORRECT = "#22C55E"
BG = WHITE

TITLE_SIZE = 40
QUESTION_SIZE = 28
CHOICE_LETTER_SIZE = 24
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Spatial Visualization"
QUESTION_TEXT = "Which shape is hidden in this overlapping figure?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]
SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
COLOR_CYCLE = [
    "#E4572E", "#F59E0B", "#7C3AED", "#0D9488", "#EC4899", "#EAB308",
]
ROLE_COLORS = [ACCENT, FRONT_COLOR, THIRD_COLOR]

ATTRIBUTES = ["two_hidden_shape", "two_hidden_color", "three_hidden", "three_hidden_combo", "three_hidden_hard"]
ATTR_VARIES = {
    "two_hidden_shape": {"shape": True, "color": False},
    "two_hidden_color": {"shape": False, "color": True},
    "three_hidden": {"shape": True, "color": False},
    "three_hidden_combo": {"shape": True, "color": True},
    "three_hidden_hard": {"shape": True, "color": True},
}
NUM_PIECES = {"two_hidden_shape": 2, "two_hidden_color": 2, "three_hidden": 3,
              "three_hidden_combo": 3, "three_hidden_hard": 3}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}

OFFSETS = [ORIGIN, RIGHT * 0.5 + UP * 0.15, LEFT * 0.45 + DOWN * 0.3]
OFFSETS_HARD = [ORIGIN, RIGHT * 0.6 + UP * 0.3, LEFT * 0.55 + DOWN * 0.4]


@dataclass(frozen=True)
class Piece:
    shape: str = "circle"
    color: str = INK
    size_scale: float = 1.0


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
    def question_id(self) -> str:
        base = f"sv_hid_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def pieces_for(spec: PatternSpec) -> tuple[Piece, ...]:
    off = spec.palette_offset
    varies = ATTR_VARIES[spec.attribute]
    n = NUM_PIECES[spec.attribute]
    pieces = []
    for k in range(n):
        shape = SHAPE_CYCLE[(off + (k * 2 if varies["shape"] else 0)) % len(SHAPE_CYCLE)]
        if varies["color"]:
            color = COLOR_CYCLE[(off + k * 2) % len(COLOR_CYCLE)]
        else:
            color = ROLE_COLORS[k % len(ROLE_COLORS)]
        pieces.append(Piece(shape, color, 1.0))
    return tuple(pieces)


def _first_unused(cycle: list[str], used: set[str], start: int) -> str:
    for k in range(len(cycle)):
        val = cycle[(start + k) % len(cycle)]
        if val not in used:
            return val
    raise RuntimeError("no unused value available in cycle")


def distractor_pieces_for(spec: PatternSpec, pieces: tuple[Piece, ...], target: Piece) -> list[Piece]:
    off = spec.palette_offset
    used_shapes = {p.shape for p in pieces}
    used_colors = {p.color for p in pieces}

    same_shape_other_color = Piece(target.shape, _first_unused(COLOR_CYCLE, used_colors, off + 1), 1.0)
    same_color_other_shape = Piece(_first_unused(SHAPE_CYCLE, used_shapes, off + 2), target.color, 1.0)
    unrelated1 = Piece(_first_unused(SHAPE_CYCLE, used_shapes, off + 3),
                        _first_unused(COLOR_CYCLE, used_colors, off + 4), 1.0)
    unrelated2 = Piece(_first_unused(SHAPE_CYCLE, used_shapes, off + 4),
                        _first_unused(COLOR_CYCLE, used_colors, off + 5), 1.0)

    candidates = [same_shape_other_color, same_color_other_shape, unrelated1, unrelated2]
    used_pieces = set(pieces)
    distractors: list[Piece] = []
    for cand in candidates:
        if cand not in used_pieces and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    i = 0
    while len(distractors) < 4 and i < len(SHAPE_CYCLE) * len(COLOR_CYCLE):
        shape = SHAPE_CYCLE[(off + 5 + i) % len(SHAPE_CYCLE)]
        color = COLOR_CYCLE[(off + 5 + i) % len(COLOR_CYCLE)]
        cand = Piece(shape, color, 1.0)
        i += 1
        if shape not in used_shapes and cand not in used_pieces and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_pieces_for(spec: PatternSpec, pieces: tuple[Piece, ...]) -> tuple[list[Piece], str]:
    target = pieces[0]
    distractors = distractor_pieces_for(spec, pieces, target)
    choices = distractors + [target]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(target)]
    return choices, correct_letter


def _build_single_marker(piece: Piece, scale: float = 1.0, opacity: float = 1.0):
    s = 0.42 * scale * piece.size_scale
    shape, color = piece.shape, piece.color
    kwargs = dict(color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
    if shape == "circle":
        return Circle(radius=s, **kwargs)
    if shape == "square":
        return Square(side_length=s * 1.8, **kwargs)
    if shape == "triangle":
        return Triangle(**kwargs).scale(s * 1.55)
    if shape == "diamond":
        return Square(side_length=s * 1.8, **kwargs).rotate(PI / 4)
    if shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5, **kwargs)
    if shape == "hexagon":
        return RegularPolygon(n=6, **kwargs).scale(s * 1.05)
    raise ValueError(shape)


def build_figure(spec: PatternSpec, pieces: tuple[Piece, ...], scale: float = 1.0):
    offsets = OFFSETS_HARD if spec.attribute == "three_hidden_hard" else OFFSETS
    group = VGroup()
    for i, p in enumerate(pieces):
        m = _build_single_marker(p, scale * 1.3, opacity=0)
        m.shift(offsets[i] * scale)
        group.add(m)
    return group


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_choice_row(choices: list[Piece], labels=("A", "B", "C", "D", "E"), buff=0.75):
    group = VGroup(*[_build_single_marker(c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
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
        "figure": "Here is a figure made of two or three overlapping outlines.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Only one choice truly matches a shape in the figure.",
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

    pieces = pieces_for(spec)
    figure = build_figure(spec, pieces, scale=1.3)
    figure.next_to(question, DOWN, buff=0.6)

    choices, _ = choice_pieces_for(spec, pieces)
    choice_group = build_choice_row(choices)
    choice_group.next_to(figure, DOWN, buff=2.6)

    _group = VGroup(title, question, figure, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)
    scene.choice_regions = {letter: _group[-1][i] for i, letter in enumerate("ABCDE")}


class HiddenOverlappingShapesVideoScene(VoiceoverScene):
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

        pieces = pieces_for(spec)
        figure = build_figure(spec, pieces, scale=1.3)
        figure.next_to(question, DOWN, buff=2.0)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["figure"]) as tracker:
            self.play(FadeIn(figure, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        choices, correct_letter = choice_pieces_for(spec, pieces)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(figure, DOWN, buff=2.6)

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
        answer_text.next_to(figure, DOWN, buff=2.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, figure, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    pieces = pieces_for(spec)
    choices, correct_letter = choice_pieces_for(spec, pieces)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "spatial_visualization",
        "skill": "hidden_overlapping_shapes",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "num_pieces": len(pieces),
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sv_hid_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["figure"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
