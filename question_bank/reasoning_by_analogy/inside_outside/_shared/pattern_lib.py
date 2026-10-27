"""
Shared content engine for Reasoning by Analogy -> Inside-Outside
Transformation.

Two-pair analogy format: a fixed container shape stays constant within
a question; a small dot sits at a given angle around it, either just
OUTSIDE or just INSIDE the boundary. First pair (A -> B) demonstrates
"move from outside to inside" (or the reverse); apply the same
direction to a second pair's starting dot (C -> ?). A and C sit at
DIFFERENT angles so the question can't be answered by copying B.
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
ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]

# attribute -> (container shape, direction: "out_to_in" | "in_to_out")
CONFIG_BY_ATTR = {
    "out_to_in_circle": ("circle", "out_to_in"),
    "in_to_out_circle": ("circle", "in_to_out"),
    "out_to_in_square": ("square", "out_to_in"),
    "in_to_out_triangle": ("triangle", "in_to_out"),
    "out_to_in_star": ("star", "out_to_in"),
}
ATTRIBUTES = list(CONFIG_BY_ATTR.keys())
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}


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
    def container_shape(self) -> str:
        return CONFIG_BY_ATTR[self.attribute][0]

    @property
    def direction(self) -> str:
        return CONFIG_BY_ATTR[self.attribute][1]

    @property
    def angle_a(self) -> int:
        return ANGLES[self.palette_offset % len(ANGLES)]

    @property
    def angle_c(self) -> int:
        return ANGLES[(self.palette_offset + 4) % len(ANGLES)]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_io_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def tokens_for(spec: PatternSpec) -> dict:
    start_loc, end_loc = ("outside", "inside") if spec.direction == "out_to_in" else ("inside", "outside")
    a = (spec.angle_a, start_loc)
    b = (spec.angle_a, end_loc)
    c = (spec.angle_c, start_loc)
    correct = (spec.angle_c, end_loc)
    return {"a": a, "b": b, "c": c, "correct": correct, "start_loc": start_loc, "end_loc": end_loc}


def distractor_tokens_for(spec: PatternSpec, tokens: dict) -> list[tuple[int, str]]:
    same_as_c = tokens["c"]
    same_as_b = tokens["b"]
    wrong_direction = (tokens["c"][0], tokens["start_loc"])  # stayed/moved away instead of in
    on_edge = (tokens["c"][0], "edge")

    candidates = [same_as_c, same_as_b, wrong_direction, on_edge]
    used = {tokens["correct"]}
    distractors: list[tuple[int, str]] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    i = 0
    fallback_angles = [a for a in ANGLES if a not in (tokens["a"][0], tokens["c"][0])]
    while len(distractors) < 4 and i < len(fallback_angles):
        cand = (fallback_angles[i], tokens["end_loc"])
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, tokens: dict) -> tuple[list[tuple[int, str]], str]:
    distractors = distractor_tokens_for(spec, tokens)
    choices = distractors + [tokens["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(tokens["correct"])]
    return choices, correct_letter


def _build_container(shape: str, scale: float = 1.0):
    s = 0.55 * scale
    if shape == "circle":
        return Circle(radius=s, color=INK, stroke_width=6, fill_opacity=0)
    if shape == "square":
        return Square(side_length=s * 1.8, color=INK, stroke_width=6, fill_opacity=0)
    if shape == "triangle":
        return Triangle(color=INK, stroke_width=6, fill_opacity=0).scale(s * 1.6)
    if shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5, color=INK, stroke_width=6, fill_opacity=0)
    raise ValueError(shape)


def _container_radius_at(shape: str, scale: float) -> float:
    # Approximate "edge distance from center" used to place the dot; doesn't
    # need to be exact for every shape, just consistent enough that inside
    # vs. outside vs. edge are visually unambiguous.
    return 0.5 * scale if shape != "triangle" else 0.4 * scale


def _build_token(shape: str, token: tuple[int, str], scale: float = 1.0):
    container = _build_container(shape, scale)
    angle, loc = token
    r = _container_radius_at(shape, scale)
    radius = {"inside": r * 0.5, "edge": r * 1.0, "outside": r * 1.6}[loc]
    dot = Circle(radius=0.08 * scale, color=ACCENT, stroke_width=0, fill_color=ACCENT, fill_opacity=1)
    dot.move_to(container.get_center() + radius * rotate_vector(RIGHT, angle * DEGREES))
    return VGroup(container, dot)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_pair(left_mobj, right_mobj, buff=0.6):
    arrow = Arrow(LEFT * 0.9, RIGHT * 0.9, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.3)
    return VGroup(left_mobj, arrow, right_mobj).arrange(RIGHT, buff=buff)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=0.6):
    group = VGroup(*choices).arrange(RIGHT, buff=buff)
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
    verb = "moves from outside to inside" if spec.direction == "out_to_in" else "moves from inside to outside"
    return {
        "intro": QUESTION_TEXT,
        "first_pair": f"In the first pair, the dot {verb} the shape.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"The same rule applies: the dot {verb} again.",
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

    tokens = tokens_for(spec)
    pair1 = build_pair(_build_token(spec.container_shape, tokens["a"]), _build_token(spec.container_shape, tokens["b"]))
    pair2 = build_pair(_build_token(spec.container_shape, tokens["c"]), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.5)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_tokens, _ = choice_tokens_for(spec, tokens)
    choices = build_choice_row([_build_token(spec.container_shape, t, 0.8) for t in choice_tokens])
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(pairs.width, choices.width))
    if _choice_fit < 1.0:
        pairs.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(pairs, DOWN, buff=0.9)

    _group = VGroup(title, question, pairs, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class AnalogyInsideOutsideVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)

        with self.voiceover(text=narration_lines(spec, "")["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        tokens = tokens_for(spec)
        mobj_a = _build_token(spec.container_shape, tokens["a"])
        mobj_b = _build_token(spec.container_shape, tokens["b"])
        pair1 = build_pair(mobj_a, mobj_b)
        pair1.move_to(ORIGIN).shift(UP * 1.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(mobj_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(mobj_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        mobj_c = _build_token(spec.container_shape, tokens["c"])
        qmark = _qmark()
        pair2 = build_pair(mobj_c, qmark)
        pair2.move_to(ORIGIN).shift(DOWN * 0.6)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_tokens, correct_letter = choice_tokens_for(spec, tokens)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_build_token(spec.container_shape, t, 0.8) for t in choice_tokens])
        _choice_fit = min(1.0, (config.frame_width - 1.0) / max(VGroup(pair1, pair2).width, choices.width))
        if _choice_fit < 1.0:
            self.play(pair1.animate.scale(_choice_fit), pair2.animate.scale(_choice_fit), run_time=0.3)
            choices.scale(_choice_fit)
        choices.next_to(VGroup(pair1, pair2), DOWN, buff=0.9)

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

        resolved = _build_token(spec.container_shape, tokens["correct"]).move_to(qmark.get_center())
        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(qmark, scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.8)
            qmark.set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(VGroup(pair1, pair2), DOWN, buff=0.6)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, pair1, pair2, resolved, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    tokens = tokens_for(spec)
    choice_tokens, correct_letter = choice_tokens_for(spec, tokens)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "reasoning_by_analogy",
        "skill": "inside_outside",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_io_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "direction": spec.direction,
        "container_shape": spec.container_shape,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
