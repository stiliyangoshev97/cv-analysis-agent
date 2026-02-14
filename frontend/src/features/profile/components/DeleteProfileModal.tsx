/**
 * @fileoverview Delete Profile Confirmation Modal.
 *
 * Modal for confirming profile deletion.
 *
 * @module features/profile/components/DeleteProfileModal
 */

import {
  Modal,
  ModalBody,
  ModalFooter,
  Button,
  Text,
} from '@/shared/components/ui';
import { useDeleteProfile } from '../hooks';
import type { ProfileSummary } from '@/shared/schemas';

interface DeleteProfileModalProps {
  /** Profile to delete */
  profile: ProfileSummary | null;
  /** Whether modal is open */
  isOpen: boolean;
  /** Called when modal closes */
  onClose: () => void;
  /** Called when deletion succeeds */
  onSuccess?: () => void;
}

/**
 * Delete Profile Modal
 *
 * Confirmation dialog for deleting a profile.
 *
 * @example
 * ```tsx
 * <DeleteProfileModal
 *   profile={selectedProfile}
 *   isOpen={isDeleteOpen}
 *   onClose={() => setIsDeleteOpen(false)}
 *   onSuccess={() => refetch()}
 * />
 * ```
 */
export const DeleteProfileModal = ({
  profile,
  isOpen,
  onClose,
  onSuccess,
}: DeleteProfileModalProps) => {
  const { mutate: deleteProfile, isPending } = useDeleteProfile();

  const handleDelete = () => {
    if (!profile) return;

    deleteProfile(profile.id, {
      onSuccess: () => {
        onClose();
        onSuccess?.();
      },
    });
  };

  if (!profile) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Delete Profile"
      size="sm"
    >
      <ModalBody>
        <Text>
          Are you sure you want to delete{' '}
          <span className="font-semibold">"{profile.name}"</span>?
        </Text>
        <Text color="muted" size="sm" className="mt-2">
          This action cannot be undone. All {profile.criteria_count} criteria
          associated with this profile will also be deleted.
        </Text>
      </ModalBody>

      <ModalFooter>
        <Button
          type="button"
          variant="ghost"
          onClick={onClose}
          disabled={isPending}
        >
          Cancel
        </Button>
        <Button
          variant="danger"
          onClick={handleDelete}
          isLoading={isPending}
          disabled={isPending}
        >
          Delete Profile
        </Button>
      </ModalFooter>
    </Modal>
  );
};
