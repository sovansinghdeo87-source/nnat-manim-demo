"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { ProgressBar } from "./ProgressBar";
import { QuestionCard } from "./QuestionCard";
import { Confetti } from "./Confetti";
import type { Question, SkillMeta } from "@/content/types";
import { imagePath, videoPath } from "@/content/data";

function shuffle<T>(items: T[]): T[] {
  const arr = [...items];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

const PRAISE = [
  "Great job! 🎉",
  "Awesome! 🌟",
  "You nailed it! 🙌",
  "Super smart! 🧠✨",
  "Nice work! 👏",
  "Brilliant! 💫",
];

const ENCOURAGE = [
  "Not quite — the answer is",
  "So close! The answer is",
  "Almost! The answer is",
  "Nice try — the answer is",
];

const FINISH_MESSAGES = [
  { min: 90, emoji: "🏆", message: "Puzzle master!" },
  { min: 70, emoji: "🌟", message: "Awesome work!" },
  { min: 50, emoji: "🎉", message: "Nice job!" },
  { min: 0, emoji: "💪", message: "Keep practicing!" },
];

function pickFrom<T>(items: T[], seed: string): T {
  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return items[hash % items.length];
}

export function QuizClient({
  questions,
  gradeLabel,
  skill,
}: {
  questions: Question[];
  gradeLabel: string;
  skill: SkillMeta;
}) {
  const [mounted, setMounted] = useState(false);
  const [order, setOrder] = useState<Question[]>(questions);
  const [index, setIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [selected, setSelected] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [finished, setFinished] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [confettiTrigger, setConfettiTrigger] = useState(0);

  useEffect(() => {
    setOrder(shuffle(questions));
    setSpeechSupported(
      typeof window !== "undefined" && "speechSynthesis" in window
    );
    setMounted(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const current = order[index];
  const total = order.length;

  const explanationText = useMemo(
    () => current?.explanationScript.join(" ") ?? "",
    [current]
  );

  function handleAnswer(letter: string) {
    if (revealed || !current) return;
    setSelected(letter);
    setRevealed(true);
    if (letter === current.correctAnswer) {
      setScore((s) => s + 1);
      setStreak((s) => s + 1);
      setConfettiTrigger((t) => t + 1);
    } else {
      setStreak(0);
    }
  }

  function handleNext() {
    if (index + 1 >= total) {
      setFinished(true);
    } else {
      setIndex((i) => i + 1);
      setSelected(null);
      setRevealed(false);
    }
  }

  function handleRestart() {
    setOrder(shuffle(questions));
    setIndex(0);
    setScore(0);
    setStreak(0);
    setSelected(null);
    setRevealed(false);
    setFinished(false);
  }

  function speak() {
    if (!speechSupported) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(explanationText);
    utter.rate = 0.95;
    window.speechSynthesis.speak(utter);
  }

  if (!mounted) {
    return (
      <div className="flex flex-1 items-center justify-center text-ink/50">
        Getting your puzzles ready…
      </div>
    );
  }

  if (finished) {
    const pct = total > 0 ? Math.round((score / total) * 100) : 0;
    const stars = pct >= 90 ? 3 : pct >= 60 ? 2 : pct >= 30 ? 1 : 0;
    const { emoji, message } =
      FINISH_MESSAGES.find((f) => pct >= f.min) ?? FINISH_MESSAGES[FINISH_MESSAGES.length - 1];
    return (
      <div className="mx-auto flex w-full max-w-sm flex-1 flex-col items-center justify-center gap-5 px-6 text-center">
        <Confetti trigger={pct >= 50 ? 1 : 0} count={40} />
        <p className="pc-pop text-7xl">{emoji}</p>
        <h2 className="text-2xl font-extrabold text-ink">{message}</h2>
        <p className="text-2xl tracking-wide">
          {"⭐".repeat(stars)}
          <span className="text-ink/15">{"⭐".repeat(3 - stars)}</span>
        </p>
        <p className="text-lg text-ink/70">
          You got <span className="font-extrabold text-correct">{score}</span>{" "}
          out of <span className="font-extrabold">{total}</span> right.
        </p>
        <div className="mt-4 flex w-full flex-col gap-3">
          <button
            type="button"
            onClick={handleRestart}
            className="rounded-full bg-accent px-6 py-3 text-lg font-bold text-white shadow-sm transition hover:-translate-y-0.5 active:scale-95"
          >
            Play again
          </button>
          <Link
            href={`/grade/${gradeLabel}`}
            className="rounded-full border-2 border-ink/10 bg-white px-6 py-3 text-lg font-bold text-ink shadow-sm transition hover:-translate-y-0.5 active:scale-95"
          >
            Back to skills
          </Link>
        </div>
      </div>
    );
  }

  if (!current) {
    return (
      <div className="flex flex-1 items-center justify-center text-ink/50">
        No questions found for this skill yet.
      </div>
    );
  }

  const isCorrect = selected === current.correctAnswer;
  const praise = pickFrom(PRAISE, current.questionId);
  const encourage = pickFrom(ENCOURAGE, current.questionId);

  return (
    <div className="mx-auto flex min-h-0 w-full max-w-xs flex-1 flex-col gap-5 px-6 py-6">
      <Confetti trigger={confettiTrigger} />
      <ProgressBar current={index + 1} total={total} score={score} streak={streak} />

      <h1 className="text-center text-xl font-extrabold text-ink">
        {skill.emoji} {skill.name}
      </h1>

      <div key={current.questionId} className="card-in flex min-h-0 flex-1 flex-col gap-5">
        <QuestionCard
          question={current}
          imageSrc={imagePath(current)}
          videoSrc={videoPath(current)}
          hasVideo={current.hasVideo}
          selected={selected}
          revealed={revealed}
          onAnswer={handleAnswer}
        />

        {revealed && (
        <div className="rounded-2xl border-2 border-ink/5 bg-white p-4 shadow-sm">
          <div className="flex items-center justify-between gap-2">
            <p
              className={`text-sm font-bold ${
                isCorrect ? "text-correct" : "text-ink/70"
              }`}
            >
              {isCorrect
                ? praise
                : `${encourage} ${current.correctAnswer}.`}
            </p>
            {speechSupported && (
              <button
                type="button"
                onClick={speak}
                aria-label="Read explanation aloud"
                className="shrink-0 rounded-full bg-accent-soft px-3 py-1 text-sm font-bold text-accent"
              >
                🔊 Read it to me
              </button>
            )}
          </div>
          <p className="mt-2 text-sm text-ink/70">{explanationText}</p>
          <button
            type="button"
            onClick={handleNext}
            className="mt-4 w-full rounded-full bg-accent px-6 py-3 text-lg font-bold text-white shadow-sm transition hover:-translate-y-0.5 active:scale-95"
          >
            {index + 1 >= total ? "See my score" : "Next question →"}
          </button>
        </div>
        )}
      </div>
    </div>
  );
}
