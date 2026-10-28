"""
Shared content engine for Pattern Completion -> Reflection.

A directional arrow alternates between its normal orientation and its
left-right mirror image every step (period 2, like Alternating
Patterns). The base angle is always a diagonal (never 0/90/180/270)
because a purely horizontal or vertical arrow looks IDENTICAL to its
own left-right mirror -- the flip would be invisible. Verified
empirically: Manim's flip(axis=UP) mirrors left-right, flip(axis=RIGHT)
mirrors top-bottom.

Distractors specifically target reflection/rotation confusion:
rotating 90 or 180 degrees (a rotation, not a reflection) and mirroring
across the WRONG axis (top-bottom instead of left-right).
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

# Diagonal-only: a horizontal/vertical arrow would look unchanged when mirrored.
BASE_ANGLES = [30, 45, 60, 120, 135, 150, 210, 225, 240, 300, 315, 330]
ATTR_BASE_INDEX = {"diag1": 0, "diag2": 2, "diag3": 4, "diag4": 6, "diag5": 8}
ATTRIBUTES = list(ATTR_BASE_INDEX.keys())

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
    def base_angle(self) -> int:
        idx = (ATTR_BASE_INDEX[self.attribute] + self.palette_offset) % len(BASE_ANGLES)
        return BASE_ANGLES[idx]

    @property
    def displayed_count(self) -> int:
        return CYCLES_SHOWN_BY_GRADE[self.grade_rank] * 2

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_ref_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


@dataclass(frozen=True)
class Token:
    base_angle: int
    transform: str  # normal | mirror_lr | mirror_tb | rotate90 | rotate180


def unit_tokens_for(spec: PatternSpec) -> list[Token]:
    start_mirrored = bool(spec.palette_offset % 2)
    a = Token(spec.base_angle, "mirror_lr" if start_mirrored else "normal")
    b = Token(spec.base_angle, "normal" if start_mirrored else "mirror_lr")
    return [a, b]


def sequence_for(spec: PatternSpec) -> tuple[list[Token], Token, list[Token]]:
    unit = unit_tokens_for(spec)
    seq = [unit[i % 2] for i in range(spec.displayed_count)]
    correct = unit[spec.displayed_count % 2]
    return seq, correct, unit


def distractor_tokens_for(spec: PatternSpec, unit: list[Token], correct: Token) -> list[Token]:
    other = next(t for t in unit if t != correct)
    a = spec.base_angle
    candidates = [
        other,
        Token(a, "rotate90"),
        Token(a, "rotate180"),
        Token(a, "mirror_tb"),
    ]
    used = {correct, *unit}
    distractors: list[Token] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    fallback_angles = [(a + 15) % 360, (a - 15) % 360, (a + 75) % 360]
    i = 0
    while len(distractors) < 4 and i < len(fallback_angles):
        cand = Token(fallback_angles[i], "normal")
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


def _apply_transform(arrow, transform: str):
    if transform == "normal":
        return arrow
    if transform == "mirror_lr":
        return arrow.flip(axis=UP)
    if transform == "mirror_tb":
        return arrow.flip(axis=RIGHT)
    if transform == "rotate90":
        return arrow.rotate(90 * DEGREES, about_point=arrow.get_start())
    if transform == "rotate180":
        return arrow.rotate(180 * DEGREES, about_point=arrow.get_start())
    raise ValueError(transform)


def _build_marker(token: Token, scale: float = 1.0):
    arrow = Arrow(
        ORIGIN, RIGHT * 0.95 * scale, buff=0, color=INK, stroke_width=8,
        max_tip_length_to_length_ratio=0.4,
    )
    arrow.rotate(token.base_angle * DEGREES, about_point=arrow.get_start())
    return _apply_transform(arrow, token.transform)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    seq, correct, unit = sequence_for(spec)
    mobjs = [_build_marker(t, 1.0) for t in seq] + [_qmark(1.0)]
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


def build_choice_group(spec: PatternSpec, unit: list[Token], correct: Token):
    choices, correct_letter = choice_tokens_for(spec, unit, correct)
    markers = [_build_marker(t, 0.85) for t in choices]
    group = VGroup(*markers).arrange(RIGHT, buff=1.1)

    full = VGroup()
    for letter, marker in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(marker, UP, buff=0.35)
        full.add(VGroup(letter_text, marker))
    full.move_to(ORIGIN)
    _max_w = min(12, config.frame_width - 1.0)
    if full.width > _max_w:
        full.scale(_max_w / full.width)
    return full, correct_letter


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.32, stroke_width=6, corner_radius=0.12)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": QUESTION_TEXT,
        "sequence": "It flips to its mirror image, back and forth.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "It keeps flipping. Next is the mirror image.",
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

    row, arrows, _, seq, correct, unit, item_scale = build_sequence_group(spec)
    sequence_group = VGroup(row, arrows)
    sequence_group.move_to(ORIGIN).shift(UP * 0.6)

    choices, _ = build_choice_group(spec, unit, correct)
    choices.next_to(sequence_group, DOWN, buff=1.3)

    _group = VGroup(title, question, sequence_group, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class ReflectionVideoScene(VoiceoverScene):
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
        choices, correct_letter = build_choice_group(spec, unit, correct)
        choices.next_to(sequence_group, DOWN, buff=2.8)
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

        resolved = _build_marker(correct, item_scale)
        resolved.move_to(mobjs[-1].get_center())
        explain = Text(
            "flips to its mirror image",
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
    seq, correct, unit = sequence_for(spec)
    choices, correct_letter = choice_tokens_for(spec, unit, correct)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "reflection",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_ref_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "base_angle": spec.base_angle,
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
