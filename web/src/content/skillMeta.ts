import type { FamilyMeta, SkillMeta } from "./types";

export const FAMILIES: FamilyMeta[] = [
  {
    slug: "pattern_completion",
    name: "Pattern Completion",
    blurb: "Finish the picture pattern",
    emoji: "🧩",
  },
  {
    slug: "reasoning_by_analogy",
    name: "Picture Analogies",
    blurb: "A is to B as C is to...?",
    emoji: "🔗",
  },
  {
    slug: "serial_reasoning",
    name: "Serial Reasoning",
    blurb: "Find what completes the sequence",
    emoji: "🔢",
  },
  {
    slug: "spatial_visualization",
    name: "Spatial Visualization",
    blurb: "Picture shapes moving in space",
    emoji: "📐",
  },
];

export const FAMILY_BY_SLUG: Record<string, FamilyMeta> = Object.fromEntries(
  FAMILIES.map((f) => [f.slug, f])
);

export const SKILLS: SkillMeta[] = [
  // pattern_completion
  {
    slug: "alternating_patterns",
    family: "pattern_completion",
    name: "Alternating Patterns",
    blurb: "Spot what swaps back and forth",
    emoji: "🔀",
  },
  {
    slug: "color_shading_continuation",
    family: "pattern_completion",
    name: "Color & Shading",
    blurb: "Follow how colors change step by step",
    emoji: "🎨",
  },
  {
    slug: "line_shape_continuation",
    family: "pattern_completion",
    name: "Lines & Shapes",
    blurb: "See how a shape keeps growing",
    emoji: "➰",
  },
  {
    slug: "multi_rule_patterns",
    family: "pattern_completion",
    name: "Multi-Rule Patterns",
    blurb: "Track two rules happening at once",
    emoji: "🧩",
  },
  {
    slug: "overlapping_shapes",
    family: "pattern_completion",
    name: "Overlapping Shapes",
    blurb: "Figure out what's hidden underneath",
    emoji: "🟣",
  },
  {
    slug: "position_orientation",
    family: "pattern_completion",
    name: "Position & Direction",
    blurb: "Watch where things move",
    emoji: "🧭",
  },
  {
    slug: "reflection",
    family: "pattern_completion",
    name: "Reflection",
    blurb: "Find the mirror image",
    emoji: "🪞",
  },
  {
    slug: "repeating_patterns",
    family: "pattern_completion",
    name: "Repeating Patterns",
    blurb: "Catch the beat that repeats",
    emoji: "🔁",
  },
  {
    slug: "rotation",
    family: "pattern_completion",
    name: "Rotation",
    blurb: "Watch the shape turn",
    emoji: "🔄",
  },
  {
    slug: "symmetry",
    family: "pattern_completion",
    name: "Symmetry",
    blurb: "Match the two sides",
    emoji: "✨",
  },

  // reasoning_by_analogy
  {
    slug: "addition_removal",
    family: "reasoning_by_analogy",
    name: "Addition & Removal",
    blurb: "Something gets added or taken away",
    emoji: "➕",
  },
  {
    slug: "color_shading_change",
    family: "reasoning_by_analogy",
    name: "Color & Shading Change",
    blurb: "Colors change following a rule",
    emoji: "🎨",
  },
  {
    slug: "combined_transformations",
    family: "reasoning_by_analogy",
    name: "Combined Changes",
    blurb: "A few changes happen all at once",
    emoji: "🔀",
  },
  {
    slug: "count_change",
    family: "reasoning_by_analogy",
    name: "Count Change",
    blurb: "The number of things changes",
    emoji: "🔢",
  },
  {
    slug: "inside_outside",
    family: "reasoning_by_analogy",
    name: "Inside & Outside",
    blurb: "Things move inside or outside",
    emoji: "📦",
  },
  {
    slug: "movement_position",
    family: "reasoning_by_analogy",
    name: "Movement & Position",
    blurb: "Watch where things move to",
    emoji: "🧭",
  },
  {
    slug: "reflection",
    family: "reasoning_by_analogy",
    name: "Reflection",
    blurb: "Find the mirror match",
    emoji: "🪞",
  },
  {
    slug: "rotation",
    family: "reasoning_by_analogy",
    name: "Rotation",
    blurb: "Watch the shape turn",
    emoji: "🔄",
  },
  {
    slug: "shape_change",
    family: "reasoning_by_analogy",
    name: "Shape Change",
    blurb: "One shape turns into another",
    emoji: "🔺",
  },
  {
    slug: "size_change",
    family: "reasoning_by_analogy",
    name: "Size Change",
    blurb: "Things grow or shrink",
    emoji: "🔍",
  },

  // serial_reasoning
  {
    slug: "addition_subtraction",
    family: "serial_reasoning",
    name: "Addition & Subtraction",
    blurb: "Shapes are added or taken away in a row",
    emoji: "➕",
  },
  {
    slug: "alternation",
    family: "serial_reasoning",
    name: "Alternation",
    blurb: "Catch what swaps back and forth",
    emoji: "🔀",
  },
  {
    slug: "color_shading_progression",
    family: "serial_reasoning",
    name: "Color & Shading Progression",
    blurb: "Colors shift step by step",
    emoji: "🎨",
  },
  {
    slug: "column_sequences",
    family: "serial_reasoning",
    name: "Column Sequences",
    blurb: "Find the pattern going down",
    emoji: "⬇️",
  },
  {
    slug: "count_progression",
    family: "serial_reasoning",
    name: "Count Progression",
    blurb: "Count up or down the row",
    emoji: "🔢",
  },
  {
    slug: "distribution_rules",
    family: "serial_reasoning",
    name: "Distribution Rules",
    blurb: "Figure out how pieces are shared out",
    emoji: "🧩",
  },
  {
    slug: "multi_rule_matrices",
    family: "serial_reasoning",
    name: "Multi-Rule Matrices",
    blurb: "Two rules at once in a grid",
    emoji: "🧮",
  },
  {
    slug: "overlay_intersection_rules",
    family: "serial_reasoning",
    name: "Overlay & Intersection",
    blurb: "See how shapes overlap",
    emoji: "🟣",
  },
  {
    slug: "position_sequence",
    family: "serial_reasoning",
    name: "Position Sequence",
    blurb: "Watch where it moves in the row",
    emoji: "🧭",
  },
  {
    slug: "rotation_sequence",
    family: "serial_reasoning",
    name: "Rotation Sequence",
    blurb: "Watch it turn along the row",
    emoji: "🔄",
  },
  {
    slug: "row_sequences",
    family: "serial_reasoning",
    name: "Row Sequences",
    blurb: "Find the pattern across the row",
    emoji: "➡️",
  },
  {
    slug: "shape_progression",
    family: "serial_reasoning",
    name: "Shape Progression",
    blurb: "Shapes change step by step",
    emoji: "🔺",
  },
  {
    slug: "three_by_three_matrices",
    family: "serial_reasoning",
    name: "3×3 Matrices",
    blurb: "Solve a 3-by-3 grid puzzle",
    emoji: "🔳",
  },
  {
    slug: "two_by_two_matrices",
    family: "serial_reasoning",
    name: "2×2 Matrices",
    blurb: "Solve a 2-by-2 grid puzzle",
    emoji: "🔲",
  },
  {
    slug: "two_simultaneous_attributes",
    family: "serial_reasoning",
    name: "Two Attributes at Once",
    blurb: "Track two things changing together",
    emoji: "🧠",
  },

  // spatial_visualization
  {
    slug: "folding_and_unfolding",
    family: "spatial_visualization",
    name: "Folding & Unfolding",
    blurb: "Picture the paper folded and unfolded",
    emoji: "📄",
  },
  {
    slug: "hidden_overlapping_shapes",
    family: "spatial_visualization",
    name: "Hidden Shapes",
    blurb: "Find the shape hiding underneath",
    emoji: "🕵️",
  },
  {
    slug: "mental_transformation",
    family: "spatial_visualization",
    name: "Mental Transformation",
    blurb: "Picture it after a couple of moves",
    emoji: "🧠",
  },
  {
    slug: "multiple_spatial_operations",
    family: "spatial_visualization",
    name: "Multiple Operations",
    blurb: "Add a piece, then take one away",
    emoji: "🧩",
  },
  {
    slug: "overlay",
    family: "spatial_visualization",
    name: "Overlay",
    blurb: "Find what's hidden at the bottom",
    emoji: "🪆",
  },
  {
    slug: "piece_assembly",
    family: "spatial_visualization",
    name: "Piece Assembly",
    blurb: "Match the pieces that fit together",
    emoji: "🧩",
  },
  {
    slug: "reflection",
    family: "spatial_visualization",
    name: "Reflection",
    blurb: "Find the mirror image",
    emoji: "🪞",
  },
  {
    slug: "rotation",
    family: "spatial_visualization",
    name: "Rotation",
    blurb: "Picture the shape turned around",
    emoji: "🔄",
  },
  {
    slug: "shape_combination",
    family: "spatial_visualization",
    name: "Shape Combination",
    blurb: "See what pieces make together",
    emoji: "🔗",
  },
  {
    slug: "shape_subtraction",
    family: "spatial_visualization",
    name: "Shape Subtraction",
    blurb: "See what's left after taking a piece away",
    emoji: "➖",
  },
];

export const SKILL_BY_KEY: Record<string, SkillMeta> = Object.fromEntries(
  SKILLS.map((s) => [`${s.family}/${s.slug}`, s])
);

export function skillsFor(family: string): SkillMeta[] {
  return SKILLS.filter((s) => s.family === family);
}

export const GRADES = [
  { label: "K", name: "Kindergarten" },
  { label: "1", name: "Grade 1" },
  { label: "2", name: "Grade 2" },
  { label: "3", name: "Grade 3" },
  { label: "4", name: "Grade 4" },
];
