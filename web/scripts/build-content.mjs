#!/usr/bin/env node
// Flattens question_bank/pattern_completion/*/questions/*.json into one
// manifest and copies the matching rendered PNGs into public/. Regenerable
// build output -- see web/.gitignore. Run with `npm run build:content`.

import { readdirSync, readFileSync, writeFileSync, mkdirSync, copyFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = join(__dirname, "..");
const BANK_ROOT = join(WEB_ROOT, "..", "question_bank", "pattern_completion");
const VIDEOS_SRC_ROOT = join(WEB_ROOT, "..", "samples");
const MANIFEST_OUT = join(WEB_ROOT, "src", "content", "pattern_completion.json");
const IMAGES_OUT_ROOT = join(WEB_ROOT, "public", "images", "pattern_completion");
const VIDEOS_OUT_ROOT = join(WEB_ROOT, "public", "videos", "pattern_completion");

function listSkillDirs() {
  return readdirSync(BANK_ROOT, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
    .map((d) => d.name)
    .sort();
}

function listQuestionFiles(skill) {
  const dir = join(BANK_ROOT, skill, "questions");
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => join(dir, f))
    .sort();
}

function normalizeEntry(raw, skill, hasVideo) {
  return {
    questionId: raw.question_id,
    skill,
    gradeLabel: raw.grade_label,
    gradeRank: raw.grade_rank,
    questionNumber: raw.question_number,
    variationIndex: raw.variation_index,
    difficulty: raw.difficulty,
    questionText: raw.question_text,
    correctAnswer: raw.correct_answer,
    explanationScript: raw.explanation_script,
    hasVideo,
  };
}

function main() {
  const skills = listSkillDirs();
  const manifest = [];
  let imagesCopied = 0;
  let imagesMissing = 0;
  let videosCopied = 0;

  for (const skill of skills) {
    const imagesOutDir = join(IMAGES_OUT_ROOT, skill);
    const videosOutDir = join(VIDEOS_OUT_ROOT, skill);
    mkdirSync(imagesOutDir, { recursive: true });
    mkdirSync(videosOutDir, { recursive: true });

    for (const file of listQuestionFiles(skill)) {
      const entries = JSON.parse(readFileSync(file, "utf-8"));
      for (const raw of entries) {
        const srcImage = join(BANK_ROOT, skill, "images", `${raw.question_id}.png`);
        const destImage = join(imagesOutDir, `${raw.question_id}.png`);
        try {
          statSync(srcImage);
          copyFileSync(srcImage, destImage);
          imagesCopied += 1;
        } catch {
          imagesMissing += 1;
          console.warn(`  missing image for ${raw.question_id} (${skill})`);
        }

        const srcVideo = join(VIDEOS_SRC_ROOT, `pattern_completion_${skill}__${raw.question_id}.mp4`);
        const destVideo = join(videosOutDir, `${raw.question_id}.mp4`);
        let hasVideo = false;
        try {
          statSync(srcVideo);
          copyFileSync(srcVideo, destVideo);
          videosCopied += 1;
          hasVideo = true;
        } catch {
          // No rendered explanation video for this question yet -- fine, the UI falls back to text.
        }

        manifest.push(normalizeEntry(raw, skill, hasVideo));
      }
    }
  }

  mkdirSync(dirname(MANIFEST_OUT), { recursive: true });
  writeFileSync(MANIFEST_OUT, JSON.stringify(manifest), "utf-8");

  console.log(`Wrote ${manifest.length} question entries across ${skills.length} skills to ${MANIFEST_OUT}`);
  console.log(`Copied ${imagesCopied} images${imagesMissing ? `, ${imagesMissing} missing` : ""} to ${IMAGES_OUT_ROOT}`);
  console.log(`Copied ${videosCopied} explanation videos to ${VIDEOS_OUT_ROOT}`);
}

main();
