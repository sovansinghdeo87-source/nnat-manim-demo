import questions from "./pattern_completion.json";
import type { Question } from "./types";

const ALL_QUESTIONS = questions as Question[];

export function getQuestionsFor(gradeLabel: string, skill: string): Question[] {
  return ALL_QUESTIONS.filter(
    (q) => q.gradeLabel === gradeLabel && q.skill === skill
  );
}

export function countFor(gradeLabel: string, skill: string): number {
  return getQuestionsFor(gradeLabel, skill).length;
}

export function imagePath(q: Question): string {
  return `/images/pattern_completion/${q.skill}/${q.questionId}.png`;
}

export function videoPath(q: Question): string {
  return `/videos/pattern_completion/${q.skill}/${q.questionId}.mp4`;
}
