import type { SkillMeta } from "./types";

export const SKILLS: SkillMeta[] = [
  {
    slug: "alternating_patterns",
    name: "Alternating Patterns",
    blurb: "Spot what swaps back and forth",
    emoji: "🔀",
  },
  {
    slug: "color_shading_continuation",
    name: "Color & Shading",
    blurb: "Follow how colors change step by step",
    emoji: "🎨",
  },
  {
    slug: "line_shape_continuation",
    name: "Lines & Shapes",
    blurb: "See how a shape keeps growing",
    emoji: "➰",
  },
  {
    slug: "multi_rule_patterns",
    name: "Multi-Rule Patterns",
    blurb: "Track two rules happening at once",
    emoji: "🧩",
  },
  {
    slug: "overlapping_shapes",
    name: "Overlapping Shapes",
    blurb: "Figure out what's hidden underneath",
    emoji: "🟣",
  },
  {
    slug: "position_orientation",
    name: "Position & Direction",
    blurb: "Watch where things move",
    emoji: "🧭",
  },
  {
    slug: "reflection",
    name: "Reflection",
    blurb: "Find the mirror image",
    emoji: "🪞",
  },
  {
    slug: "repeating_patterns",
    name: "Repeating Patterns",
    blurb: "Catch the beat that repeats",
    emoji: "🔁",
  },
  {
    slug: "rotation",
    name: "Rotation",
    blurb: "Watch the shape turn",
    emoji: "🔄",
  },
  {
    slug: "symmetry",
    name: "Symmetry",
    blurb: "Match the two sides",
    emoji: "✨",
  },
];

export const SKILL_BY_SLUG: Record<string, SkillMeta> = Object.fromEntries(
  SKILLS.map((s) => [s.slug, s])
);

export const GRADES = [
  { label: "K", name: "Kindergarten" },
  { label: "1", name: "Grade 1" },
  { label: "2", name: "Grade 2" },
  { label: "3", name: "Grade 3" },
  { label: "4", name: "Grade 4" },
];
