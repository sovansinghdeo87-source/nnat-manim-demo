"""
Shared content engine for Pattern Completion -> Color or Shading
Continuation.

Unlike Repeating/Alternating Patterns (cyclic), this subskill is a
MONOTONIC progression: each step gets a little darker, or a little
further along a color gradient, and the answer continues that trend by
one more step (never wraps back around).

Five attribute themes (one per base question):
    shade_darker   -- same shape/hue, opacity increases step by step
    shade_lighter  -- same shape/hue, opacity decreases step by step
    hue_warm       -- color walks along a pale-yellow -> deep-maroon gradient
    hue_cool       -- color walks along a pale-cyan -> deep-violet gradient
    intensity_pink -- color walks along a pale-pink -> deep-magenta gradient
"""

from __future__ import annotations

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

SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
GRADE_LABELS = ["K", "1", "2", "3", "4"]
ATTRIBUTES = ["shade_darker", "shade_lighter", "hue_warm", "hue_cool", "intensity_pink"]

GRADIENT_LEN = 10


def _lerp_color(hex1: str, hex2: str, t: float) -> str:
    r1, g1, b1 = int(hex1[1:3], 16), int(hex1[3:5], 16), int(hex1[5:7], 16)
    r2, g2, b2 = int(hex2[1:3], 16), int(hex2[3:5], 16), int(hex2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def _gradient(hex1: str, hex2: str, n: int) -> list[str]:
    return [_lerp_color(hex1, hex2, i / (n - 1)) for i in range(n)]


WARM_GRADIENT = _gradient("#FEF08A", "#7F1D1D", GRADIENT_LEN)
COOL_GRADIENT = _gradient("#CFFAFE", "#4C1D95", GRADIENT_LEN)
PINK_GRADIENT = _gradient("#FCE7F3", "#831843", GRADIENT_LEN)
SHADE_LEVELS = [round(0.08 + i * (1.0 - 0.08) / (GRADIENT_LEN - 1), 3) for i in range(GRADIENT_LEN)]

DISPLAYED_COUNT_BY_GRADE = {0: 3, 1: 3, 2: 4, 3: 4, 4: 5}
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
    def displayed_count(self) -> int:
        return DISPLAYED_COUNT_BY_GRADE[self.grade_rank]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"pc_csc_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base

    @property
    def start_index(self) -> int:
        needed = self.displayed_count + 3  # shown + correct + 2 overshoot headroom
        safe_range = max(1, GRADIENT_LEN - needed)
        return self.palette_offset % safe_range

    @property
    def shape(self) -> str:
        return SHAPE_CYCLE[self.palette_offset % len(SHAPE_CYCLE)]

    @property
    def other_shape(self) -> str:
        return SHAPE_CYCLE[(self.palette_offset + 1) % len(SHAPE_CYCLE)]


@dataclass(frozen=True)
class Token:
    shape: str
    color: str
    opacity: float = 1.0


def _effective_sequence(spec: PatternSpec) -> list[str] | list[float]:
    if spec.attribute == "shade_darker":
        return SHADE_LEVELS
    if spec.attribute == "shade_lighter":
        return SHADE_LEVELS[::-1]
    if spec.attribute == "hue_warm":
        return WARM_GRADIENT
    if spec.attribute == "hue_cool":
        return COOL_GRADIENT
    if spec.attribute == "intensity_pink":
        return PINK_GRADIENT
    raise ValueError(spec.attribute)


def _token_at(spec: PatternSpec, seq, index: int) -> Token:
    value = seq[index]
    if spec.attribute in ("shade_darker", "shade_lighter"):
        return Token(shape=spec.shape, color=INK, opacity=value)
    return Token(shape=spec.shape, color=value, opacity=1.0)


def sequence_for(spec: PatternSpec) -> tuple[list[Token], Token, "PatternSpec"]:
    seq = _effective_sequence(spec)
    start = spec.start_index
    shown = [_token_at(spec, seq, start + i) for i in range(spec.displayed_count)]
    correct = _token_at(spec, seq, start + spec.displayed_count)
    return shown, correct, seq


def distractor_tokens_for(spec: PatternSpec, shown: list[Token], correct: Token, seq) -> list[Token]:
    start = spec.start_index
    n = spec.displayed_count

    overshoot1 = _token_at(spec, seq, start + n + 1)
    overshoot2 = _token_at(spec, seq, min(start + n + 2, GRADIENT_LEN - 1))
    undershoot = shown[-1]  # "no change" -- repeats the last shown step
    far_away = _token_at(spec, seq, 0 if start > 1 else GRADIENT_LEN - 1)
    wrong_shape = Token(shape=spec.other_shape, color=correct.color, opacity=correct.opacity)

    hard = spec.grade_rank >= 3
    candidates = [overshoot1, wrong_shape, overshoot2 if hard else far_away, undershoot]

    used = {correct, *shown}
    distractors: list[Token] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    # fallback fillers if any collided away
    fallback_pool = [far_away, overshoot1, overshoot2, undershoot,
                      Token(shape=spec.other_shape, color=INK, opacity=0.5)]
    i = 0
    while len(distractors) < 4 and i < len(fallback_pool):
        cand = fallback_pool[i]
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)
    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_tokens_for(spec: PatternSpec, shown: list[Token], correct: Token, seq) -> tuple[list[Token], str]:
    import random
    distractors = distractor_tokens_for(spec, shown, correct, seq)
    choices = distractors + [correct]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(correct)]
    return choices, correct_letter


