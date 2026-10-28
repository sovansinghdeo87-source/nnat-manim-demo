"""
Shared content engine for Spatial Visualization -> Overlay.

Complementary to Shape Combination/Shape Subtraction: the question
shows the FINAL overlaid picture of 2 or 3 pieces (back to front, each
layer slightly smaller and shifted, same convention as those two
subskills) and asks which single piece is on the BOTTOM -- partially
hidden behind the others. This is a genuine depth/occlusion
visualization skill, the mirror image of Pattern Completion's
Overlapping Shapes (which asks "who's on top"): here the answer
choices are single shapes, not combos, since the student must isolate
one specific layer from the merged picture.
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
QUESTION_TEXT = "Which piece is on the bottom, hidden behind the others?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]
SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]
SIZE_LEVELS = [0.7, 0.9, 1.1, 1.3]

ATTRIBUTES = ["two_back_shape", "two_back_color", "two_back_size", "three_back", "three_back_combo"]
ATTR_VARIES = {
    "two_back_shape": {"shape": True, "color": False, "size": False},
    "two_back_color": {"shape": False, "color": True, "size": False},
    "two_back_size": {"shape": False, "color": False, "size": True},
    "three_back": {"shape": True, "color": False, "size": False},
    "three_back_combo": {"shape": True, "color": True, "size": False},
}
NUM_PIECES = {"two_back_shape": 2, "two_back_color": 2, "two_back_size": 2,
              "three_back": 3, "three_back_combo": 3}
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
    def question_id(self) -> str:
        base = f"sv_ovl_{self.grade_label}_q{self.question_number:02d}"
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


def distractor_singles_for(spec: PatternSpec, pieces: tuple[Piece, ...]) -> list[Piece]:
    correct = pieces[0]
    candidates = list(pieces[1:])
    shifted = pieces_for(replace(spec, palette_offset=spec.palette_offset + 1))[0]
    unrelated = pieces_for(replace(spec, palette_offset=spec.palette_offset + 5))[0]
    candidates += [shifted, unrelated]

    used = {correct}
    distractors: list[Piece] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    i = 0
    while len(distractors) < 4 and i < len(SHAPE_CYCLE):
        cand = Piece(SHAPE_CYCLE[i], correct.color, correct.size_scale)
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_singles_for(spec: PatternSpec, pieces: tuple[Piece, ...]) -> tuple[list[Piece], str]:
    correct = pieces[0]
    distractors = distractor_singles_for(spec, pieces)
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


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    q = Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)
    _max_w = min(11, config.frame_width - 1.0)
    if q.width > _max_w:
        q.scale(_max_w / q.width)
    return q


def build_choice_row(choices: list[Piece], labels=("A", "B", "C", "D", "E"), buff=0.75):
    group = VGroup(*[_build_single_marker(c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
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
        "picture": "Here is a picture made of overlapping pieces.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "The back piece is partly covered, but its edge still peeks out.",
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
    picture = build_combo_marker(pieces, scale=1.3)
    _max_w = min(12, config.frame_width - 1.0)
    if picture.width > _max_w:
        picture.scale(_max_w / picture.width)
    picture.next_to(question, DOWN, buff=0.6)

    choices, _ = choice_singles_for(spec, pieces)
    choice_group = build_choice_row(choices)
    choice_group.next_to(picture, DOWN, buff=2.6)

    _group = VGroup(title, question, picture, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class OverlayVideoScene(VoiceoverScene):
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
        picture = build_combo_marker(pieces, scale=1.3)
        _max_w = min(12, config.frame_width - 1.0)
        if picture.width > _max_w:
            picture.scale(_max_w / picture.width)
        picture.next_to(question, DOWN, buff=2.0)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["picture"]) as tracker:
            self.play(FadeIn(picture, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        choices, correct_letter = choice_singles_for(spec, pieces)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(picture, DOWN, buff=2.6)

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
        answer_text.next_to(picture, DOWN, buff=2.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, picture, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    pieces = pieces_for(spec)
    choices, correct_letter = choice_singles_for(spec, pieces)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "spatial_visualization",
        "skill": "overlay",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "num_pieces": len(pieces),
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sv_ovl_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["picture"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
