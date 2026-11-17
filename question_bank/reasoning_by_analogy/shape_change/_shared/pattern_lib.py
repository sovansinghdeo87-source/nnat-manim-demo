"""
Shared content engine for Reasoning by Analogy -> Shape Change.

Two-pair analogy format: first pair (A -> B) demonstrates "shift N
positions forward along a fixed shape cycle" (circle -> square ->
triangle -> diamond -> star -> hexagon -> back to circle); apply the
same shift to a second pair's starting shape (C -> ?).

A fixed CYCLE (not a single hardcoded pair substitution) is used
deliberately: a literal fixed pair like "circle always becomes square"
would force A and C to both be circles for the rule to even apply,
which breaks the "A and C must differ" guard against copy-shortcuts.
Shifting along a shared cycle lets A and C be different shapes while
still testing the same abstract rule -- consistent with how Rotation
(shift angle) and Size Change (shift size level) are modeled.
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
SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]

SHIFT_BY_ATTR = {"shift_1": 1, "shift_2": 2, "shift_3": 3, "shift_4": 4, "shift_5": 5}
ATTRIBUTES = list(SHIFT_BY_ATTR.keys())
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}
N = len(SHAPE_CYCLE)


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
    def shift(self) -> int:
        return SHIFT_BY_ATTR[self.attribute]

    @property
    def idx_a(self) -> int:
        return self.palette_offset % N

    @property
    def idx_c(self) -> int:
        return (self.palette_offset + 3) % N

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_shc_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def shapes_for(spec: PatternSpec) -> dict:
    idx_b = (spec.idx_a + spec.shift) % N
    idx_correct = (spec.idx_c + spec.shift) % N
    return {
        "a": SHAPE_CYCLE[spec.idx_a], "b": SHAPE_CYCLE[idx_b],
        "c": SHAPE_CYCLE[spec.idx_c], "correct": SHAPE_CYCLE[idx_correct],
        "idx_a": spec.idx_a, "idx_b": idx_b, "idx_c": spec.idx_c, "idx_correct": idx_correct,
    }


def distractor_shapes_for(spec: PatternSpec, shapes: dict) -> list[str]:
    same_as_c = shapes["c"]
    same_as_b = shapes["b"]
    wrong_direction = SHAPE_CYCLE[(shapes["idx_c"] - spec.shift) % N]
    wrong_shift = SHAPE_CYCLE[(shapes["idx_c"] + spec.shift + 1) % N]

    candidates = [same_as_c, same_as_b, wrong_direction, wrong_shift]
    used = {shapes["correct"]}
    distractors: list[str] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    i = 0
    while len(distractors) < 4 and i < N:
        cand = SHAPE_CYCLE[i]
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_shapes_for(spec: PatternSpec, shapes: dict) -> tuple[list[str], str]:
    distractors = distractor_shapes_for(spec, shapes)
    choices = distractors + [shapes["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(shapes["correct"])]
    return choices, correct_letter


def _build_shape(shape: str, scale: float = 1.0, color: str = INK):
    s = 0.5 * scale
    if shape == "circle":
        return Circle(radius=s, color=color, stroke_width=6, fill_color=color, fill_opacity=1)
    if shape == "square":
        return Square(side_length=s * 1.8, color=color, stroke_width=5, fill_color=color, fill_opacity=1)
    if shape == "triangle":
        tri = Triangle(color=color, stroke_width=5, fill_color=color, fill_opacity=1)
        return tri.scale(s * 1.55)
    if shape == "diamond":
        d = Square(side_length=s * 1.8, color=color, stroke_width=5, fill_color=color, fill_opacity=1)
        return d.rotate(PI / 4)
    if shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                     color=color, stroke_width=5, fill_color=color, fill_opacity=1)
    if shape == "hexagon":
        return RegularPolygon(n=6, color=color, stroke_width=5, fill_color=color, fill_opacity=1).scale(s * 1.05)
    raise ValueError(shape)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_pair(left_mobj, right_mobj, buff=0.6):
    arrow = Arrow(LEFT * 0.9, RIGHT * 0.9, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.3)
    return VGroup(left_mobj, arrow, right_mobj).arrange(RIGHT, buff=buff)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=1.0):
    group = VGroup(*choices).arrange(RIGHT, buff=buff)
    full = VGroup()
    for letter, mobj in zip(labels, group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(mobj, UP, buff=0.3)
        full.add(VGroup(letter_text, mobj))
    full.move_to(ORIGIN)
    return full


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.3, stroke_width=6, corner_radius=0.12)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    return {
        "intro": QUESTION_TEXT,
        "first_pair": "In the first pair, the shape changes into a different shape.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "The same rule applies: change this shape the same way.",
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

    shapes = shapes_for(spec)
    pair1 = build_pair(_build_shape(shapes["a"]), _build_shape(shapes["b"]))
    pair2 = build_pair(_build_shape(shapes["c"]), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.5)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_shapes, _ = choice_shapes_for(spec, shapes)
    choices = build_choice_row([_build_shape(s, 0.85) for s in choice_shapes])
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


class AnalogyShapeChangeVideoScene(VoiceoverScene):
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

        shapes = shapes_for(spec)
        shape_a = _build_shape(shapes["a"])
        shape_b = _build_shape(shapes["b"])
        pair1 = build_pair(shape_a, shape_b)
        pair1.next_to(question, DOWN, buff=2.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(shape_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(shape_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        shape_c = _build_shape(shapes["c"])
        qmark = _qmark()
        pair2 = build_pair(shape_c, qmark)
        pair2.next_to(pair1, DOWN, buff=2.0)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_shapes, correct_letter = choice_shapes_for(spec, shapes)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_build_shape(s, 0.85) for s in choice_shapes])
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

        resolved = _build_shape(shapes["correct"]).move_to(qmark.get_center())
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
    shapes = shapes_for(spec)
    choice_shapes, correct_letter = choice_shapes_for(spec, shapes)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "reasoning_by_analogy",
        "skill": "shape_change",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_shc_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "shift": spec.shift,
        "shapes": shapes,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
