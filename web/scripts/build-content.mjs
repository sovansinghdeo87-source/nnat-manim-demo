#!/usr/bin/env node
// Flattens question_bank/<family>/*/questions/*.json (across all 4 skill
// families) into one manifest and copies the matching rendered PNGs/videos
// into public/. Regenerable build output -- see web/.gitignore.
// Run with `npm run build:content`.

import { readdirSync, readFileSync, writeFileSync, mkdirSync, copyFileSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = join(__dirname, "..");
const BANK_ROOT = join(WEB_ROOT, "..", "question_bank");
const VIDEOS_SRC_ROOT = join(WEB_ROOT, "..", "samples");
const MANIFEST_OUT = join(WEB_ROOT, "src", "content", "content.json");
const IMAGES_OUT_ROOT = join(WEB_ROOT, "public", "images");
const VIDEOS_OUT_ROOT = join(WEB_ROOT, "public", "videos");

const FAMILIES = [
  "pattern_completion",
  "reasoning_by_analogy",
  "serial_reasoning",
  "spatial_visualization",
];

function listSkillDirs(familyRoot) {
  return readdirSync(familyRoot, { withFileTypes: true })
    .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
    .map((d) => d.name)
    .sort();
}

function listQuestionFiles(skillDir) {
  const dir = join(skillDir, "questions");
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json"))
    .map((f) => join(dir, f))
    .sort();
}

function normalizeEntry(raw, family, skill, hasVideo, choiceRegions) {
  return {
    questionId: raw.question_id,
    family,
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
    choiceRegions,
  };
}

function main() {
  const manifest = [];
  let skillCount = 0;
  let imagesCopied = 0;
  let imagesMissing = 0;
  let videosCopied = 0;
  let regionsFound = 0;

  for (const family of FAMILIES) {
    const familyRoot = join(BANK_ROOT, family);
    const skills = listSkillDirs(familyRoot);
    skillCount += skills.length;

    for (const skill of skills) {
      const skillDir = join(familyRoot, skill);
      const imagesOutDir = join(IMAGES_OUT_ROOT, family, skill);
      const videosOutDir = join(VIDEOS_OUT_ROOT, family, skill);
      mkdirSync(imagesOutDir, { recursive: true });
      mkdirSync(videosOutDir, { recursive: true });

      for (const file of listQuestionFiles(skillDir)) {
        const entries = JSON.parse(readFileSync(file, "utf-8"));
        for (const raw of entries) {
          const srcImage = join(skillDir, "images", `${raw.question_id}.png`);
          const destImage = join(imagesOutDir, `${raw.question_id}.png`);
          try {
            statSync(srcImage);
            copyFileSync(srcImage, destImage);
            imagesCopied += 1;
          } catch {
            imagesMissing += 1;
            console.warn(`  missing image for ${raw.question_id} (${family}/${skill})`);
          }

          const srcVideo = join(VIDEOS_SRC_ROOT, `${family}_${skill}__${raw.question_id}.mp4`);
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

          const srcRegions = join(skillDir, "images", `${raw.question_id}.regions.json`);
          let choiceRegions;
          try {
            choiceRegions = JSON.parse(readFileSync(srcRegions, "utf-8"));
            regionsFound += 1;
          } catch {
            // No tap-region metadata for this question -- the A-E buttons below still work.
          }

          manifest.push(normalizeEntry(raw, family, skill, hasVideo, choiceRegions));
        }
      }
    }
  }

  mkdirSync(dirname(MANIFEST_OUT), { recursive: true });
  writeFileSync(MANIFEST_OUT, JSON.stringify(manifest), "utf-8");

  console.log(`Wrote ${manifest.length} question entries across ${skillCount} skills (${FAMILIES.length} families) to ${MANIFEST_OUT}`);
  console.log(`Copied ${imagesCopied} images${imagesMissing ? `, ${imagesMissing} missing` : ""} to ${IMAGES_OUT_ROOT}`);
  console.log(`Copied ${videosCopied} explanation videos to ${VIDEOS_OUT_ROOT}`);
  console.log(`Found tap-region metadata for ${regionsFound} questions`);
}

main();
