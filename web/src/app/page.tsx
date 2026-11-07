import Link from "next/link";
import { Header } from "@/components/Header";
import { GRADES } from "@/content/skillMeta";

const GRADE_COLORS = [
  "bg-rose-200 hover:bg-rose-300",
  "bg-amber-200 hover:bg-amber-300",
  "bg-lime-200 hover:bg-lime-300",
  "bg-sky-200 hover:bg-sky-300",
  "bg-violet-200 hover:bg-violet-300",
];

const FLOATERS = [
  { emoji: "🔺", top: "8%", left: "6%", rot: "-10deg", delay: "0s", size: "text-3xl" },
  { emoji: "⬛", top: "16%", left: "88%", rot: "12deg", delay: "0.6s", size: "text-2xl" },
  { emoji: "⭐", top: "70%", left: "10%", rot: "6deg", delay: "1.1s", size: "text-3xl" },
  { emoji: "🔵", top: "78%", left: "85%", rot: "-6deg", delay: "0.3s", size: "text-2xl" },
  { emoji: "🔶", top: "40%", left: "92%", rot: "14deg", delay: "1.5s", size: "text-2xl" },
  { emoji: "🔷", top: "50%", left: "3%", rot: "-14deg", delay: "0.9s", size: "text-2xl" },
];

export default function Home() {
  return (
    <div className="relative flex min-h-full flex-1 flex-col overflow-hidden">
      <Header />

      <div aria-hidden className="pointer-events-none absolute inset-0">
        {FLOATERS.map((f, i) => (
          <span
            key={i}
            className={`float-slow absolute opacity-20 ${f.size}`}
            style={{
              top: f.top,
              left: f.left,
              animationDelay: f.delay,
              "--rot": f.rot,
            } as React.CSSProperties}
          >
            {f.emoji}
          </span>
        ))}
      </div>

      <main className="relative mx-auto flex w-full max-w-3xl flex-1 flex-col items-center px-6 py-10 text-center">
        <p className="text-5xl">🧩✨🔄</p>
        <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-ink sm:text-5xl">
          Let&apos;s practice patterns!
        </h1>
        <p className="mt-3 max-w-md text-lg text-ink/70">
          Pick your grade to start solving fun picture puzzles.
        </p>

        <div className="mt-10 grid w-full grid-cols-2 gap-4 sm:grid-cols-5">
          {GRADES.map((grade, i) => (
            <Link
              key={grade.label}
              href={`/grade/${grade.label}`}
              className={`flex flex-col items-center justify-center gap-1 rounded-3xl p-6 shadow-sm transition hover:-translate-y-1 hover:scale-105 hover:shadow-md active:scale-95 ${GRADE_COLORS[i % GRADE_COLORS.length]}`}
            >
              <span className="text-4xl font-extrabold text-ink">
                {grade.label}
              </span>
              <span className="text-sm font-semibold text-ink/70">
                {grade.name}
              </span>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
