/**
 * @fileoverview Threshold slider component.
 *
 * A styled range slider for setting notification threshold score.
 *
 * @module features/notification/components/ThresholdSlider
 */

import { cn } from '@/shared/utils';

interface ThresholdSliderProps {
  /** Current threshold value (0-100) */
  value: number;
  /** Callback when value changes */
  onChange: (value: number) => void;
  /** Whether the slider is disabled */
  disabled?: boolean;
}

/**
 * Get color class based on threshold value.
 */
const getThresholdColor = (value: number): string => {
  if (value >= 80) return 'text-green-600';
  if (value >= 60) return 'text-yellow-600';
  return 'text-red-600';
};

/**
 * Threshold slider component.
 *
 * @example
 * ```tsx
 * <ThresholdSlider
 *   value={threshold}
 *   onChange={setThreshold}
 * />
 * ```
 */
export const ThresholdSlider = ({ value, onChange, disabled }: ThresholdSliderProps) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-600">Minimum score to trigger notification</span>
        <span className={cn('text-lg font-bold', getThresholdColor(value))}>
          {value}%
        </span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        step="5"
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className={cn(
          'w-full h-2 rounded-lg appearance-none cursor-pointer',
          'bg-gradient-to-r from-red-300 via-yellow-300 to-green-300',
          disabled && 'cursor-not-allowed opacity-50',
          // Custom thumb styling
          '[&::-webkit-slider-thumb]:appearance-none',
          '[&::-webkit-slider-thumb]:w-5',
          '[&::-webkit-slider-thumb]:h-5',
          '[&::-webkit-slider-thumb]:rounded-full',
          '[&::-webkit-slider-thumb]:bg-white',
          '[&::-webkit-slider-thumb]:shadow-lg',
          '[&::-webkit-slider-thumb]:border-2',
          '[&::-webkit-slider-thumb]:border-indigo-500',
          '[&::-webkit-slider-thumb]:cursor-pointer',
          '[&::-moz-range-thumb]:w-5',
          '[&::-moz-range-thumb]:h-5',
          '[&::-moz-range-thumb]:rounded-full',
          '[&::-moz-range-thumb]:bg-white',
          '[&::-moz-range-thumb]:shadow-lg',
          '[&::-moz-range-thumb]:border-2',
          '[&::-moz-range-thumb]:border-indigo-500',
          '[&::-moz-range-thumb]:cursor-pointer'
        )}
      />
      <div className="flex justify-between text-xs text-gray-400 mt-1">
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>
    </div>
  );
};
