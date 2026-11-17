"""
Shared content engine for Spatial Visualization -> Shape Subtraction.

The inverse of Shape Combination: the question shows a combined
(overlaid) figure of 2 or 3 pieces, then shows ONE of those pieces
being taken away, and asks what remains. Reuses the same Piece /
combo-overlay drawing building blocks as Shape Combination.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, replace
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
QUESTION_TEXT = "If you take away this piece, what remains?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]
SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]
SIZE_LEVELS = [0.7, 0.9, 1.1, 1.3]

ATTRIBUTES = ["two_minus_shape", "two_minus_color", "two_minus_size", "three_minus_mid", "three_minus_edge"]
ATTR_VARIES = {
    "two_minus_shape": {"shape": True, "color": False, "size": False},
    "two_minus_color": {"shape": False, "color": True, "size": False},
    "two_minus_size": {"shape": False, "color": False, "size": True},
    "three_minus_mid": {"shape": True, "color": True, "size": False},
    "three_minus_edge": {"shape": True, "color": True, "size": False},
}
NUM_PIECES = {"two_minus_shape": 2, "two_minus_color": 2, "two_minus_size": 2,
              "three_minus_mid": 3, "three_minus_edge": 3}
SUBTRACT_INDEX = {"two_minus_shape": 0, "two_minus_color": 0, "two_minus_size": 0,
                   "three_minus_mid": 1, "three_minus_edge": 2}
ROLE_COLORS = [ACCENT, FRONT_COLOR, THIRD_COLOR]

DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}

LAYER_SCALE = 0.78
LAYER_SHIFT = RIGHT * 0.2 + DOWN * 0.2


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
    def subtract_index(self) -> int:
        return SUBTRACT_INDEX[self.attribute]

    @property
    def question_id(self) -> str:
        base = f"sv_sub_{self.grade_label}_q{self.question_number:02d}"
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
            color = COLOR_CYCLE[(off + k * 2) % len(COLOR_CYCLE)][1]
        else:
            color = ROLE_COLORS[k % len(ROLE_COLORS)]
        if varies["size"]:
            size = SIZE_LEVELS[(off + k) % len(SIZE_LEVELS)]
        else:
            size = 1.0 if k == 0 else 0.72
        pieces.append(Piece(shape, color, size))
    return tuple(pieces)


def _remaining(pieces: tuple[Piece, ...], idx_removed: int) -> tuple[Piece, ...]:
    return tuple(p for i, p in enumerate(pieces) if i != idx_removed)


def distractor_combos_for(spec: PatternSpec, all_pieces: tuple[Piece, ...],
                           correct: tuple[Piece, ...]) -> list[tuple[Piece, ...]]:
    n = len(all_pieces)
    idx = spec.subtract_index
    alt_idx = (idx + 1) % n
    wrong_subtract = _remaining(all_pieces, alt_idx)
    forgot_to_subtract = all_pieces

    shifted_all = pieces_for(replace(spec, palette_offset=spec.palette_offset + 1))
    shifted_remaining = _remaining(shifted_all, idx)

    unrelated_all = pieces_for(replace(spec, palette_offset=spec.palette_offset + 5))
    unrelated_remaining = _remaining(unrelated_all, idx)

    candidates = [wrong_subtract, forgot_to_subtract, shifted_remaining, unrelated_remaining]
    used = {correct}
    distractors: list[tuple[Piece, ...]] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    i = 0
    while len(distractors) < 4 and i < len(SHAPE_CYCLE):
        head = Piece(SHAPE_CYCLE[i], correct[0].color, correct[0].size_scale)
        cand = (head,) + correct[1:]
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_combos_for(spec: PatternSpec, all_pieces: tuple[Piece, ...],
                       correct: tuple[Piece, ...]) -> tuple[list[tuple[Piece, ...]], str]:
    distractors = distractor_combos_for(spec, all_pieces, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
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


def build_combo_marker(pieces: tuple[Piece, ...], scale: float = 1.0):
    group = VGroup()
    for idx, p in enumerate(pieces):
        layer_scale = scale * (LAYER_SCALE ** idx)
        marker = _build_single_marker(p, layer_scale, opacity=0.78)
        marker.shift(LAYER_SHIFT * scale * idx)
        group.add(marker)
    return group


def build_subtraction_row(all_pieces: tuple[Piece, ...], subtract_index: int, scale: float = 1.0):
    subtracted = all_pieces[subtract_index]
    row = VGroup(
        build_combo_marker(all_pieces, scale),
        Text("−", font_size=int(44 * scale), color=INK, weight=BOLD),
        _build_single_marker(subtracted, scale),
        Text("=", font_size=int(44 * scale), color=INK, weight=BOLD),
        Text("?", font_size=int(48 * scale), color=ACCENT, weight=BOLD),
    )
    row.arrange(RIGHT, buff=0.5 * scale)
    return row


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_choice_row(choices: list[tuple[Piece, ...]], labels=("A", "B", "C", "D", "E"), buff=0.75):
    group = VGroup(*[build_combo_marker(c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
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
        "pieces": "Here is a combined shape, and one piece being taken away.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Only the removed piece disappears -- the rest stays the same.",
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

    all_pieces = pieces_for(spec)
    correct = _remaining(all_pieces, spec.subtract_index)
    sub_row = build_subtraction_row(all_pieces, spec.subtract_index, scale=0.85)
    sub_row.next_to(question, DOWN, buff=0.6)
    _max_w = min(11, config.frame_width - 1.0)
    if sub_row.width > _max_w:
        sub_row.scale(_max_w / sub_row.width)

    choices, _ = choice_combos_for(spec, all_pieces, correct)
    choice_group = build_choice_row(choices)
    choice_group.next_to(sub_row, DOWN, buff=2.6)

    _group = VGroup(title, question, sub_row, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)
    scene.choice_regions = {letter: _group[-1][i] for i, letter in enumerate("ABCDE")}


class ShapeSubtractionVideoScene(VoiceoverScene):
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

        all_pieces = pieces_for(spec)
        correct = _remaining(all_pieces, spec.subtract_index)
        sub_row = build_subtraction_row(all_pieces, spec.subtract_index, scale=0.85)
        sub_row.next_to(question, DOWN, buff=2.0)
        _max_w = min(11, config.frame_width - 1.0)
        if sub_row.width > _max_w:
            sub_row.scale(_max_w / sub_row.width)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["pieces"]) as tracker:
            self.play(FadeIn(sub_row, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        choices, correct_letter = choice_combos_for(spec, all_pieces, correct)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(sub_row, DOWN, buff=2.6)

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
        answer_text.next_to(sub_row, DOWN, buff=2.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, sub_row, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    all_pieces = pieces_for(spec)
    correct = _remaining(all_pieces, spec.subtract_index)
    choices, correct_letter = choice_combos_for(spec, all_pieces, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "spatial_visualization",
        "skill": "shape_subtraction",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "num_pieces": len(all_pieces),
        "subtract_index": spec.subtract_index,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sv_sub_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["pieces"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
