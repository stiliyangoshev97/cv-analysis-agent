/**
 * @fileoverview Re-evaluate CV Modal.
 *
 * Modal for selecting a different evaluation profile and re-evaluating a CV.
 *
 * @module features/cv/components/ReEvaluateModal
 */

import { useState } from 'react';
import {
  Modal,
  ModalBody,
  ModalFooter,
  Button,
  Text,
  Spinner,
} from '@/shared/components/ui';
import { useProfiles } from '@/features/profile/hooks';
import { useReEvaluateCV } from '../hooks';

// =============================================================================
// Types
// =============================================================================

interface ReEvaluateModalProps {
  /** CV ID to re-evaluate */
  cvId: string;
  /** Candidate name for display */
  candidateName?: string;
  /** Current evaluation template ID (if known) */
  currentTemplateId?: string;
  /** Whether modal is open */
  isOpen: boolean;
  /** Callback when modal closes */
  onClose: () => void;
  /** Callback when re-evaluation completes successfully */
  onSuccess?: () => void;
}

// =============================================================================
// Component
// =============================================================================

/**
 * Modal for re-evaluating a CV with a different profile.
 *
 * Shows a list of available evaluation profiles and triggers
 * re-evaluation when one is selected.
 */
export const ReEvaluateModal = ({
  cvId,
  candidateName,
  currentTemplateId,
  isOpen,
  onClose,
  onSuccess,
}: ReEvaluateModalProps) => {
  const [selectedProfileId, setSelectedProfileId] = useState<string>('');
  
  const { data: profiles, isLoading: loadingProfiles } = useProfiles();
  const { mutate: reEvaluate, isPending: isReEvaluating } = useReEvaluateCV();

  const handleReEvaluate = () => {
    if (!selectedProfileId) return;

    reEvaluate(
      { cvId, templateId: selectedProfileId },
      {
        onSuccess: () => {
          setSelectedProfileId('');
          onClose();
          onSuccess?.();
        },
      }
    );
  };

  const handleClose = () => {
    if (!isReEvaluating) {
      setSelectedProfileId('');
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Re-evaluate CV"
      size="md"
    >
      <ModalBody>
        <Text color="muted" className="mb-4">
          Select a different evaluation profile to re-evaluate{' '}
          <span className="font-semibold text-gray-900 dark:text-white">
            {candidateName || 'this CV'}
          </span>
          . The previous evaluation will be replaced.
        </Text>

        {loadingProfiles ? (
          <div className="flex justify-center py-8">
            <Spinner size="md" />
          </div>
        ) : profiles?.profiles && profiles.profiles.length > 0 ? (
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {profiles.profiles.map((profile) => {
              const isSelected = selectedProfileId === profile.id;
              const isCurrent = currentTemplateId === profile.id;

              return (
                <button
                  key={profile.id}
                  type="button"
                  disabled={isReEvaluating}
                  onClick={() => setSelectedProfileId(profile.id)}
                  className={`
                    w-full text-left p-4 rounded-lg border-2 transition-all
                    ${isSelected
                      ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }
                    ${isReEvaluating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <Text weight="medium" className="text-gray-900 dark:text-white">
                          {profile.name}
                        </Text>
                        {profile.is_system_template && (
                          <span className="px-2 py-0.5 text-xs rounded-full bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300">
                            System
                          </span>
                        )}
                        {isCurrent && (
                          <span className="px-2 py-0.5 text-xs rounded-full bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                            Current
                          </span>
                        )}
                      </div>
                      {profile.description && (
                        <Text size="sm" color="muted" className="mt-1 line-clamp-2">
                          {profile.description}
                        </Text>
                      )}
                      <Text size="xs" color="muted" className="mt-1">
                        {profile.criteria_count || 0} criteria • Pass: {profile.passing_score}%
                      </Text>
                    </div>
                    <div className="ml-4">
                      {isSelected && (
                        <svg
                          className="w-5 h-5 text-blue-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                            clipRule="evenodd"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-8">
            <svg
              className="w-12 h-12 mx-auto text-gray-400 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <Text color="muted">No evaluation profiles found</Text>
            <Text size="sm" color="muted" className="mt-1">
              Create a profile first in Settings → Profiles
            </Text>
          </div>
        )}

        {/* Re-evaluation warning */}
        {selectedProfileId && (
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
            <div className="flex items-start gap-2">
              <svg
                className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <Text size="sm" className="text-yellow-800 dark:text-yellow-200">
                This will replace the current evaluation. The previous scores and reasoning will be lost.
              </Text>
            </div>
          </div>
        )}
      </ModalBody>

      <ModalFooter>
        <Button
          variant="ghost"
          onClick={handleClose}
          disabled={isReEvaluating}
        >
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleReEvaluate}
          disabled={!selectedProfileId || isReEvaluating}
          isLoading={isReEvaluating}
        >
          {isReEvaluating ? 'Re-evaluating...' : 'Re-evaluate'}
        </Button>
      </ModalFooter>
    </Modal>
  );
};
