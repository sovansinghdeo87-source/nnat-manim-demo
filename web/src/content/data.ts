import questions from "./content.json";
import type { Question } from "./types";

const ALL_QUESTIONS = questions as Question[];

export function getQuestionsFor(
  gradeLabel: string,
  family: string,
  skill: string
): Question[] {
  return ALL_QUESTIONS.filter(
    (q) => q.gradeLabel === gradeLabel && q.family === family && q.skill === skill
  );
}

export function countFor(gradeLabel: string, family: string, skill: string): number {
  return getQuestionsFor(gradeLabel, family, skill).length;
}

export function countForFamily(gradeLabel: string, family: string): number {
  return ALL_QUESTIONS.filter(
    (q) => q.gradeLabel === gradeLabel && q.family === family
  ).length;
}

export function imagePath(q: Question): string {
  return `/images/${q.family}/${q.skill}/${q.questionId}.png`;
}

export function videoPath(q: Question): string {
  return `/videos/${q.family}/${q.skill}/${q.questionId}.mp4`;
}
