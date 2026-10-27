"""
NNAT-style question explanation videos, narrated with Azure text-to-speech
via the manim-voiceover plugin.

Contains three self-contained Manim Community Edition scenes:
    - PatternQuestion   (Question 1: Pattern Completion)
    - AnalogyQuestion   (Question 2: Visual Analogy)
    - RotationQuestion  (Question 3: Spatial Rotation)

Requires the AZURE_SUBSCRIPTION_KEY and AZURE_SERVICE_REGION environment
variables (or a .env file next to this script) — see the project README.

Render a single scene:
    manim -pqh nnat_questions.py PatternQuestion

Render all three in one command:
    manim -pqh nnat_questions.py PatternQuestion AnalogyQuestion RotationQuestion
"""

import os

from manim import *
from manim import config

if os.environ.get("ASPECT_RATIO") == "9:16":
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_height = 14.222222222222221
    config.frame_width = 8.0

from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

# ---------------------------------------------------------------------------
# Shared visual style
# ---------------------------------------------------------------------------

INK = "#1A1A2E"          # near-black text / outline color
ACCENT = "#3B82F6"       # blue accent (arrows, dividers)
CORRECT = "#22C55E"      # green highlight for the correct answer
BG = WHITE

TITLE_SIZE = 40
QUESTION_SIZE = 30
LABEL_SIZE = 26
CHOICE_LETTER_SIZE = 24
EXPLAIN_SIZE = 26
ANSWER_SIZE = 40

# Azure neural voice used for narration. Browse other options at
# https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts
AZURE_VOICE = "en-US-JennyNeural"


def make_title(text):
    return Text(text, font_size=TITLE_SIZE, color=INK, weight=BOLD).to_edge(UP, buff=0.5)


def make_question(text):
    return Text(text, font_size=QUESTION_SIZE, color=INK)


# ---------------------------------------------------------------------------
# Shape helpers (no external assets: every glyph is a native Manim mobject)
# ---------------------------------------------------------------------------

def empty_circle(radius=0.55):
    return Circle(radius=radius, color=INK, stroke_width=8, fill_opacity=0)


def filled_circle(radius=0.55):
    return Circle(
        radius=radius, color=INK, stroke_width=8, fill_color=INK, fill_opacity=1
    )


def up_triangle(scale=0.85, filled=True):
    tri = Triangle(color=INK, stroke_width=7)
    tri.set_fill(INK, opacity=1 if filled else 0)
    return tri.scale(scale)


def filled_square(side=1.0):
    return Square(
        side_length=side, color=INK, stroke_width=7, fill_color=INK, fill_opacity=1
    )


def filled_diamond(side=1.0):
    return Square(
        side_length=side, color=INK, stroke_width=7, fill_color=INK, fill_opacity=1
    ).rotate(PI / 4)


def filled_star(radius=0.6):
    return Star(
        n=5, outer_radius=radius, inner_radius=radius * 0.45,
        color=INK, stroke_width=6, fill_color=INK, fill_opacity=1,
    )


def choice_row(shapes, labels=("A", "B", "C", "D", "E"), spacing=2.3):
    """Builds a row of (letter above, shape below) pairs, centered on ORIGIN."""
    group = VGroup(*shapes).arrange(RIGHT, buff=spacing - 1.0)

    full = VGroup()
    for letter, shape in zip(labels, group):
        letter_text = Text(letter, font_size=CHOICE_LETTER_SIZE, color=INK, weight=BOLD)
        letter_text.next_to(shape, UP, buff=0.35)
        pair = VGroup(letter_text, shape)
        full.add(pair)
    full.move_to(ORIGIN)
    max_w = config.frame_width - 1.0
    if full.width > max_w:
        full.scale(max_w / full.width)
    return full


def surround(mobj, color=CORRECT):
    return SurroundingRectangle(mobj, color=color, buff=0.28, stroke_width=6, corner_radius=0.12)


# ---------------------------------------------------------------------------
# Question 1 — Pattern Completion
# ---------------------------------------------------------------------------

