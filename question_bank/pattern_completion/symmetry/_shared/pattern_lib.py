"""
Shared content engine for Pattern Completion -> Symmetry.

Unlike the other 9 subskills, this is NOT a sequence-with-arrows
question. A square frame is split by a dashed vertical mirror line.
The LEFT half shows 1-3 small marks at fixed positions; the RIGHT half
is blank. The student picks which of 5 complete (left+right) pictures
correctly mirrors the left half across the line.

Four distractor types, always present regardless of mark count:
    upside_down  -- right half flipped across BOTH axes (wrong axis)
    no_mirror    -- right half has the same arrangement as the left, just moved
                    over -- NOT reflected (tests mirror vs. copy confusion)
    shifted      -- correctly mirrored but offset vertically (off registration)
    color_swap   -- correct position, but the wrong color
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
QUESTION_SIZE = 28
CHOICE_LETTER_SIZE = 24
EXPLAIN_SIZE = 24
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Symmetry"
QUESTION_TEXT = "Which picture correctly completes the mirror image?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]

SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star"]
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"),
]

MARKS_COUNT_BY_GRADE = {0: 1, 1: 1, 2: 2, 3: 2, 4: 3}
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5}

LEFT_POSITIONS_POOL = [(-0.3, 0.28), (-0.15, -0.28), (-0.32, -0.05), (-0.12, 0.32), (-0.28, 0.06)]

ATTRIBUTES = ["motif_a", "motif_b", "motif_c", "motif_d", "motif_e"]


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
    def marks_count(self) -> int:
        return MARKS_COUNT_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_sym_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


@dataclass(frozen=True)
class Mark:
    shape: str
    color: str
    x: float
    y: float


def left_marks_for(spec: PatternSpec) -> tuple[Mark, ...]:
    n = spec.marks_count
    attr_idx = ATTRIBUTES.index(spec.attribute)
    off = spec.palette_offset
    marks = []
    for i in range(n):
        shape = SHAPE_CYCLE[(attr_idx + off + i) % len(SHAPE_CYCLE)]
        color = COLOR_CYCLE[(attr_idx + off + i) % len(COLOR_CYCLE)][1]
        x, y = LEFT_POSITIONS_POOL[(attr_idx + i) % len(LEFT_POSITIONS_POOL)]
        marks.append(Mark(shape, color, x, y))
    return tuple(marks)


def _mirror(marks: tuple[Mark, ...]) -> tuple[Mark, ...]:
    return tuple(Mark(m.shape, m.color, -m.x, m.y) for m in marks)


def _variant_right_marks(marks: tuple[Mark, ...], kind: str) -> tuple[Mark, ...]:
    if kind == "correct":
        return _mirror(marks)
    if kind == "upside_down":
        return tuple(Mark(m.shape, m.color, -m.x, -m.y) for m in marks)
    if kind == "no_mirror":
        # Shifted into the right half but NOT reflected -- same orientation as the
        # left, just translated. (Simply keeping x unchanged would leave the "right
        # half" sitting in the left half, invisible/overlapping the original.)
        return tuple(Mark(m.shape, m.color, m.x + 0.45, m.y) for m in marks)
    if kind == "shifted":
        return tuple(Mark(m.shape, m.color, -m.x, m.y + 0.15) for m in marks)
    if kind == "color_swap":
        return tuple(
            Mark(m.shape, COLOR_CYCLE[(i + 1) % len(COLOR_CYCLE)][1], -m.x, m.y)
            for i, m in enumerate(marks)
        )
    raise ValueError(kind)


def choice_variants_for(spec: PatternSpec) -> tuple[list[str], str]:
    kinds = ["upside_down", "no_mirror", "shifted", "color_swap", "correct"]
    rng = random.Random(spec.question_id)
    rng.shuffle(kinds)
    correct_letter = "ABCDE"[kinds.index("correct")]
    return kinds, correct_letter


def _build_mark(mark: Mark, frame_half_w: float, frame_half_h: float, scale: float = 1.0):
    cx = mark.x / 0.45 * frame_half_w
    cy = mark.y / 0.45 * frame_half_h
    s = 0.16 * scale
    if mark.shape == "circle":
        shape = Circle(radius=s, color=mark.color, stroke_width=0, fill_color=mark.color, fill_opacity=1)
    elif mark.shape == "square":
        shape = Square(side_length=s * 1.8, color=mark.color, stroke_width=0, fill_color=mark.color, fill_opacity=1)
    elif mark.shape == "triangle":
        shape = Triangle(color=mark.color, stroke_width=0, fill_color=mark.color, fill_opacity=1).scale(s * 1.6)
    elif mark.shape == "diamond":
        shape = Square(side_length=s * 1.8, color=mark.color, stroke_width=0,
                        fill_color=mark.color, fill_opacity=1).rotate(PI / 4)
    elif mark.shape == "star":
        shape = Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                      color=mark.color, stroke_width=0, fill_color=mark.color, fill_opacity=1)
    else:
        raise ValueError(mark.shape)
    shape.move_to(RIGHT * cx + UP * cy)
    return shape


def _build_frame(left_marks, right_marks, scale: float = 1.0, show_right: bool = True):
    half_w, half_h = 0.65 * scale, 0.5 * scale
    frame = Rectangle(width=2 * half_w, height=2 * half_h, color=INK, stroke_width=5)
    divider = DashedLine(UP * half_h, DOWN * half_h, color=INK, stroke_width=3, dash_length=0.06)
    group = VGroup(frame, divider)
    for m in left_marks:
        group.add(_build_mark(m, half_w, half_h, scale))
    if show_right:
        for m in right_marks:
            group.add(_build_mark(m, half_w, half_h, scale))
    return group


def _qmark_half(half_w, half_h, scale=1.0):
    q = Text("?", font_size=int(32 * scale), color=ACCENT, weight=BOLD)
    q.move_to(RIGHT * half_w * 0.5)
    return q


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.22, stroke_width=6, corner_radius=0.1)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": "Here is half of a picture, split by a dashed mirror line.",
        "prompt": "Find the correctly mirrored half.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Everything flips across the line -- same distance, same shape.",
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
    question = make_question().next_to(title, DOWN, buff=0.3)
    _max_w = min(11, config.frame_width - 1.0)
    if question.width > _max_w:
        question.scale(_max_w / question.width)

    left_marks = left_marks_for(spec)
    big_frame = _build_frame(left_marks, (), scale=2.5, show_right=False)
    half_w = 0.65 * 2.5
    half_h = 0.5 * 2.5
    qmark = _qmark_half(half_w, half_h, scale=2.5)
    big_frame.add(qmark)
    big_frame.next_to(question, DOWN, buff=0.4)

    kinds, _ = choice_variants_for(spec)
    choice_frames = VGroup()
    for letter, kind in zip("ABCDE", kinds):
        right_marks = _variant_right_marks(left_marks, kind)
        frame = _build_frame(left_marks, right_marks, scale=1.0)
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(frame, UP, buff=0.25)
        choice_frames.add(VGroup(letter_text, frame))
    choice_frames.arrange(RIGHT, buff=0.55)
    _max_w = min(12, config.frame_width - 1.0)
    if choice_frames.width > _max_w:
        choice_frames.scale(_max_w / choice_frames.width)
    choice_frames.next_to(big_frame, DOWN, buff=0.7)

    _group = VGroup(title, question, big_frame, choice_frames)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class SymmetryVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.3)
        _max_w = min(11, config.frame_width - 1.0)
        if question.width > _max_w:
            question.scale(_max_w / question.width)

        with self.voiceover(text=narration_lines(spec, "")["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        left_marks = left_marks_for(spec)
        half_w, half_h = 0.65 * 2.5, 0.5 * 2.5
        frame_outline = Rectangle(width=2 * half_w, height=2 * half_h, color=INK, stroke_width=5)
        divider = DashedLine(UP * half_h, DOWN * half_h, color=INK, stroke_width=3, dash_length=0.06)
        left_mobjs = VGroup(*[_build_mark(m, half_w, half_h, 2.5) for m in left_marks])
        qmark = _qmark_half(half_w, half_h, scale=2.5)
        big_frame = VGroup(frame_outline, divider, left_mobjs, qmark)
        big_frame.next_to(question, DOWN, buff=0.4)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["prompt"]) as tracker:
            self.play(Create(frame_outline), Create(divider), run_time=0.8)
            self.play(FadeIn(left_mobjs, scale=0.7), run_time=0.6)
            self.play(FadeIn(qmark, scale=0.7), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        kinds, correct_letter = choice_variants_for(spec)
        lines = narration_lines(spec, correct_letter)
        choice_frames = VGroup()
        for letter, kind in zip("ABCDE", kinds):
            right_marks = _variant_right_marks(left_marks, kind)
            frame = _build_frame(left_marks, right_marks, scale=1.0)
            letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
            letter_text.next_to(frame, UP, buff=0.25)
            choice_frames.add(VGroup(letter_text, frame))
        choice_frames.arrange(RIGHT, buff=0.55)
        _max_w = min(12, config.frame_width - 1.0)
        if choice_frames.width > _max_w:
            choice_frames.scale(_max_w / choice_frames.width)
        choice_frames.next_to(big_frame, DOWN, buff=0.7)

        with self.voiceover(text=lines["choices"]) as tracker:
            self.play(FadeIn(choice_frames, shift=UP * 0.3), run_time=0.9)
            self.wait(tracker.get_remaining_duration())

        correct_index = "ABCDE".index(correct_letter)
        choice_correct = choice_frames[correct_index]
        box = surround(choice_correct)
        with self.voiceover(text=lines["reveal"]) as tracker:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(choice_correct, color=CORRECT, scale_factor=1.1), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        correct_right_marks = _variant_right_marks(left_marks, "correct")
        resolved_marks = VGroup(*[_build_mark(m, half_w, half_h, 2.5) for m in correct_right_marks])
        resolved_marks.shift(frame_outline.get_center())
        explain = Text(
            "mirrored across the line",
            font_size=EXPLAIN_SIZE, color=INK,
        ).next_to(big_frame, DOWN, buff=0.4)

        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(qmark, scale=0.6), FadeIn(resolved_marks, scale=0.6), run_time=0.6)
            qmark.set_opacity(0)
            self.play(FadeOut(choice_frames), FadeOut(box), run_time=0.4)
            self.play(Write(explain), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(explain, DOWN, buff=0.5)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, frame_outline, divider, left_mobjs,
                            resolved_marks, explain, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    kinds, correct_letter = choice_variants_for(spec)
    lines = narration_lines(spec, correct_letter)
    left_marks = left_marks_for(spec)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "symmetry",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "marks_count": spec.marks_count,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_sym_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "left_marks": [[m.shape, m.color, m.x, m.y] for m in left_marks],
        "explanation_script": [
            lines["intro"], lines["prompt"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
