import { notFound } from "next/navigation";
import { Header } from "@/components/Header";
import { QuizClient } from "@/components/QuizClient";
import { GRADES, SKILL_BY_SLUG, SKILLS } from "@/content/skillMeta";
import { getQuestionsFor } from "@/content/data";

export function generateStaticParams() {
  return GRADES.flatMap((grade) =>
    SKILLS.map((skill) => ({ grade: grade.label, skill: skill.slug }))
  );
}

export default async function QuizPage({
  params,
}: {
  params: Promise<{ grade: string; skill: string }>;
}) {
  const { grade, skill } = await params;
  const gradeMeta = GRADES.find((g) => g.label === grade);
  const skillMeta = SKILL_BY_SLUG[skill];
  if (!gradeMeta || !skillMeta) notFound();

  const questions = getQuestionsFor(grade, skill);

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <Header backHref={`/grade/${grade}`} backLabel="Skills" />
      <QuizClient questions={questions} gradeLabel={grade} skill={skillMeta} />
    </div>
  );
}
