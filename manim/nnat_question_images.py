"""
Generates the 3 static NNAT-style question images (questions/question_01.png,
question_02.png, question_03.png) using the same shapes and style as the
Manim explanation videos in nnat_questions.py.

These are separate Scene classes (NOT part of the required 3 video scenes)
so that nnat_questions.py can stay exactly PatternQuestion / AnalogyQuestion /
RotationQuestion as specified.

Render a single frame (PNG) per scene with the -s (save last frame) flag:

    manim -s -qh nnat_question_images.py PatternQuestionImage
    manim -s -qh nnat_question_images.py AnalogyQuestionImage
    manim -s -qh nnat_question_images.py RotationQuestionImage

See the project README for the exact commands to move/rename the PNGs into
the questions/ folder.
"""

from manim import *

from nnat_questions import (
    INK, ACCENT, BG,
    TITLE_SIZE, QUESTION_SIZE, CHOICE_LETTER_SIZE,
    make_title, make_question,
    empty_circle, filled_circle, up_triangle,
    filled_square, filled_diamond, filled_star,
    choice_row,
)


class PatternQuestionImage(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = make_title("Pattern Completion")
        question = make_question("Which figure comes next?").next_to(title, DOWN, buff=0.4)

        seq_shapes = [empty_circle(), filled_circle(), empty_circle(), filled_circle(),
                      Text("?", font_size=56, color=ACCENT, weight=BOLD)]
        seq_row = VGroup(*seq_shapes).arrange(RIGHT, buff=1.0)
        max_w = config.frame_width - 1.0
        if seq_row.width > max_w:
            seq_row.scale(max_w / seq_row.width)
        arrows = VGroup()
        for a, b in zip(seq_shapes[:-1], seq_shapes[1:]):
            arrows.add(Arrow(a.get_right(), b.get_left(), buff=0.1, color=ACCENT,
                              stroke_width=4, max_tip_length_to_length_ratio=0.25))
        sequence = VGroup(seq_row, arrows)
        sequence.next_to(question, DOWN, buff=0.9)

        choices = choice_row(
            [empty_circle(0.4), filled_circle(0.4), up_triangle(0.55), filled_square(0.7), filled_diamond(0.7)]
        )
        choices.next_to(sequence, DOWN, buff=1.1)

        self.add(title, question, sequence, choices)


class AnalogyQuestionImage(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = make_title("Visual Analogy").to_edge(UP, buff=0.35)
        question = make_question("Complete the analogy.").next_to(title, DOWN, buff=0.25)

        arrow1 = Arrow(LEFT * 1.0, RIGHT * 1.0, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        pair1 = VGroup(empty_circle(0.45), arrow1.copy(), filled_circle(0.45)).arrange(RIGHT, buff=0.5)

        arrow2 = Arrow(LEFT * 1.0, RIGHT * 1.0, color=ACCENT, stroke_width=4, max_tip_length_to_length_ratio=0.25)
        qmark = Text("?", font_size=48, color=ACCENT, weight=BOLD)
        pair2 = VGroup(up_triangle(0.7, filled=False), arrow2.copy(), qmark).arrange(RIGHT, buff=0.5)

        pairs = VGroup(pair1, pair2).arrange(DOWN, buff=0.3)
        pairs.next_to(question, DOWN, buff=0.45)

        choices = choice_row(
            [up_triangle(0.5, filled=False), up_triangle(0.5, filled=True),
             filled_square(0.65), filled_diamond(0.65), filled_star(0.38)]
        )
        choices.next_to(pairs, DOWN, buff=0.55)

        self.add(title, question, pairs, choices)


class RotationQuestionImage(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = make_title("Spatial Rotation")
        question = make_question("Which figure is correct after a\n90° clockwise rotation?")
        question.scale(0.9)
        question.next_to(title, DOWN, buff=0.4)

        triangle = up_triangle(1.1, filled=True)
        triangle.next_to(question, DOWN, buff=0.7)

        rot_arrow = CurvedArrow(
            triangle.get_top() + UP * 0.3 + LEFT * 0.6,
            triangle.get_right() + RIGHT * 0.3 + UP * 0.6,
            color=ACCENT, stroke_width=5, angle=-TAU / 4,
        )

        choice_shapes = [
            up_triangle(0.5, filled=True),
            up_triangle(0.5, filled=True).rotate(-PI / 2),
            up_triangle(0.5, filled=True).rotate(PI),
            up_triangle(0.5, filled=True).rotate(PI / 2),
            filled_diamond(0.6),
        ]
        choices = choice_row(choice_shapes)
        choices.next_to(triangle, DOWN, buff=1.1)

        self.add(title, question, triangle, rot_arrow, choices)
