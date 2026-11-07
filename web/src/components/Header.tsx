import Link from "next/link";

export function Header({
  backHref,
  backLabel,
  title,
}: {
  backHref?: string;
  backLabel?: string;
  title?: string;
}) {
  return (
    <header className="sticky top-0 z-10 flex items-center justify-between bg-background/90 px-5 py-4 backdrop-blur">
      <Link
        href="/"
        className="flex items-center gap-2 text-lg font-extrabold text-ink"
      >
        <span className="text-2xl">🧠</span>
        NNAT Practice
      </Link>
      {backHref && (
        <Link
          href={backHref}
          className="rounded-full border-2 border-ink/10 bg-white px-4 py-2 text-sm font-bold text-ink shadow-sm transition hover:border-accent hover:text-accent"
        >
          ← {backLabel ?? "Back"}
        </Link>
      )}
      {title && (
        <span className="hidden text-sm font-semibold text-ink/60 sm:inline">
          {title}
        </span>
      )}
    </header>
  );
}
