"use client";

import { useEffect, useState } from "react";

const COLORS = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#ec4899"];

type Piece = {
  id: number;
  left: number;
  color: string;
  delay: number;
  duration: number;
  rotate: number;
  drift: number;
};

export function Confetti({
  trigger,
  count = 24,
}: {
  trigger: number;
  count?: number;
}) {
  const [pieces, setPieces] = useState<Piece[]>([]);

  useEffect(() => {
    if (trigger === 0) return;
    const next = Array.from({ length: count }, (_, i) => ({
      id: trigger * 1000 + i,
      left: Math.random() * 100,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      delay: Math.random() * 0.15,
      duration: 0.9 + Math.random() * 0.6,
      rotate: Math.random() * 360,
      drift: (Math.random() - 0.5) * 60,
    }));
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setPieces(next);
    const timer = setTimeout(() => setPieces([]), 1700);
    return () => clearTimeout(timer);
  }, [trigger, count]);

  if (pieces.length === 0) return null;

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-50 overflow-hidden"
    >
      {pieces.map((p) => (
        <span
          key={p.id}
          className="confetti-piece absolute top-0 block h-2.5 w-2.5 rounded-sm"
          style={
            {
              left: `${p.left}%`,
              backgroundColor: p.color,
              animationDelay: `${p.delay}s`,
              animationDuration: `${p.duration}s`,
              "--drift": `${p.drift}px`,
              transform: `rotate(${p.rotate}deg)`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  );
}
