"""Question image scene -- renders ANY question in this subskill's
questions/ folder by QUESTION_ID. Defaults to the first entry of the
first question file if QUESTION_ID is unset.
    QUESTION_ID=<question_id> manim -s -qh question_image_scene.py QuestionImage
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "_shared"))

from manim import config  # noqa: E402

if os.environ.get("ASPECT_RATIO") == "9:16":
    config.pixel_width = 1080
    config.pixel_height = 1920
    config.frame_height = 14.222222222222221
    config.frame_width = 8.0
from pattern_lib import PatternSpec, render_question_image
from manim import DOWN, LEFT, RIGHT, UP, Scene

ROOT = Path(__file__).resolve().parent
QUESTIONS_DIR = ROOT / "questions"
ID_TAIL = re.compile(r"_(?P<grade>[^_]+)_q(?P<num>\d{2})(?:_v[1-5])?$")


def _spec_for(entry: dict) -> PatternSpec:
    return PatternSpec(
        grade_rank=entry["grade_rank"],
        question_number=entry["question_number"],
        attribute=entry["subskill_attribute"],
        variation_index=entry["variation_index"],
        palette_offset=entry["palette_offset"],
    )


def _load_entry() -> dict:
    qid = os.environ.get("QUESTION_ID")
    if qid:
        m = ID_TAIL.search(qid)
        if m:
            target = QUESTIONS_DIR / f"{m.group('grade')}_q{m.group('num')}.json"
            if target.exists():
                for entry in json.loads(target.read_text()):
                    if entry["question_id"] == qid:
                        return entry
    first_file = sorted(QUESTIONS_DIR.glob("*.json"))[0]
    return json.loads(first_file.read_text())[0]


def _write_choice_regions(entry: dict, regions: dict) -> None:
    """Dumps each answer choice's bounding box as a fraction (0-1) of the
    rendered frame, next to the question image, so the web UI can overlay
    tappable hit-areas directly on top of the drawn shapes."""
    half_w = config.frame_width / 2
    half_h = config.frame_height / 2

    def to_fraction(point):
        x, y = point[0], point[1]
        return (
            (x + half_w) / config.frame_width,
            (half_h - y) / config.frame_height,
        )

    out = {}
    for letter, mobj in regions.items():
        ul = mobj.get_corner(UP + LEFT)
        dr = mobj.get_corner(DOWN + RIGHT)
        x0, y0 = to_fraction(ul)
        x1, y1 = to_fraction(dr)
        out[letter] = {
            "x": round(min(x0, x1), 4),
            "y": round(min(y0, y1), 4),
            "w": round(abs(x1 - x0), 4),
            "h": round(abs(y1 - y0), 4),
        }

    images_dir = ROOT / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    out_path = images_dir / f"{entry['question_id']}.regions.json"
    out_path.write_text(json.dumps(out))


class QuestionImage(Scene):
    def construct(self):
        entry = _load_entry()
        render_question_image(self, _spec_for(entry))
        regions = getattr(self, "choice_regions", None)
        if regions:
            _write_choice_regions(entry, regions)
