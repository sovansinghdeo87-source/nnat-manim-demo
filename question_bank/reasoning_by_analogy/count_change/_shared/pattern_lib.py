"""
Shared content engine for Reasoning by Analogy -> Count Change.

Deliberately distinct from Addition/Removal of Elements (additive
delta, +-N): this subskill is MULTIPLICATIVE -- "double this count",
"triple it", "cut it in half" -- the classic analogy confusion being
additive vs. multiplicative reasoning. Two-pair analogy format: first
pair (A -> B) demonstrates the ratio; apply the same ratio to a second
pair's starting cluster (C -> ?). A and C start at different counts
(from the same valid pool) so the question can't be answered by
copying B.
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
MARK_TYPES = ["dot", "square", "triangle", "star"]

# attribute -> (ratio, valid starting-count pool so results stay whole numbers)
RATIO_POOLS: dict[str, tuple[float, list[int]]] = {
    "double": (2, [1, 2, 3, 4, 5]),
    "triple": (3, [1, 2, 3]),
    "quadruple": (4, [1, 2]),
    "half": (0.5, [2, 4, 6, 8]),
    "third": (1 / 3, [3, 6, 9]),
}
ATTRIBUTES = list(RATIO_POOLS.keys())
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
    def ratio(self) -> float:
        return RATIO_POOLS[self.attribute][0]

    @property
    def pool(self) -> list[int]:
        return RATIO_POOLS[self.attribute][1]

    @property
    def mark_type(self) -> str:
        return MARK_TYPES[self.palette_offset % len(MARK_TYPES)]

    @property
    def count_a(self) -> int:
        pool = self.pool
        return pool[self.palette_offset % len(pool)]

    @property
    def count_c(self) -> int:
        pool = self.pool
        # offset=1 always differs from count_a's index for any pool with >=2
        # entries; a previous version used len//2+1, which reduces to 0 mod 2
        # for the 2-entry "quadruple" pool -- always picking the SAME index.
        return pool[(self.palette_offset + 1) % len(pool)]

    @property
    def difficulty(self) -> int:
        return DIFFICULTY_BY_GRADE[self.grade_rank]

    @property
    def question_id(self) -> str:
        base = f"an_cnt_{self.grade_label}_q{self.question_number:02d}"
        if self.variation_index:
            return f"{base}_v{self.variation_index}"
        return base


def counts_for(spec: PatternSpec) -> dict:
    r = spec.ratio
    return {
        "a": spec.count_a, "b": round(spec.count_a * r),
        "c": spec.count_c, "correct": round(spec.count_c * r),
    }


def distractor_counts_for(spec: PatternSpec, counts: dict) -> list[int]:
    correct = counts["correct"]
    same_as_c = counts["c"]
    same_as_b = counts["b"]
    inverse_ratio = max(1, round(counts["c"] / spec.ratio)) if spec.ratio != 0 else counts["c"]
    additive_instead = max(1, counts["c"] + (counts["b"] - counts["a"]))  # additive, not multiplicative

    candidates = [same_as_c, same_as_b, inverse_ratio, additive_instead]
    used = {correct}
    distractors: list[int] = []
    for cand in candidates:
        if cand not in used and cand not in distractors and cand >= 1:
            distractors.append(cand)

    salt = 1
    while len(distractors) < 4:
        cand = correct + salt if salt % 2 else max(1, correct - salt)
        salt += 1
        if cand not in used and cand not in distractors and cand >= 1:
            distractors.append(cand)
    return distractors[:4]


def choice_counts_for(spec: PatternSpec, counts: dict) -> tuple[list[int], str]:
    distractors = distractor_counts_for(spec, counts)
    choices = distractors + [counts["correct"]]
    rng = random.Random(spec.question_id)
    rng.shuffle(choices)
    correct_letter = "ABCDE"[choices.index(counts["correct"])]
    return choices, correct_letter


def _mark(mark_type: str, scale: float = 1.0):
    s = 0.13 * scale
    if mark_type == "dot":
        return Circle(radius=s, color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
    if mark_type == "square":
        return Square(side_length=s * 1.8, color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
    if mark_type == "triangle":
        return Triangle(color=INK, stroke_width=0, fill_color=INK, fill_opacity=1).scale(s * 1.6)
    if mark_type == "star":
        return Star(n=5, outer_radius=s * 1.3, inner_radius=s * 0.6,
                     color=INK, stroke_width=0, fill_color=INK, fill_opacity=1)
    raise ValueError(mark_type)


def _build_cluster(mark_type: str, count: int, scale: float = 1.0):
    marks = [_mark(mark_type, scale) for _ in range(max(count, 1))]
    cols = min(4, max(1, count))
    return VGroup(*marks).arrange_in_grid(rows=None, cols=cols, buff=0.13 * scale)


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
    return SurroundingRectangle(mobj, color=color, buff=0.25, stroke_width=6, corner_radius=0.1)


def narration_lines(spec: PatternSpec, correct_letter: str) -> dict:
    verb = {"double": "doubles", "triple": "triples", "quadruple": "becomes four times as many",
            "half": "is cut in half", "third": "is cut into a third"}[spec.attribute]
    return {
        "intro": QUESTION_TEXT,
        "first_pair": f"In the first pair, the count {verb}.",
        "second_pair": "Now the second pair.",
        "choices": "Here are the five answer choices.",
        "reveal": f"The correct answer is {correct_letter}.",
        "explain": f"The same rule applies: this count {verb} too.",
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

    counts = counts_for(spec)
    pair1 = build_pair(_build_cluster(spec.mark_type, counts["a"]), _build_cluster(spec.mark_type, counts["b"]))
    pair2 = build_pair(_build_cluster(spec.mark_type, counts["c"]), _qmark())
    pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.5)
    pairs.next_to(question, DOWN, buff=0.5)

    choice_counts, _ = choice_counts_for(spec, counts)
    choices = build_choice_row([_build_cluster(spec.mark_type, c, 0.85) for c in choice_counts])
    _choice_fit = min(1.0, (config.frame_width - 1.0) / max(pairs.width, choices.width))
    if _choice_fit < 1.0:
        pairs.scale(_choice_fit)
        choices.scale(_choice_fit)
    choices.next_to(pairs, DOWN, buff=0.9)

    _group = VGroup(title, question, pairs, choices)
    _spread_group_vertically(_group)
    _group.move_to(ORIGIN)
    scene.add(_group)


class AnalogyCountChangeVideoScene(VoiceoverScene):
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

        counts = counts_for(spec)
        cluster_a = _build_cluster(spec.mark_type, counts["a"])
        cluster_b = _build_cluster(spec.mark_type, counts["b"])
        pair1 = build_pair(cluster_a, cluster_b)
        pair1.next_to(question, DOWN, buff=2.2)

        lines = narration_lines(spec, "")
        with self.voiceover(text=lines["first_pair"]) as tracker:
            self.play(FadeIn(cluster_a, scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(FadeIn(cluster_b, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        cluster_c = _build_cluster(spec.mark_type, counts["c"])
        qmark = _qmark()
        pair2 = build_pair(cluster_c, qmark)
        pair2.next_to(pair1, DOWN, buff=2.0)

        with self.voiceover(text=lines["second_pair"]) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        choice_counts, correct_letter = choice_counts_for(spec, counts)
        lines = narration_lines(spec, correct_letter)
        choices = build_choice_row([_build_cluster(spec.mark_type, c, 0.85) for c in choice_counts])
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

        resolved = _build_cluster(spec.mark_type, counts["correct"]).move_to(qmark.get_center())
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
    counts = counts_for(spec)
    choice_counts, correct_letter = choice_counts_for(spec, counts)
    lines = narration_lines(spec, correct_letter)
    return {
        "question_id": spec.question_id,
        "category": "reasoning_by_analogy",
        "skill": "count_change",
        "subskill_attribute": spec.attribute,
        "difficulty": spec.difficulty,
        "grade_label": spec.grade_label,
        "grade_rank": spec.grade_rank,
        "minimum_grade": spec.grade_rank,
        "maximum_grade": spec.grade_rank,
        "variation_of": (f"an_cnt_{spec.grade_label}_q{spec.question_number:02d}"
                          if spec.variation_index else None),
        "variation_index": spec.variation_index,
        "title": TITLE_TEXT,
        "question_text": QUESTION_TEXT,
        "format": "multiple_choice_5",
        "correct_answer": correct_letter,
        "ratio": spec.ratio,
        "counts": counts,
        "explanation_script": [
            lines["intro"], lines["first_pair"], lines["second_pair"], lines["choices"],
            lines["reveal"], lines["explain"], lines["final"],
        ],
    }
