"""
Shared content engine for Reasoning by Analogy -> Color or Shading
Change.

Two-pair analogy format: first pair (A -> B) demonstrates either
"flip filled <-> outline" (the original 3-question demo's rule) or
"shift N steps along a fixed color cycle"; apply the same rule to a
second pair's starting shape (C -> ?).

Shape identity differs between A and C (so the question can't be
answered by just copying B's shape), but the shape of the CORRECT
answer always matches C's shape -- only the varying attribute (fill or
color) changes, exactly like the original demo's circle/triangle
example.
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
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]

ATTRIBUTES = ["fill_on", "fill_off", "color_shift_1", "color_shift_2", "color_shift_3"]
DIFFICULTY_BY_GRADE = {0: 1, 1: 2, 2: 2, 3: 3, 4: 4}
NS = len(SHAPE_CYCLE)
NC = len(COLOR_CYCLE)


@dataclass(frozen=True)
class Token:
    shape: str
    color: str = INK
    fill: bool = True


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
    def mode(self) -> str:
        return "fill" if self.attribute.startswith("fill") else "color"

    @property
    def shift(self) -> int:
        return int(self.attribute[-1]) if self.mode == "color" else 0

    @property
    def shape_a(self) -> str:
        return SHAPE_CYCLE[self.palette_offset % NS]

    @property
    def shape_c(self) -> str:
        return SHAPE_CYCLE[(self.palette_offset + 3) % NS]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_csc_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def _transform(spec: PatternSpec, token: Token) -> Token:
    if spec.mode == "fill":
        return Token(token.shape, token.color, not token.fill)
    idx = next(i for i, (_, hexv) in enumerate(COLOR_CYCLE) if hexv == token.color)
    new_color = COLOR_CYCLE[(idx + spec.shift) % NC][1]
    return Token(token.shape, new_color, token.fill)


def tokens_for(spec: PatternSpec) -> dict:
    if spec.mode == "fill":
        start_fill = spec.attribute == "fill_off"
        a = Token(spec.shape_a, INK, start_fill)
        c = Token(spec.shape_c, INK, start_fill)
    else:
        color_a = COLOR_CYCLE[spec.palette_offset % NC][1]
        color_c = COLOR_CYCLE[(spec.palette_offset + 3) % NC][1]
        a = Token(spec.shape_a, color_a, True)
        c = Token(spec.shape_c, color_c, True)
    b = _transform(spec, a)
    correct = _transform(spec, c)
    return {"a": a, "b": b, "c": c, "correct": correct}


def distractor_tokens_for(spec: PatternSpec, tokens: dict) -> list[Token]:
    correct = tokens["correct"]
    same_as_c = tokens["c"]
    same_as_b = tokens["b"]
    wrong_shape = Token(tokens["a"].shape, correct.color, correct.fill)
    unrelated_shape = SHAPE_CYCLE[(SHAPE_CYCLE.index(tokens["c"].shape) + 2) % NS]
    extra = Token(unrelated_shape, correct.color, correct.fill)

    candidates = [same_as_c, same_as_b, wrong_shape, extra]
    used = {correct}
    distractors: list[Token] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    i = 0
    fallback_shapes = [s for s in SHAPE_CYCLE if s not in (tokens["a"].shape, tokens["c"].shape)]
    while len(distractors) < 4 and i < len(fallback_shapes):
        cand = Token(fallback_shapes[i], correct.color, not correct.fill)
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, tokens: dict) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, tokens)
    choices = distractors + [tokens["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(tokens["correct"])]
    return choices, correct_letter


def _build_shape(token: Token, scale: float = 1.0):
    s = 0.5 * scale
    color = token.color
    opacity = 1 if token.fill else 0
    if token.shape == "circle":
        return Circle(radius=s, color=color, stroke_width=6, fill_color=color, fill_opacity=opacity)
    if token.shape == "square":
        return Square(side_length=s * 1.8, color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
    if token.shape == "triangle":
        tri = Triangle(color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
        return tri.scale(s * 1.55)
    if token.shape == "diamond":
        d = Square(side_length=s * 1.8, color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
        return d.rotate(PI / 4)
    if token.shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                     color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
    if token.shape == "hexagon":
        return RegularPolygon(n=6, color=color, stroke_width=5, fill_color=color, fill_opacity=opacity).scale(s * 1.05)
    raise ValueError(token.shape)


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
    if spec.mode == "fill":
        rule = "changes from outline to filled" if spec.attribute == "fill_on" else "changes from filled to outline"
    else:
        rule = f"shifts {spec.shift} step{'s' if spec.shift != 1 else ''} along the color wheel"
    return {
        "intro": QUESTION_TEXT,
        "first_pair": f"In the first pair, the shape {rule}.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"The same rule applies: this shape {rule} too.",
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

    tokens = tokens_for(spec)
    pair1 = build_pair(_build_shape(tokens["a"]), _build_shape(tokens["b"]))
    pair2 = build_pair(_build_shape(tokens["c"]), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.5)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_tokens, _ = choice_tokens_for(spec, tokens)
    choices = build_choice_row([_build_shape(t, 0.85) for t in choice_tokens])
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(pairs.width, choices.width))
    if _choice_fit < 1.0:
        pairs.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(pairs, DOWN, buff=0.9)

    _group = VGroup(title, question, pairs, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class AnalogyColorShadingVideoScene(VoiceoverScene):
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

        tokens = tokens_for(spec)
        shape_a = _build_shape(tokens["a"])
        shape_b = _build_shape(tokens["b"])
        pair1 = build_pair(shape_a, shape_b)
        pair1.next_to(question, DOWN, buff=2.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(shape_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(shape_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        shape_c = _build_shape(tokens["c"])
        qmark = _qmark()
        pair2 = build_pair(shape_c, qmark)
        pair2.next_to(pair1, DOWN, buff=2.0)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_tokens, correct_letter = choice_tokens_for(spec, tokens)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_build_shape(t, 0.85) for t in choice_tokens])
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

        resolved = _build_shape(tokens["correct"]).move_to(qmark.get_center())
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
    tokens = tokens_for(spec)
    choice_tokens, correct_letter = choice_tokens_for(spec, tokens)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "reasoning_by_analogy",
        "skill": "color_shading_change",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_csc_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "mode": spec.mode,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
