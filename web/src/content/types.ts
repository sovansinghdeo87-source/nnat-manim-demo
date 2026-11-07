export type Question = {
  questionId: string;
  skill: string;
  gradeLabel: string;
  gradeRank: number;
  questionNumber: number;
  variationIndex: number;
  difficulty: number;
  questionText: string;
  correctAnswer: string;
  explanationScript: string[];
  hasVideo: boolean;
};

export type SkillMeta = {
  slug: string;
  name: string;
  blurb: string;
  emoji: string;
};
