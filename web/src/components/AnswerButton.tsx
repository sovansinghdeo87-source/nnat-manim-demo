export type AnswerStatus = "idle" | "correct" | "wrong" | "muted";

const STATUS_CLASSES: Record<AnswerStatus, string> = {
  idle: "border-ink/10 bg-white text-ink hover:border-accent hover:bg-accent-soft",
  correct: "border-correct bg-correct-soft text-correct pc-pop",
  wrong: "border-wrong bg-wrong-soft text-wrong pc-shake",
  muted: "border-ink/5 bg-white text-ink/30",
};

export function AnswerButton({
  letter,
  status,
  disabled,
  onClick,
}: {
  letter: string;
  status: AnswerStatus;
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`flex h-16 flex-1 items-center justify-center rounded-2xl border-2 text-2xl font-extrabold shadow-sm transition active:scale-90 disabled:cursor-not-allowed sm:h-20 sm:text-3xl ${STATUS_CLASSES[status]}`}
    >
      {letter}
      {status === "correct" && <span className="ml-2">✓</span>}
      {status === "wrong" && <span className="ml-2">✕</span>}
    </button>
  );
}
