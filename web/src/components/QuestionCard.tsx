"use client";

import { useEffect, useRef } from "react";
import type { Question } from "@/content/types";
import { AnswerButton, type AnswerStatus } from "./AnswerButton";

const LETTERS = ["A", "B", "C", "D", "E"];

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
