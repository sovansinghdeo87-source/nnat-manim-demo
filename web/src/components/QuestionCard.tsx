"use client";

import { useEffect, useRef } from "react";
import type { ChoiceRegion, Question } from "@/content/types";
import { AnswerButton, type AnswerStatus } from "./AnswerButton";

const LETTERS = ["A", "B", "C", "D", "E"];

// Hit-areas are padded beyond the drawn shape's exact bounds so small
// fingers have an easier time tapping the right one.
const HIT_PADDING = 0.18;

function paddedRegion(region: ChoiceRegion): ChoiceRegion {
  const padW = region.w * HIT_PADDING;
  const padH = region.h * HIT_PADDING;
  const x = Math.max(0, region.x - padW / 2);
  const y = Math.max(0, region.y - padH / 2);
  return {
    x,
    y,
    w: Math.min(region.w + padW, 1 - x),
    h: Math.min(region.h + padH, 1 - y),
  };
}

const OVERLAY_STATUS_CLASSES: Record<AnswerStatus, string> = {
  idle: "tap-hint border-2 border-transparent hover:border-accent/40 hover:bg-accent-soft/40 active:border-accent active:bg-accent-soft/60 focus-visible:border-accent focus-visible:bg-accent-soft/40 focus-visible:outline-none",
  correct: "border-2 border-correct bg-correct-soft/50 pc-pop",
  wrong: "border-2 border-wrong bg-wrong-soft/50 pc-shake",
  muted: "border-2 border-transparent",
};

export function QuestionCard({
  question,
  imageSrc,
  videoSrc,
  hasVideo,
  selected,
  revealed,
  onAnswer,
}: {
  question: Question;
  imageSrc: string;
  videoSrc: string;
  hasVideo: boolean;
  selected: string | null;
  revealed: boolean;
  onAnswer: (letter: string) => void;
}) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const flipped = revealed && hasVideo;

  useEffect(() => {
    if (!flipped) return;
    const video = videoRef.current;
    if (!video) return;
    video.currentTime = 0;
    const playPromise = video.play();
    if (playPromise) {
      playPromise.catch(() => {
        video.muted = true;
        video.play().catch(() => {});
      });
    }
  }, [flipped, videoSrc]);

  return (
    <div className="flex flex-col items-center gap-5">
      <div className="flip-perspective aspect-[9/16] max-h-[56vh] w-full max-w-xs">
        <div className={`flip-inner ${flipped ? "flip-inner-flipped" : ""}`}>
          <div className="flip-face flex items-center justify-center overflow-hidden rounded-3xl border-2 border-ink/5 bg-white shadow-sm">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageSrc}
              alt={question.questionText}
              className="max-h-full max-w-full object-contain"
            />

            {LETTERS.map((letter) => {
              const region = question.choiceRegions?.[letter];
              if (!region) return null;
              const box = paddedRegion(region);
              let status: AnswerStatus = "idle";
              if (revealed) {
                if (letter === question.correctAnswer) status = "correct";
                else if (letter === selected) status = "wrong";
                else status = "muted";
              }
              return (
                <button
                  key={letter}
                  type="button"
                  aria-label={`Option ${letter}`}
                  disabled={revealed}
                  onClick={() => onAnswer(letter)}
                  className={`absolute rounded-xl transition disabled:cursor-not-allowed enabled:cursor-pointer active:scale-95 ${OVERLAY_STATUS_CLASSES[status]}`}
                  style={{
                    left: `${box.x * 100}%`,
                    top: `${box.y * 100}%`,
                    width: `${box.w * 100}%`,
                    height: `${box.h * 100}%`,
                  }}
                />
              );
            })}
          </div>

          {hasVideo && (
            <div className="flip-face flip-face-back flex items-center justify-center overflow-hidden rounded-3xl border-2 border-ink/5 bg-black shadow-sm">
              <video
                ref={videoRef}
                src={videoSrc}
                className="h-full w-full object-contain"
                playsInline
                controls
                loop
              />
            </div>
          )}
        </div>
      </div>

      <div className="flex w-full max-w-xs shrink-0 gap-2">
        {LETTERS.map((letter) => {
          let status: AnswerStatus = "idle";
          if (revealed) {
            if (letter === question.correctAnswer) status = "correct";
            else if (letter === selected) status = "wrong";
            else status = "muted";
          }
          return (
            <AnswerButton
              key={letter}
              letter={letter}
              status={status}
              disabled={revealed}
              onClick={() => onAnswer(letter)}
            />
          );
        })}
      </div>
    </div>
  );
}