class PatternQuestion(VoiceoverScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title("Pattern Completion")
        question = make_question("Which figure comes next?").next_to(title, DOWN, buff=0.35)

        with self.voiceover(
            text="Let's look at this pattern completion question. Which figure comes next?"
        ) as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        # --- Build the sequence: empty -> filled -> empty -> filled -> ? ---
        s1 = empty_circle()
        s2 = filled_circle()
        s3 = empty_circle()
        s4 = filled_circle()
        qmark = Text("?", font_size=56, color=ACCENT, weight=BOLD)

        seq_shapes = [s1, s2, s3, s4, qmark]
        seq_row = VGroup(*seq_shapes).arrange(RIGHT, buff=1.0)
        seq_row.move_to(ORIGIN).shift(UP * 0.6)
        max_w = config.frame_width - 1.0
        if seq_row.width > max_w:
            seq_row.scale(max_w / seq_row.width)

        arrows = VGroup()
        for a, b in zip(seq_shapes[:-1], seq_shapes[1:]):
            arrows.add(Arrow(a.get_right(), b.get_left(), buff=0.1, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.25))

        with self.voiceover(
            text="Here is the sequence: an empty circle, a filled circle, empty, filled, "
            "and then a question mark."
        ) as tracker:
            self.play(FadeIn(s1, scale=0.7), run_time=0.4)
            self.play(GrowArrow(arrows[0]), FadeIn(s2, scale=0.7), run_time=0.5)
            self.play(GrowArrow(arrows[1]), FadeIn(s3, scale=0.7), run_time=0.5)
            self.play(GrowArrow(arrows[2]), FadeIn(s4, scale=0.7), run_time=0.5)
            self.play(GrowArrow(arrows[3]), FadeIn(qmark, scale=0.7), run_time=0.5)
            self.wait(tracker.get_remaining_duration())

        # --- Thinking pause ---
        with self.voiceover(text="Take a moment to think about what comes next.") as tracker:
            self.wait(tracker.get_remaining_duration() + 0.8)

        # --- Answer choices A-E ---
        choices = choice_row(
            [empty_circle(0.4), filled_circle(0.4), up_triangle(0.55), filled_square(0.7), filled_diamond(0.7)]
        )
        choices.next_to(seq_row, DOWN, buff=1.3)

        with self.voiceover(text="Here are the five answer choices, A through E.") as tracker:
            self.play(FadeIn(choices, shift=UP * 0.3), run_time=0.9)
            self.wait(tracker.get_remaining_duration())

        # --- Reveal / highlight correct answer A ---
        choice_A = choices[0]
        box = surround(choice_A)
        with self.voiceover(text="The correct answer is A.") as tracker:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(choice_A, color=CORRECT, scale_factor=1.15), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        # --- Animate the complete pattern again & explain the alternation rule ---
        resolved = empty_circle().move_to(qmark.get_center())
        explain = Text(
            "empty -> filled -> empty -> filled -> empty",
            font_size=EXPLAIN_SIZE, color=INK,
        ).next_to(seq_row, DOWN, buff=0.9)

        with self.voiceover(
            text="Notice how the shapes alternate: empty, filled, empty, filled, and now empty again."
        ) as tracker:
            self.play(FadeOut(qmark, scale=0.6), FadeIn(resolved, scale=0.6), run_time=0.6)
            qmark.set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.play(Write(explain), run_time=1.2)
            self.wait(tracker.get_remaining_duration())

        # --- Final answer ---
        answer_text = Text("Answer: A", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(explain, DOWN, buff=0.6)
        with self.voiceover(text="So the next figure is an empty circle, and the answer is A.") as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(FadeOut(VGroup(title, question, seq_row, arrows, resolved, explain, answer_text)), run_time=0.8)


# ---------------------------------------------------------------------------
# Question 2 — Visual Analogy
# ---------------------------------------------------------------------------

class AnalogyQuestion(VoiceoverScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title("Visual Analogy")
        question = make_question("Complete the analogy.").next_to(title, DOWN, buff=0.35)

        with self.voiceover(text="In this question, we need to complete a visual analogy.") as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        # --- First pair: empty circle -> filled circle ---
        c_empty = empty_circle()
        c_filled = filled_circle()
        arrow1 = Arrow(LEFT * 1.0, RIGHT * 1.0, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.25)

        pair1 = VGroup(c_empty.copy(), arrow1, c_filled).arrange(RIGHT, buff=0.6)
        pair1.move_to(ORIGIN).shift(UP * 1.3 + LEFT * 0.5)

        with self.voiceover(text="In the first pair, an empty circle becomes a filled circle.") as tracker:
            self.play(FadeIn(pair1[0], scale=0.7), run_time=0.5)
            self.play(GrowArrow(pair1[1]), run_time=0.4)
            self.play(TransformFromCopy(pair1[0], pair1[2]), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        transform_label = Text("Outline -> Filled", font_size=LABEL_SIZE, color=ACCENT)
        transform_label.next_to(pair1, RIGHT, buff=0.7)
        if transform_label.get_right()[0] > config.frame_width / 2 - 0.5:
            transform_label.next_to(pair1, DOWN, buff=0.35)
        with self.voiceover(
            text="That means an outline shape transforms into a solid, filled shape."
        ) as tracker:
            self.play(FadeIn(transform_label, shift=RIGHT * 0.2), run_time=0.6)
            self.wait(tracker.get_remaining_duration())
        self.play(FadeOut(transform_label), run_time=0.4)

        # --- Second pair: triangle -> ? ---
        t_outline = up_triangle(0.85, filled=False)
        qmark = Text("?", font_size=56, color=ACCENT, weight=BOLD)
        arrow2 = Arrow(LEFT * 1.0, RIGHT * 1.0, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.25)

        pair2 = VGroup(t_outline, arrow2, qmark).arrange(RIGHT, buff=0.6)
        pair2.move_to(ORIGIN).shift(DOWN * 0.4 + LEFT * 0.5)

        with self.voiceover(
            text="Now look at the second pair: an outlined triangle, followed by a question mark."
        ) as tracker:
            self.play(FadeIn(pair2, shift=UP * 0.2), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        # --- Answer choices A-E ---
        choices = choice_row(
            [up_triangle(0.55, filled=False), up_triangle(0.55, filled=True),
             filled_square(0.7), filled_diamond(0.7), filled_star(0.4)]
        )
        choices.next_to(pair2, DOWN, buff=1.1)

        with self.voiceover(text="Here are the five answer choices.") as tracker:
            self.play(FadeIn(choices, shift=UP * 0.3), run_time=0.9)
            self.wait(tracker.get_remaining_duration())

        # --- Reveal / highlight correct answer B ---
        choice_B = choices[1]
        box = surround(choice_B)
        with self.voiceover(text="The correct answer is B.") as tracker:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(choice_B, color=CORRECT, scale_factor=1.15), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        # --- Animate triangle -> filled triangle (same transformation applied) ---
        resolved_tri = up_triangle(0.85, filled=True).move_to(qmark.get_center())
        explain = Text(
            "Same transformation: outline -> filled",
            font_size=EXPLAIN_SIZE, color=INK,
        ).next_to(pair2, DOWN, buff=0.9)

        with self.voiceover(
            text="Just like the circle, the triangle changes from an outline to a solid, filled shape."
        ) as tracker:
            self.play(FadeOut(qmark, scale=0.6), TransformFromCopy(pair2[0], resolved_tri), run_time=0.8)
            qmark.set_opacity(0)
            self.play(FadeOut(choices), FadeOut(box), run_time=0.4)
            self.play(Write(explain), run_time=1.1)
            self.wait(tracker.get_remaining_duration())

        # --- Final answer ---
        answer_text = Text("Answer: B", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(explain, DOWN, buff=0.6)
        with self.voiceover(text="So the triangle becomes filled, and the answer is B.") as tracker:
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, pair1, pair2, resolved_tri, explain, answer_text)),
            run_time=0.8,
        )


# ---------------------------------------------------------------------------
# Question 3 — Spatial Rotation
# ---------------------------------------------------------------------------

class RotationQuestion(VoiceoverScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_speech_service(AzureService(voice=AZURE_VOICE))

        title = make_title("Spatial Rotation")
        question = make_question("Which figure is correct after a\n90° clockwise rotation?").next_to(
            title, DOWN, buff=0.35
        )
        question.scale(0.9)

        with self.voiceover(text="This question tests spatial rotation.") as tracker:
            self.play(Write(title), run_time=0.8)
            self.play(FadeIn(question, shift=UP * 0.2), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        # --- Original upward-pointing triangle ---
        triangle = up_triangle(1.1, filled=True)
        triangle.move_to(ORIGIN).shift(UP * 0.5)

        with self.voiceover(text="We start with a triangle pointing straight up.") as tracker:
            self.play(FadeIn(triangle, scale=0.7), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        # curved clockwise rotation arrow around the triangle
        rot_arrow = CurvedArrow(
            triangle.get_top() + UP * 0.3 + LEFT * 0.6,
            triangle.get_right() + RIGHT * 0.3 + UP * 0.6,
            color=ACCENT, stroke_width=5, angle=-TAU / 4,
        )

        with self.voiceover(text="Watch as it rotates ninety degrees clockwise.") as tracker:
            self.play(Create(rot_arrow), run_time=0.7)
            self.play(Rotate(triangle, angle=-PI / 2, about_point=triangle.get_center()), run_time=1.2)
            self.play(FadeOut(rot_arrow), run_time=0.4)
            self.wait(tracker.get_remaining_duration())

        points_right = Text("Now points right", font_size=LABEL_SIZE, color=ACCENT)
        points_right.next_to(triangle, DOWN, buff=0.6)
        with self.voiceover(text="Now it points to the right.") as tracker:
            self.play(FadeIn(points_right, shift=UP * 0.2), run_time=0.6)
            self.wait(tracker.get_remaining_duration())
        self.play(FadeOut(points_right), run_time=0.4)

        # --- Answer choices A-E ---
        choice_shapes = [
            up_triangle(0.5, filled=True),
            up_triangle(0.5, filled=True).rotate(-PI / 2),
            up_triangle(0.5, filled=True).rotate(PI),
            up_triangle(0.5, filled=True).rotate(PI / 2),
            filled_diamond(0.6),
        ]
        choices = choice_row(choice_shapes)
        choices.next_to(triangle, DOWN, buff=1.0)

        with self.voiceover(text="Here are the five answer choices.") as tracker:
            self.play(FadeIn(choices, shift=UP * 0.3), run_time=0.9)
            self.wait(tracker.get_remaining_duration())

        # --- Reveal / highlight correct answer B ---
        choice_B = choices[1]
        box = surround(choice_B)
        with self.voiceover(text="The correct answer is B.") as tracker:
            self.play(Create(box), run_time=0.6)
            self.play(Indicate(choice_B, color=CORRECT, scale_factor=1.15), run_time=0.6)
            self.wait(tracker.get_remaining_duration())

        self.play(FadeOut(choices), FadeOut(box), run_time=0.4)

        # --- Repeat the 90-degree rotation once more, for emphasis ---
        with self.voiceover(text="Let's rotate it once more to confirm.") as tracker:
            self.play(Rotate(triangle, angle=-PI / 2, about_point=triangle.get_center()), run_time=1.2)
            self.wait(0.3)
            # rotate back so the final frame still reads "up -> right"
            self.play(Rotate(triangle, angle=PI / 2, about_point=triangle.get_center()), run_time=0.8)
            self.wait(tracker.get_remaining_duration())

        summary = Text("Up -> Right", font_size=EXPLAIN_SIZE, color=INK, weight=BOLD)
        summary.next_to(triangle, DOWN, buff=0.7)
        answer_text = Text("Answer: B", font_size=ANSWER_SIZE, color=CORRECT, weight=BOLD)
        answer_text.next_to(summary, DOWN, buff=0.5)

        with self.voiceover(text="Up becomes right, so the correct answer is B.") as tracker:
            self.play(Write(summary), run_time=0.9)
            self.play(FadeIn(answer_text, scale=0.8), run_time=0.7)
            self.wait(tracker.get_remaining_duration())

        self.wait(0.4)
        self.play(
            FadeOut(VGroup(title, question, triangle, summary, answer_text)),
            run_time=0.8,
        )
