"""
Shared content engine for Reasoning by Analogy -> Combined
Transformations.

Two-pair analogy format where TWO rules apply simultaneously -- e.g.
the arrow both rotates AND changes color at once. First pair (A -> B)
demonstrates both rules; apply both to a second pair's starting figure
(C -> ?). A and C start at different combined states so the question
can't be answered by copying B.

Five combos, each pairing two of four transform dimensions
(rotate/color/size/fill). When "rotate" is active the marker is an
arrow (so the rotation is always visible); otherwise it's a plain
circle.
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
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]
SIZE_LEVELS = [0.7, 0.9, 1.1, 1.3]

COMBO_BY_ATTR = {
    "rotate_color": ("rotate", "color"),
    "rotate_size": ("rotate", "size"),
    "rotate_fill": ("rotate", "fill"),
    "color_size": ("color", "size"),
    "size_fill": ("size", "fill"),
}
ATTRIBUTES = list(COMBO_BY_ATTR.keys())
DIFFICULTY_BY_GRADE = {0: 2, 1: 3, 2: 3, 3: 4, 4: 5}  # inherently harder: 2 rules at once


@dataclass(frozen=True)
class Token:
    angle: int = 0
    color: str = INK
    fill: bool = True
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
    def dims(self) -> tuple[str, str]:
        return COMBO_BY_ATTR[self.attribute]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_cmb_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def _state_at(idx: int, dims: tuple[str, str]) -> Token:
    kwargs = {}
    for i, dim in enumerate(dims):
        j = idx + i * 2
        if dim == "rotate":
            kwargs["angle"] = ANGLES[j % len(ANGLES)]
        elif dim == "color":
            kwargs["color"] = COLOR_CYCLE[j % len(COLOR_CYCLE)][1]
        elif dim == "size":
            kwargs["size_scale"] = SIZE_LEVELS[j % len(SIZE_LEVELS)]
        elif dim == "fill":
            kwargs["fill"] = bool(j % 2)
    return Token(**kwargs)


def _apply_delta(token: Token, dim: str) -> Token:
    if dim == "rotate":
        return Token((token.angle + 90) % 360, token.color, token.fill, token.size_scale)
    if dim == "color":
        idx = next(i for i, (_, hexv) in enumerate(COLOR_CYCLE) if hexv == token.color)
        return Token(token.angle, COLOR_CYCLE[(idx + 1) % len(COLOR_CYCLE)][1], token.fill, token.size_scale)
    if dim == "size":
        idx = SIZE_LEVELS.index(token.size_scale)
        return Token(token.angle, token.color, token.fill, SIZE_LEVELS[(idx + 1) % len(SIZE_LEVELS)])
    if dim == "fill":
        return Token(token.angle, token.color, not token.fill, token.size_scale)
    raise ValueError(dim)


def _transform(token: Token, dims: tuple[str, str]) -> Token:
    for dim in dims:
        token = _apply_delta(token, dim)
    return token


def tokens_for(spec: PatternSpec) -> dict:
    dims = spec.dims
    a = _state_at(spec.palette_offset, dims)
    c = _state_at(spec.palette_offset + 5, dims)
    b = _transform(a, dims)
    correct = _transform(c, dims)
    return {"a": a, "b": b, "c": c, "correct": correct}


def distractor_tokens_for(spec: PatternSpec, tokens: dict) -> list[Token]:
    dims = spec.dims
    same_as_c = tokens["c"]
    same_as_b = tokens["b"]
    only_first = _apply_delta(tokens["c"], dims[0])     # one rule applied, not the other
    only_second = _apply_delta(tokens["c"], dims[1])

    candidates = [same_as_c, same_as_b, only_first, only_second]
    used = {tokens["correct"]}
    distractors: list[Token] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    # Bounded fallback: apply both deltas twice more (fixed, finite list).
    fallback_sources = [tokens["a"], tokens["b"], tokens["c"], tokens["correct"]]
    i = 0
    while len(distractors) < 4 and i < len(fallback_sources):
        cand = _transform(_transform(fallback_sources[i], dims), dims)
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, tokens: dict) -> tuple[list[Token], str]:
    distractors = distractor_tokens_for(spec, tokens)
    choices = distractors + [tokens["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(tokens["correct"])]
    return choices, correct_letter


def _build_marker(token: Token, dims: tuple[str, str], scale: float = 1.0):
    if "rotate" in dims:
        length = 0.95 * scale * (token.size_scale if "size" in dims else 1.0)
        arrow = Arrow(ORIGIN, RIGHT * length, buff=0, color=token.color, stroke_width=8,
                      max_tip_length_to_length_ratio=0.4)
        arrow.rotate(token.angle * DEGREES, about_point=arrow.get_start())
        return arrow
    s = 0.5 * scale * token.size_scale
    return Circle(radius=s, color=token.color, stroke_width=6,
                  fill_color=token.color, fill_opacity=1 if token.fill else 0)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_pair(left_mobj, right_mobj, buff=0.6):
    arrow = Arrow(LEFT * 0.9, RIGHT * 0.9, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.3)
    return VGroup(left_mobj, arrow, right_mobj).arrange(RIGHT, buff=buff)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=0.7):
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


_DIM_PHRASE = {"rotate": "turns", "color": "changes color", "size": "changes size", "fill": "flips filled/outline"}


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    d1, d2 = spec.dims
    rule = f"{_DIM_PHRASE[d1]} AND {_DIM_PHRASE[d2]}"
    return {
        "intro": QUESTION_TEXT,
        "first_pair": f"In the first pair, two things happen at once: it {rule}.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "Both rules apply again -- not just one.",
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
    dims = spec.dims
    pair1 = build_pair(_build_marker(tokens["a"], dims), _build_marker(tokens["b"], dims))
    pair2 = build_pair(_build_marker(tokens["c"], dims), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.5)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_tokens, _ = choice_tokens_for(spec, tokens)
    choices = build_choice_row([_build_marker(t, dims, 0.85) for t in choice_tokens])
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(pairs.width, choices.width))
    if _choice_fit < 1.0:
        pairs.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(pairs, DOWN, buff=0.9)

    _group = VGroup(title, question, pairs, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class AnalogyCombinedVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))
        dims = spec.dims

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.35)

        with self.voiceover(text=narration_lines(spec, "")["intro"]) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        tokens = tokens_for(spec)
        mobj_a = _build_marker(tokens["a"], dims)
        mobj_b = _build_marker(tokens["b"], dims)
        pair1 = build_pair(mobj_a, mobj_b)
        pair1.move_to(ORIGIN).shift(UP * 1.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(mobj_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(mobj_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        mobj_c = _build_marker(tokens["c"], dims)
        qmark = _qmark()
        pair2 = build_pair(mobj_c, qmark)
        pair2.move_to(ORIGIN).shift(DOWN * 0.6)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_tokens, correct_letter = choice_tokens_for(spec, tokens)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_build_marker(t, dims, 0.85) for t in choice_tokens])
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

        resolved = _build_marker(tokens["correct"], dims).move_to(qmark.get_center())
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
        "skill": "combined_transformations",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_cmb_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "dims": spec.dims,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
