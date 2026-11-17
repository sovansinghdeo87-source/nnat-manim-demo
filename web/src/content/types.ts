export type ChoiceRegion = { x: number; y: number; w: number; h: number };

export type Question = {
  questionId: string;
  family: string;
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
  choiceRegions?: Partial<Record<string, ChoiceRegion>>;
};

export type SkillMeta = {
  slug: string;
  family: string;
  name: string;
  blurb: string;
  emoji: string;
};

export type FamilyMeta = {
  slug: string;
  name: string;
  blurb: string;
  emoji: string;
};
