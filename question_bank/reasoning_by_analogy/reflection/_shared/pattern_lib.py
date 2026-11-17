"""
Shared content engine for Reasoning by Analogy -> Reflection.

Two-pair analogy format (see ../../rotation/_shared/pattern_lib.py):
first pair (A -> B) demonstrates "mirror left-right"; apply the same
rule to a second pair's starting arrow (C -> ?).

A and C are the same arrow marker at two DIFFERENT diagonal starting
angles (never the same angle, and never horizontal/vertical -- a
horizontal or vertical arrow looks IDENTICAL to its own left-right
mirror, which would make the question trivial/broken).

Mirror formulas (reflecting a direction vector (cos th, sin th)):
    left-right mirror (across a vertical line):   (180 - theta) mod 360
    top-bottom mirror (across a horizontal line):  (360 - theta) mod 360
Confirmed both algebraically and against a rendered test in Pattern
Completion's Reflection subskill.
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
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Visual Analogy"
QUESTION_TEXT = "Complete the analogy."

GRADE_LABELS = ["K", "1", "2", "3", "4"]

BASE_ANGLES = [30, 45, 60, 120, 135, 150, 210, 225, 240, 300, 315, 330]
ATTR_BASE_INDEX = {"diag1": 0, "diag2": 2, "diag3": 4, "diag4": 6, "diag5": 8}
ATTRIBUTES = list(ATTR_BASE_INDEX.keys())
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}


def mirror_lr(theta: int) -> int:
    return (180 - theta) % 360


def mirror_tb(theta: int) -> int:
    return (360 - theta) % 360


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
    def angle_a(self) -> int:
        idx = ATTR_BASE_INDEX[self.attribute] + self.palette_offset
        return BASE_ANGLES[idx % len(BASE_ANGLES)]

    @property
    def angle_c(self) -> int:
        idx = ATTR_BASE_INDEX[self.attribute] + self.palette_offset + 3
        return BASE_ANGLES[idx % len(BASE_ANGLES)]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_ref_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def angles_for(spec: PatternSpec) -> dict:
    angle_b = mirror_lr(spec.angle_a)
    correct = mirror_lr(spec.angle_c)
    return {"a": spec.angle_a, "b": angle_b, "c": spec.angle_c, "correct": correct}


def distractor_angles_for(spec: PatternSpec, angles: dict) -> list[int]:
    wrong_axis = mirror_tb(spec.angle_c)
    same_as_c = angles["c"]
    same_as_b = angles["b"]
    rotate180 = (angles["correct"] + 180) % 360

    candidates = [wrong_axis, same_as_c, same_as_b, rotate180]
    used = {angles["correct"]}
    distractors: list[int] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    salt = 1
    while len(distractors) < 4:
        cand = (angles["correct"] + salt * 25) % 360
        salt += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_angles_for(spec: PatternSpec, angles: dict) -> tuple[list[int], str]:
    distractors = distractor_angles_for(spec, angles)
    choices = distractors + [angles["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(angles["correct"])]
    return choices, correct_letter


def _arrow_marker(angle_deg: float, scale: float = 1.0):
    arrow = Arrow(
        ORIGIN, RIGHT * 0.95 * scale, buff=0, color=INK, stroke_width=8,
        max_tip_length_to_length_ratio=0.4,
    )
    arrow.rotate(angle_deg * DEGREES, about_point=arrow.get_start())
    return arrow


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_pair(left_mobj, right_mobj, buff=0.6):
    arrow = Arrow(LEFT * 0.9, RIGHT * 0.9, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.3)
    return VGroup(left_mobj, arrow, right_mobj).arrange(RIGHT, buff=buff)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=1.1):
    group = VGroup(*choices).arrange(RIGHT, buff=buff)
    full = VGroup()
    for letter, mobj in zip(labels, group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(mobj, UP, buff=0.35)
        full.add(VGroup(letter_text, mobj))
    full.move_to(ORIGIN)
    return full


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.3, stroke_width=6, corner_radius=0.12)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": QUESTION_TEXT,
        "first_pair": "In the first pair, the arrow flips into its mirror image.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "The same rule applies: flip this arrow into its mirror image too.",
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

    angles = angles_for(spec)
    pair1 = build_pair(_arrow_marker(angles["a"]), _arrow_marker(angles["b"]))
    pair2 = build_pair(_arrow_marker(angles["c"]), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.45)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_angles, _ = choice_angles_for(spec, angles)
    choices = build_choice_row([_arrow_marker(a, 0.85) for a in choice_angles])
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(pairs.width, choices.width))
    if _choice_fit < 1.0:
        pairs.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(pairs, DOWN, buff=0.9)

    _group = VGroup(title, question, pairs, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)
    scene.choice_regions = {letter: _group[-1][i] for i, letter in enumerate("ABCDE")}


class AnalogyReflectionVideoScene(VoiceoverScene):
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

        angles = angles_for(spec)
        arrow_a = _arrow_marker(angles["a"])
        arrow_b = _arrow_marker(angles["b"])
        pair1 = build_pair(arrow_a, arrow_b)
        pair1.next_to(question, DOWN, buff=2.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(arrow_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(arrow_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        arrow_c = _arrow_marker(angles["c"])
        qmark = _qmark()
        pair2 = build_pair(arrow_c, qmark)
        pair2.next_to(pair1, DOWN, buff=2.0)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_angles, correct_letter = choice_angles_for(spec, angles)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_arrow_marker(a, 0.85) for a in choice_angles])
        _choice_fit = min(1.0, (config.frame_width - 1.0) / max(VGroup(pair1, pair2).width, choices.width))
        if _choice_fit < 1.0:
            self.play(pair1.animate.scale(_choice_fit), pair2.animate.scale(_choice_fit), run_time=0.3)
            choices.scale(_choice_fit)
        choices.next_to(VGroup(pair1, pair2), DOWN, buff=2.8)

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

        resolved = _arrow_marker(angles["correct"]).move_to(qmark.get_center())
        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(qmark, scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.8)
            qmark.set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(VGroup(pair1, pair2), DOWN, buff=2.8)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, pair1, pair2, resolved, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    angles = angles_for(spec)
    choice_angles, correct_letter = choice_angles_for(spec, angles)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "reasoning_by_analogy",
        "skill": "reflection",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_ref_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "angles": angles,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
