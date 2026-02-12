/**
 * @fileoverview ScoreRing Component
 *
 * Circular progress ring displaying the CV match score.
 * Uses SVG for smooth animation and color-coded feedback.
 *
 * @module features/cv/components/ScoreRing
 *
 * FEATURES:
 * - Animated circular progress indicator
 * - Color-coded based on score threshold
 * - Configurable size
 * - Score value displayed in center
 *
 * COLOR THRESHOLDS:
 * - 70-100: Green (good match)
 * - 50-69: Yellow (moderate match)
 * - 0-49: Red (poor match)
 *
 * @example
 * ```tsx
 * // Default size (120px)
 * <ScoreRing score={85} />
 *
 * // Custom size
 * <ScoreRing score={45} size={100} />
 * ```
 */

/**
 * ScoreRing component props.
 */
interface ScoreRingProps {
  /** Match score (0-100) */
  score: number;
  /** Ring diameter in pixels (default: 120) */
  size?: number;
}

/**
 * Get color scheme based on score threshold.
 *
 * @param score - The match score (0-100)
 * @returns Color object with stroke, background, and text colors
 */
const getScoreColor = (score: number) => {
  if (score >= 70) return { stroke: '#22c55e', bg: '#dcfce7', text: '#166534' };
  if (score >= 50) return { stroke: '#eab308', bg: '#fef9c3', text: '#854d0e' };
  return { stroke: '#ef4444', bg: '#fee2e2', text: '#991b1b' };
};

/**
 * ScoreRing Component
 *
 * Displays a circular progress ring with the match score.
 *
 * @param props - Component props
 * @returns Score ring SVG element
 */
export const ScoreRing = ({ score, size = 120 }: ScoreRingProps) => {
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  const colors = getScoreColor(score);

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colors.stroke}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold" style={{ color: colors.text }}>
          {score}
        </span>
        <span className="text-xs text-gray-500 uppercase tracking-wide">Score</span>
      </div>
    </div>
  );
};