def _build_shape(token: Token, base_scale: float = 1.0):
    s = 0.55 * base_scale
    if token.shape == "circle":
        return Circle(radius=s, color=token.color, stroke_width=6,
                       fill_color=token.color, fill_opacity=token.opacity)
    if token.shape == "square":
        return Square(side_length=s * 1.8, color=token.color, stroke_width=5,
                       fill_color=token.color, fill_opacity=token.opacity)
    if token.shape == "triangle":
        tri = Triangle(color=token.color, stroke_width=5)
        tri.set_fill(token.color, opacity=token.opacity)
        return tri.scale(s * 1.55)
    if token.shape == "diamond":
        d = Square(side_length=s * 1.8, color=token.color, stroke_width=5,
                    fill_color=token.color, fill_opacity=token.opacity)
        return d.rotate(PI / 4)
    if token.shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                     color=token.color, stroke_width=5,
                     fill_color=token.color, fill_opacity=token.opacity)
    if token.shape == "hexagon":
        return RegularPolygon(n=6, color=token.color, stroke_width=5,
                               fill_color=token.color, fill_opacity=token.opacity).scale(s * 1.05)
    raise ValueError(token.shape)


def _qmark(scale: float = 1.0):
    return Text("?", font_size=int(56 * scale), color=ACCENT, weight=BOLD)


MAX_SEQUENCE_WIDTH = 12.0


def build_sequence_group(spec: PatternSpec):
    shown, correct, seq = sequence_for(spec)
    mobjs = [_build_shape(t, 1.0) for t in shown] + [_qmark(1.0)]
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

    return row, arrows, mobjs, shown, correct, seq, item_scale


def build_choice_group(spec: PatternSpec, shown: list[Token], correct: Token, seq):
    choices, correct_letter = choice_tokens_for(spec, shown, correct, seq)
    shapes = [_build_shape(t, 0.75) for t in choices]
    group = VGroup(*shapes).arrange(RIGHT, buff=1.3)

    full = VGroup()
    for letter, shape in zip("ABCDE", group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(shape, UP, buff=0.35)
        full.add(VGroup(letter_text, shape))
    full.move_to(ORIGIN)
    _max_w = min(12, config.frame_width - 1.0)
    if full.width > _max_w:
        full.scale(_max_w / full.width)
    return full, correct_letter


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.28, stroke_width=6, corner_radius=0.12)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


_TREND_PHRASES = {
    "shade_darker": "each shape gets a little darker",
    "shade_lighter": "each shape gets a little lighter",
    "hue_warm": "the color shifts a little further toward deep red",
    "hue_cool": "the color shifts a little further toward deep violet",
    "intensity_pink": "the pink gets a little more intense",
}


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    trend = _TREND_PHRASES[spec.attribute]
    return {
        "intro": QUESTION_TEXT,
        "sequence": f"Watch the trend: {trend} at every step.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": "The next shape just continues that trend.",
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

    row, arrows, _, shown, correct, seq, item_scale = build_sequence_group(spec)
    sequence_group = VGroup(row, arrows)
    sequence_group.move_to(ORIGIN).shift(UP * 0.6)

    choices, _ = build_choice_group(spec, shown, correct, seq)
    choices.next_to(sequence_group, DOWN, buff=1.3)

    _group = VGroup(title, question, sequence_group, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class ColorShadingVideoScene(VoiceoverScene):
    SPEC: Optional[PatternSpec] = None

    def construct(self):
        spec = self.SPEC
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title()
        question = make_question().next_to(title, DOWN, buff=0.55)

        row, arrows, mobjs, shown, correct, seq, item_scale = build_sequence_group(spec)
        sequence_group = VGroup(row, arrows)
        sequence_group.next_to(question, DOWN, buff=2.4)
        choices, correct_letter = build_choice_group(spec, shown, correct, seq)
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

        resolved = _build_shape(correct, item_scale)
        resolved.move_to(mobjs[-1].get_center())
        explain = Text(
            "the trend keeps going",
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
    shown, correct, seq = sequence_for(spec)
    choices, correct_letter = choice_tokens_for(spec, shown, correct, seq)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "pattern_completion",
        "skill": "color_shading_continuation",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"pc_csc_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "trend": _TREND_PHRASES[spec.attribute],
        "explanation_script": [
            lines["intro"], lines["sequence"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
