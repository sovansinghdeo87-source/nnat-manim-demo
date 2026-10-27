"""Explanation video scene -- renders ANY question in this subskill's
questions/ folder by QUESTION_ID. Requires AZURE_SUBSCRIPTION_KEY and
AZURE_SERVICE_REGION (see project README). Same code for every
question; only the parameters (looked up from questions/<id>.json)
change.

    QUESTION_ID=<question_id> manim -pqh explanation_video_scene.py ExplanationVideo
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
from pattern_lib import PatternSpec, AnalogyColorShadingVideoScene  # noqa: E402

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


class ExplanationVideo(AnalogyColorShadingVideoScene):
    SPEC = _spec_for(_load_entry())
