"""
Shared content engine for Spatial Visualization -> Piece Assembly.

Shows a target rectangle's outline, then 5 candidate PAIRS of separate
rectangular pieces (drawn with a visible gap between them, to true
scale against the target). The student must judge which pair's
combined dimensions would exactly tile the target if pushed together
-- genuine piece-assembly reasoning (mentally summing two disjoint
pieces' dimensions), distinct from Shape Combination/Overlay (which
stack pieces on top of each other rather than tiling them edge to
edge).

Known simplification: pieces are always axis-aligned rectangles cut by
one straight vertical or horizontal line (no diagonal/triangular
pieces) -- this keeps "do these dimensions sum correctly" an exact,
checkable arithmetic fact rather than requiring real polygon geometry.
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
TITLE_TEXT = "Spatial Visualization"
QUESTION_TEXT = "Which pair of pieces fits together to make the target shape?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

ATTRIBUTES = ["vertical_half", "vertical_uneven", "horizontal_half", "horizontal_uneven", "vertical_quarter"]
CUT_TYPE_BY_ATTR = {
    "vertical_half": "vertical", "vertical_uneven": "vertical",
    "horizontal_half": "horizontal", "horizontal_uneven": "horizontal",
    "vertical_quarter": "vertical",
}
FRACTION_BY_ATTR = {
    "vertical_half": 0.5, "vertical_uneven": 1 / 3,
    "horizontal_half": 0.5, "horizontal_uneven": 1 / 3,
    "vertical_quarter": 0.25,
}
TARGET_DIMS_BY_ATTR = {
    "vertical_half": (2.0, 2.0), "vertical_uneven": (3.0, 2.0),
    "horizontal_half": (2.0, 3.0), "horizontal_uneven": (2.0, 3.0),
    "vertical_quarter": (4.0, 2.0),
}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}

SCALE_UNIT = 0.48


@dataclass(frozen=True)
class Piece:
    width: float
    height: float

    def rounded(self) -> "Piece":
        return Piece(round(self.width, 4), round(self.height, 4))


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
    def cut_type(self) -> str:
        return CUT_TYPE_BY_ATTR[self.attribute]

    @property
    def fraction(self) -> float:
        return FRACTION_BY_ATTR[self.attribute]

    @property
    def target_dims(self) -> tuple[float, float]:
        w, h = TARGET_DIMS_BY_ATTR[self.attribute]
        s = 0.85 + 0.05 * (self.palette_offset % 4)
        return (round(w * s, 4), round(h * s, 4))

    @property
    def question_id(self) -> str:
        base = f"sv_asm_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def correct_pieces_for(spec: PatternSpec) -> tuple[Piece, Piece]:
    w, h = spec.target_dims
    f = spec.fraction
    if spec.cut_type == "vertical":
        return (Piece(w * f, h).rounded(), Piece(w * (1 - f), h).rounded())
    return (Piece(w, h * f).rounded(), Piece(w, h * (1 - f)).rounded())


def distractor_pairs_for(spec: PatternSpec, correct: tuple[Piece, Piece]) -> list[tuple[Piece, Piece]]:
    w, h = spec.target_dims
    a, b = correct

    if spec.cut_type == "vertical":
        height_mismatch = (a, Piece(b.width, b.height * 0.75).rounded())
        sum_wrong = (Piece(a.width * 1.3, a.height).rounded(), b)
        other_orientation = (Piece(w, h * spec.fraction).rounded(), Piece(w, h * (1 - spec.fraction)).rounded())
    else:
        height_mismatch = (a, Piece(b.width * 0.75, b.height).rounded())
        sum_wrong = (Piece(a.width, a.height * 1.3).rounded(), b)
        other_orientation = (Piece(w * spec.fraction, h).rounded(), Piece(w * (1 - spec.fraction), h).rounded())

    unrelated = (Piece(0.6, 0.6), Piece(0.8, 0.8))

    candidates = [height_mismatch, sum_wrong, other_orientation, unrelated]
    used = {correct}
    distractors: list[tuple[Piece, Piece]] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    bump = 1
    while len(distractors) < 4 and bump < 10:
        shrink = 1.0 - 0.05 * bump
        cand = (a, Piece(b.width * shrink, b.height * shrink).rounded())
        bump += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_pairs_for(spec: PatternSpec, correct: tuple[Piece, Piece]) -> tuple[list[tuple[Piece, Piece]], str]:
    distractors = distractor_pairs_for(spec, correct)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def build_rect(piece: Piece, color: str = ACCENT, scale: float = SCALE_UNIT):
    return Rectangle(width=max(piece.width * scale, 0.05), height=max(piece.height * scale, 0.05),
                      color=color, stroke_width=4, fill_color=color, fill_opacity=0.3)


def build_target(spec: PatternSpec, scale: float = SCALE_UNIT):
    w, h = spec.target_dims
    return Rectangle(width=w * scale, height=h * scale, color=INK, stroke_width=4, fill_opacity=0)


def build_piece_pair(pair: tuple[Piece, Piece], scale: float = SCALE_UNIT, buff: float = 0.25):
    a, b = pair
    group = VGroup(build_rect(a, ACCENT, scale), build_rect(b, FRONT_COLOR, scale))
    group.arrange(RIGHT, buff=buff)
    return group


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_choice_row(choices: list[tuple[Piece, Piece]], labels=("A", "B", "C", "D", "E"), buff=0.6):
    group = VGroup(*[build_piece_pair(c, SCALE_UNIT * 0.8) for c in choices]).arrange(RIGHT, buff=buff)
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
    return SurroundingRectangle(mobj, color=color, buff=0.2, stroke_width=6, corner_radius=0.1)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": QUESTION_TEXT,
        "target": "Here is the target shape's outline.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "The right pair's sizes add up to exactly match the target.",
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
    _max_w = min(11.5, config.frame_width - 1.0)
    if question.width > _max_w:
        question.scale(_max_w / question.width)

    target = build_target(spec)
    target.next_to(question, DOWN, buff=0.5)

    correct = correct_pieces_for(spec)
    choices, _ = choice_pairs_for(spec, correct)
    choice_group = build_choice_row(choices)
    choice_group.next_to(target, DOWN, buff=0.7)

    _group = VGroup(title, question, target, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class PieceAssemblyVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)
        _max_w = min(11.5, config.frame_width - 1.0)
        if question.width > _max_w:
            question.scale(_max_w / question.width)

        with self.voiceover(text=narration_lines(spec, "")["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        target = build_target(spec)
        target.move_to(ORIGIN).shift(UP * 0.7)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["target"]) as tracker:
            self.play(FadeIn(target, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        correct = correct_pieces_for(spec)
        choices, correct_letter = choice_pairs_for(spec, correct)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(target, DOWN, buff=0.7)

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
        answer_text.next_to(target, DOWN, buff=0.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, target, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    correct = correct_pieces_for(spec)
    choices, correct_letter = choice_pairs_for(spec, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "spatial_visualization",
        "skill": "piece_assembly",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "target_dims": list(spec.target_dims),
        "cut_type": spec.cut_type,
        "fraction": spec.fraction,
        "correct_pieces": [[p.width, p.height] for p in correct],
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sv_asm_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["target"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
