import { notFound } from "next/navigation";
import { Header } from "@/components/Header";
import { QuizClient } from "@/components/QuizClient";
import { FAMILY_BY_SLUG, GRADES, SKILL_BY_KEY, SKILLS } from "@/content/skillMeta";
import { getQuestionsFor } from "@/content/data";

export function generateStaticParams() {
  return GRADES.flatMap((grade) =>
    SKILLS.map((skill) => ({
      grade: grade.label,
      family: skill.family,
      skill: skill.slug,
    }))
  );
}

export default async function QuizPage({
  params,
}: {
  params: Promise<{ grade: string; family: string; skill: string }>;
}) {
  const { grade, family, skill } = await params;
  const gradeMeta = GRADES.find((g) => g.label === grade);
  const familyMeta = FAMILY_BY_SLUG[family];
  const skillMeta = SKILL_BY_KEY[`${family}/${skill}`];
  if (!gradeMeta || !familyMeta || !skillMeta) notFound();

  const questions = getQuestionsFor(grade, family, skill);

  return (
    <div className="relative flex min-h-full flex-1 flex-col lg:bg-linear-to-br lg:from-accent-soft/50 lg:via-background lg:to-rose-100/50">
      <Header backHref={`/grade/${grade}/${family}`} backLabel={familyMeta.name} />

      <div className="relative mx-auto flex w-full max-w-5xl flex-1 flex-col lg:flex-row lg:items-center lg:justify-center lg:gap-16 lg:py-10">
        <aside className="hidden lg:flex lg:w-72 lg:flex-col lg:gap-4">
          <p className="text-5xl">{skillMeta.emoji}</p>
          <h2 className="text-3xl font-extrabold text-ink">{skillMeta.name}</h2>
          <p className="text-lg text-ink/60">{skillMeta.blurb}</p>
          <p className="text-sm font-bold text-ink/40">
            {gradeMeta.name} · {questions.length} questions
          </p>
          <p className="mt-4 rounded-2xl bg-white/70 p-4 text-sm font-semibold text-ink/70 shadow-sm">
            💡 Tip: look for the pattern before picking an answer!
          </p>
        </aside>

        <div className="flex flex-1 flex-col lg:flex-none lg:items-center lg:justify-center">
          <div className="flex flex-1 flex-col lg:w-[420px] lg:flex-none lg:rounded-[2.5rem] lg:border-8 lg:border-white lg:bg-white lg:py-3 lg:shadow-2xl lg:ring-1 lg:ring-ink/5">
            <QuizClient questions={questions} gradeLabel={grade} skill={skillMeta} />
          </div>
        </div>
      </div>
    </div>
  );
}
