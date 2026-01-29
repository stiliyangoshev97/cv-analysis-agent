interface ScoreRingProps {
  score: number;
  size?: number;
}

export const ScoreRing = ({ score, size = 120 }: ScoreRingProps) => {
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  const getScoreColor = (score: number) => {
    if (score >= 70) return { stroke: '#22c55e', bg: '#dcfce7', text: '#166534' };
    if (score >= 50) return { stroke: '#eab308', bg: '#fef9c3', text: '#854d0e' };
    return { stroke: '#ef4444', bg: '#fee2e2', text: '#991b1b' };
  };

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
