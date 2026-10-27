# NNAT Manim Demo

A small proof-of-concept for an NNAT-style learning app: **3 sample question
images** and **3 narrated explanation videos**, generated entirely with
Python + Manim Community Edition + Azure text-to-speech. No mobile app, no
backend, no auth — just the content demo.

```
nnat-manim-demo/
├── questions/
│   ├── question_01.png   Pattern Completion
│   ├── question_02.png   Visual Analogy
│   └── question_03.png   Spatial Rotation
│
├── manim/
│   ├── nnat_questions.py         Video scenes (PatternQuestion, AnalogyQuestion, RotationQuestion)
│   └── nnat_question_images.py   Static image scenes used to generate the PNGs above
│
├── output/
│   ├── pattern_question.mp4
│   ├── analogy_question.mp4
│   └── rotation_question.mp4
│
└── README.md
```

## 1. Install Manim + manim-voiceover (Azure)

Requires Python 3.9+ and [Manim Community Edition](https://docs.manim.community).
Manim also needs FFmpeg and a LaTeX-free Cairo/Pango toolchain (installed
automatically as Python deps on most platforms; on macOS you also need
FFmpeg via Homebrew). `sox` is recommended by manim-voiceover for audio
processing.

```bash
# macOS prerequisites (skip any you already have)
brew install ffmpeg sox

# create an isolated environment (recommended)
cd nnat-manim-demo
python3 -m venv venv
source venv/bin/activate

# install manim + the voiceover plugin with Azure support
pip install manim "manim-voiceover[azure]"
```

### Azure Speech credentials

The videos are narrated with Azure's neural text-to-speech via the
[manim-voiceover](https://voiceover.manim.community) plugin's `AzureService`.
You need an Azure Speech resource (there's a free tier). Get its **key** and
**region** from the Azure portal ("Keys and Endpoint" page), then create a
file at `manim/.env`:

```
AZURE_SUBSCRIPTION_KEY=your_actual_key_here
AZURE_SERVICE_REGION=eastus
```

(use whatever region your resource is actually in). manim-voiceover loads
this `.env` automatically — no other setup needed. **Do not commit this file**
(it contains a secret) — it's already listed below as something to keep out
of version control.

Each narration line is cached under `manim/media/voiceovers/` after the first
render, so re-rendering the same scene without changing the narration text
does not re-call the Azure API.

The narration voice is set via the `AZURE_VOICE` constant at the top of
`nnat_questions.py` (defaults to `en-US-JennyNeural`). Swap it for any voice
name from the
[Azure TTS voice list](https://learn.microsoft.com/azure/ai-services/speech-service/language-support?tabs=tts).

## 2. Render the 3 explanation videos

Run from inside the `manim/` folder:

```bash
cd manim

manim -pqh nnat_questions.py PatternQuestion
manim -pqh nnat_questions.py AnalogyQuestion
manim -pqh nnat_questions.py RotationQuestion
```

`-p` previews the video after rendering, `-q h` renders at high quality
(1080p60). Drop `-p` for CI/headless rendering.

### Render all three with one command

```bash
manim -pqh nnat_questions.py PatternQuestion AnalogyQuestion RotationQuestion
```

### Even higher quality (4K)

```bash
manim -pqk nnat_questions.py PatternQuestion
manim -pqk nnat_questions.py AnalogyQuestion
manim -pqk nnat_questions.py RotationQuestion
```

(`-q k` = 4K/60fps. Use `-q m` for a quick 480p draft while iterating.)

## 3. Where the MP4s land

Manim writes rendered videos under a `media/` folder next to the script,
namespaced by quality:

```
manim/media/videos/nnat_questions/1080p60/PatternQuestion.mp4
manim/media/videos/nnat_questions/1080p60/AnalogyQuestion.mp4
manim/media/videos/nnat_questions/1080p60/RotationQuestion.mp4
```

(For `-qk` it's `2160p60/`, for `-ql` it's `480p15/`, etc.)

## 4. Copy the MP4s into output/

From the `manim/` folder:

```bash
cp media/videos/nnat_questions/1080p60/PatternQuestion.mp4  ../output/pattern_question.mp4
cp media/videos/nnat_questions/1080p60/AnalogyQuestion.mp4  ../output/analogy_question.mp4
cp media/videos/nnat_questions/1080p60/RotationQuestion.mp4 ../output/rotation_question.mp4
```

## 5. Generate the 3 question images (PNG)

The static question images are generated with a second Manim file,
`nnat_question_images.py`, which reuses the exact same shapes/colors/fonts
as the videos so everything looks like one product. Use `-s` to save just
the final frame as a PNG instead of rendering a video.

From the `manim/` folder:

```bash
manim -s -qh nnat_question_images.py PatternQuestionImage
manim -s -qh nnat_question_images.py AnalogyQuestionImage
manim -s -qh nnat_question_images.py RotationQuestionImage
```

The PNGs land under:

```
manim/media/images/nnat_question_images/PatternQuestionImage_ManimCE_v<version>.png
manim/media/images/nnat_question_images/AnalogyQuestionImage_ManimCE_v<version>.png
manim/media/images/nnat_question_images/RotationQuestionImage_ManimCE_v<version>.png
```

Copy and rename them into `questions/` (adjust the version suffix in the
filenames to match what Manim actually produced — run `ls media/images/nnat_question_images/`
to check):

```bash
cp media/images/nnat_question_images/PatternQuestionImage_ManimCE_v*.png  ../questions/question_01.png
cp media/images/nnat_question_images/AnalogyQuestionImage_ManimCE_v*.png  ../questions/question_02.png
cp media/images/nnat_question_images/RotationQuestionImage_ManimCE_v*.png ../questions/question_03.png
```

## Questions in this demo

| # | Image | Video Scene | Skill | Answer |
|---|-------|-------------|-------|--------|
| 1 | `question_01.png` | `PatternQuestion` | Pattern Completion | A |
| 2 | `question_02.png` | `AnalogyQuestion` | Visual Analogy | B |
| 3 | `question_03.png` | `RotationQuestion` | Spatial Rotation | B |

Each video follows the same structure: **question → thinking pause →
answer reveal → visual explanation**, narrated line-by-line with Azure
text-to-speech, using only native Manim shapes (`Circle`, `Triangle`,
`Square`, `Star`, `Arrow`, `CurvedArrow`, `Text`) — no external images,
fonts, or video assets required (only an Azure Speech API call at render
time for the narration audio).

## Scope note

This repo is intentionally minimal: 3 question images + 3 Manim videos
only. No React Native app, no Supabase, no RevenueCat, no auth, no question
bank. Those are out of scope for this proof of concept.
