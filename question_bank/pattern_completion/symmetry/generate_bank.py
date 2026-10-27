"""
Generates questions/<base_question_id>.json for this subskill: 5 grades
(K-4) x 5 base questions = 25 files, each holding that one question's 6
variants (1 base + 5 palette variations) as a list. Does not invoke
Manim and does not write per-question folders -- use
question_image_scene.py / explanation_video_scene.py with
QUESTION_ID=<id> to render any specific entry (same code every time,
only the parameters change).

Usage:
    python generate_bank.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "_shared"))
from pattern_lib import PatternSpec, ATTRIBUTES, GRADE_LABELS, metadata_for  # noqa: E402

ROOT = Path(__file__).resolve().parent


def main() -> None:
    out_dir = ROOT / "questions"
    out_dir.mkdir(exist_ok=True)

    file_count = 0
    entry_count = 0
    for grade_rank, grade_label in enumerate(GRADE_LABELS):
        for q_num, attribute in enumerate(ATTRIBUTES, start=1):
            variants = []
            for variation_index in range(6):
                spec = PatternSpec(
                    grade_rank=grade_rank, question_number=q_num, attribute=attribute,
                    variation_index=variation_index, palette_offset=variation_index,
                )
                entry = metadata_for(spec)
                entry["question_number"] = q_num
                entry["palette_offset"] = variation_index
                variants.append(entry)

            out = out_dir / f"{grade_label}_q{q_num:02d}.json"
            out.write_text(json.dumps(variants, indent=2) + "\n")
            file_count += 1
            entry_count += len(variants)

    print(f"Generated {file_count} question files ({entry_count} total entries) -> {out_dir}")


if __name__ == "__main__":
    main()
