// API Response Types - matches backend schemas

export type PassFailStatus = 'pass' | 'fail';

export interface EvaluationCriteria {
  name: string;
  passed: boolean;
  details: string;
}

export interface CVEvaluationResponse {
  status: PassFailStatus;
  match_score: number;
  reasoning: string;
  criteria: EvaluationCriteria[];
  candidate_name: string | null;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  evaluation: CVEvaluationResponse | null;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  detail?: string;
}

// Frontend Types
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface CVResult {
  id: string;
  filename: string;
  evaluation: CVEvaluationResponse;
  uploadedAt: Date;
}
