export function ProgressBar({
  current,
  total,
  score,
  streak = 0,
}: {
  current: number;
  total: number;
  score: number;
  streak?: number;
}) {
  const pct = total > 0 ? Math.round((current / total) * 100) : 0;
  return (
    <div className="w-full">
      <div className="flex items-center justify-between text-sm font-bold text-ink/60">
        <span>
          Question {current} of {total}
        </span>
        <span className="flex items-center gap-2">
          {streak >= 2 && (
            <span key={streak} className="streak-pop text-accent">
              🔥 {streak}
            </span>
          )}
          <span>⭐ {score}</span>
        </span>
      </div>
      <div className="mt-1 h-3 w-full overflow-hidden rounded-full bg-ink/5">
        <div
          className="h-full rounded-full bg-accent transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
