import Link from "next/link";
import { notFound } from "next/navigation";
import { Header } from "@/components/Header";
import { GRADES, SKILLS } from "@/content/skillMeta";
import { countFor } from "@/content/data";

export function generateStaticParams() {
  return GRADES.map((g) => ({ grade: g.label }));
}

export default async function GradePage({
  params,
}: {
  params: Promise<{ grade: string }>;
}) {
  const { grade } = await params;
  const gradeMeta = GRADES.find((g) => g.label === grade);
  if (!gradeMeta) notFound();

  return (
    <div className="flex min-h-full flex-1 flex-col">
      <Header backHref="/" backLabel="Grades" />
      <main className="mx-auto w-full max-w-4xl flex-1 px-6 py-8">
        <h1 className="text-3xl font-extrabold text-ink">
          {gradeMeta.name} · Pattern Completion
        </h1>
        <p className="mt-2 text-ink/70">Choose a skill to practice.</p>

        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
          {SKILLS.map((skill) => {
            const count = countFor(grade, skill.slug);
            return (
              <Link
                key={skill.slug}
                href={`/grade/${grade}/${skill.slug}`}
                className="flex items-center gap-4 rounded-3xl border-2 border-ink/5 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-accent hover:shadow-md active:scale-[0.98]"
              >
                <span className="text-4xl">{skill.emoji}</span>
                <span className="flex-1">
                  <span className="block text-lg font-bold text-ink">
                    {skill.name}
                  </span>
                  <span className="block text-sm text-ink/60">
                    {skill.blurb}
                  </span>
                </span>
                <span className="rounded-full bg-accent-soft px-3 py-1 text-sm font-bold text-accent">
                  {count}
                </span>
              </Link>
            );
          })}
        </div>
      </main>
    </div>
  );
}
