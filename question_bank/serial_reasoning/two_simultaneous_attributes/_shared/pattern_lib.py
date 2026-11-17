"""
Shared content engine for Serial Reasoning -> Two Simultaneous Attributes.

Same "row of three boxed cells, one blank" format as Row Sequences, but
TWO attributes advance together at every step instead of one (e.g.
shape AND color both cycle forward in lockstep). The skill being
tested is specifically whether a student tracks BOTH moving parts --
the most common mistake is correctly tracking one attribute while
"forgetting" the other (leaving it frozen at a neighboring cell's
value), so that is the headline distractor type here, not just an
off-by-one step.
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
ANSWER_SIZE = 40

AZURE_VOICE = "en-US-JennyNeural"
TITLE_TEXT = "Serial Reasoning"
QUESTION_TEXT = "Which figure completes the row?"

GRADE_LABELS = ["K", "1", "2", "3", "4"]
SHAPE_CYCLE = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
COLOR_CYCLE = [
    ("red", "#E4572E"), ("orange", "#F59E0B"), ("purple", "#7C3AED"),
    ("teal", "#0D9488"), ("pink", "#EC4899"), ("yellow", "#EAB308"),
]
SIZE_LEVELS = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6]

ATTRIBUTES = ["shape_color", "shape_size", "color_size", "shape_fill", "color_fill"]
ATTR_PARTS = {
    "shape_color": ("shape", "color"),
    "shape_size": ("shape", "size"),
    "color_size": ("color", "size"),
    "shape_fill": ("shape", "fill"),
    "color_fill": ("color", "fill"),
}
# position of the blank cell (0=first, 1=middle, 2=last), by grade
BLANK_POS_BY_GRADE = {0: 2, 1: 2, 2: 0, 3: 2, 4: 1}
DIFFICULTY_BY_GRADE = {0: 2, 1: 2, 2: 4, 3: 3, 4: 5}


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
    def blank_pos(self) -> int:
        pos = BLANK_POS_BY_GRADE[self.grade_rank]
        if pos == 1 and "fill" in ATTR_PARTS[self.attribute]:
            # A boolean (2-state) attribute is always the SAME at positions
            # 0 and 2 (they're 2 steps apart -> same parity), regardless of
            # whether it's constant or toggling every step. With the blank
            # in the middle, the two visible cells can never distinguish
            # "always on" from "toggles every step" -- genuinely unsolvable.
            # Fall back to the last position, where the visible 0/1 pair
            # directly shows a real transition.
            return 2
        return pos

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"sr_two_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def _part_value(part: str, i: int):
    if part == "shape":
        return SHAPE_CYCLE[i % len(SHAPE_CYCLE)]
    if part == "color":
        return COLOR_CYCLE[i % len(COLOR_CYCLE)][1]
    if part == "size":
        return SIZE_LEVELS[i % len(SIZE_LEVELS)]
    if part == "fill":
        return i % 2 == 0
    raise ValueError(part)


def _compose(spec: PatternSpec, part_a_val, part_b_val) -> tuple:
    part_a, part_b = ATTR_PARTS[spec.attribute]
    shape, color, fill, size_scale, angle = "circle", INK, True, 1.0, 0
    for part, val in ((part_a, part_a_val), (part_b, part_b_val)):
        if part == "shape":
            shape = val
        elif part == "color":
            color = val
        elif part == "size":
            size_scale = val
        elif part == "fill":
            fill = val
    return (shape, color, fill, size_scale, angle)


def _value_at(spec: PatternSpec, step: int) -> tuple:
    i = spec.palette_offset + step
    part_a, part_b = ATTR_PARTS[spec.attribute]
    return _compose(spec, _part_value(part_a, i), _part_value(part_b, i))


def row_values_for(spec: PatternSpec) -> dict:
    cells = [_value_at(spec, i) for i in range(3)]
    return {"cells": cells, "correct": cells[spec.blank_pos]}


def distractor_values_for(spec: PatternSpec, row: dict) -> list[tuple]:
    pos = spec.blank_pos
    correct = row["correct"]
    other_visible = [row["cells"][i] for i in range(3) if i != pos]

    anchor_step = pos - 1 if pos > 0 else pos + 1
    part_a, part_b = ATTR_PARTS[spec.attribute]
    i_correct = spec.palette_offset + pos
    i_anchor = spec.palette_offset + anchor_step

    forgot_a = _compose(spec, _part_value(part_a, i_anchor), _part_value(part_b, i_correct))
    forgot_b = _compose(spec, _part_value(part_a, i_correct), _part_value(part_b, i_anchor))
    adjacent = _value_at(spec, pos + 1)
    unrelated = _value_at(spec, pos + 7)

    candidates = [forgot_a, forgot_b, adjacent, unrelated] + other_visible
    used = {correct}
    distractors: list[tuple] = []
    for cand in candidates:
        if cand not in used and cand not in distractors:
            distractors.append(cand)
        if len(distractors) == 4:
            break

    shape, color, fill, size_scale, angle = correct
    i = 0
    while len(distractors) < 4 and i < len(SHAPE_CYCLE):
        cand = (SHAPE_CYCLE[i], color, fill, size_scale, angle)
        i += 1
        if cand not in used and cand not in distractors:
            distractors.append(cand)

    if len(distractors) < 4:
        raise RuntimeError(f"Could not generate 4 unique distractors for {spec.question_id}")
    return distractors[:4]


def choice_values_for(spec: PatternSpec, row: dict) -> tuple[list[tuple], str]:
    distractors = distractor_values_for(spec, row)
    choices = distractors + [row["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(row["correct"])]
    return choices, correct_letter


def _build_marker(value: tuple, scale: float = 1.0):
    shape, color, fill, size_scale, angle = value
    s = 0.45 * scale * size_scale
    opacity = 1 if fill else 0
    if shape == "circle":
        return Circle(radius=s, color=color, stroke_width=6, fill_color=color, fill_opacity=opacity)
    if shape == "square":
        return Square(side_length=s * 1.8, color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
    if shape == "triangle":
        return Triangle(color=color, stroke_width=5, fill_color=color, fill_opacity=opacity).scale(s * 1.10)
    if shape == "diamond":
        return Square(side_length=s * 1.35, color=color, stroke_width=5,
                       fill_color=color, fill_opacity=opacity).rotate(PI / 4)
    if shape == "star":
        return Star(n=5, outer_radius=s * 1.1, inner_radius=s * 0.5,
                     color=color, stroke_width=5, fill_color=color, fill_opacity=opacity)
    if shape == "hexagon":
        return RegularPolygon(n=6, color=color, stroke_width=5,
                               fill_color=color, fill_opacity=opacity).scale(s * 1.05)
    raise ValueError(shape)


def _build_cell(value: Optional[tuple], scale: float = 1.0, is_blank: bool = False):
    box = Square(side_length=1.0 * scale, color=INK, stroke_width=5, fill_opacity=0)
    if is_blank:
        content = Text("?", font_size=int(48 * scale), color=ACCENT, weight=BOLD)
    else:
        content = _build_marker(value, scale)
    content.move_to(box.get_center())
    return VGroup(box, content)


def make_title():
    return Text(TITLE_TEXT, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question():
    return Text(QUESTION_TEXT, font_size=QUESTION_SIZE, color=INK)


def build_row(spec: PatternSpec, row: dict, scale: float = 1.0):
    cells = []
    for i in range(3):
        is_blank = i == spec.blank_pos
        cells.append(_build_cell(row["cells"][i], scale, is_blank))
    return VGroup(*cells).arrange(RIGHT, buff=0.5 * scale)


def build_choice_row(choices: list, labels=("A", "B", "C", "D", "E"), buff=0.7):
    group = VGroup(*[_build_marker(c, 0.85) for c in choices]).arrange(RIGHT, buff=buff)
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
    return SurroundingRectangle(mobj, color=color, buff=0.25, stroke_width=6, corner_radius=0.1)


_POS_WORD = {0: "first", 1: "middle", 2: "last"}


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    pos_word = _POS_WORD[spec.blank_pos]
    return {
        "intro": QUESTION_TEXT,
        "row": f"Two things change together each step. The {pos_word} box is missing.",
        "choices": "Here are the five answer choices, A through E.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"Both rules together decide the {pos_word} box -- not just one of them.",
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

    row = row_values_for(spec)
    row_group = build_row(spec, row)
    row_group.next_to(question, DOWN, buff=0.7)

    choices, _ = choice_values_for(spec, row)
    choice_group = build_choice_row(choices)
    choice_group.next_to(row_group, DOWN, buff=2.8)

    _group = VGroup(title, question, row_group, choice_group)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)
    scene.choice_regions = {letter: _group[-1][i] for i, letter in enumerate("ABCDE")}


class TwoSimultaneousAttributesVideoScene(VoiceoverScene):
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

        row = row_values_for(spec)
        row_group = build_row(spec, row)
        row_group.next_to(question, DOWN, buff=2.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["row"]) as tracker:
            self.play(FadeIn(row_group, shift=UP * 0.2), run_time=1.0)
            self.wait(tracker.get_remaining_duration())

        choices, correct_letter = choice_values_for(spec, row)
        lines = narration_lines(spec, correct_letter)
        choice_group = build_choice_row(choices)
        choice_group.next_to(row_group, DOWN, buff=2.8)

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

        blank_cell = row_group[spec.blank_pos]
        resolved = _build_marker(row["correct"], 1.0).move_to(blank_cell.get_center())
        with self.voiceover(text=lines["explain"]) as tracker:
            self.play(FadeOut(blank_cell[1], scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.8)
            blank_cell[1].set_opacity(0)
            blank_cell.set_opacity(0)
            self.play(FadeOut(choice_group), FadeOut(box), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        answer_text = Text(f"Answer: {correct_letter}", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(row_group, DOWN, buff=2.8)
        with self.voiceover(text=lines["final"]) as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, row_group, resolved, answer_text)),
            run_time=0.8,
        )


def metadata_for(spec: PatternSpec) -> dict:
    row = row_values_for(spec)
    choices, correct_letter = choice_values_for(spec, row)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "serial_reasoning",
        "skill": "two_simultaneous_attributes",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "blank_position": spec.blank_pos,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"sr_two_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "explanation_script": [
            lines["intro"], lines["row"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
