/**
 * @fileoverview Clone Profile Modal Component.
 *
 * Modal for cloning a profile with a new name.
 *
 * @module features/profile/components/CloneProfileModal
 */

import { useState } from 'react';
import {
  Modal,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  Text,
  Textarea,
} from '@/shared/components/ui';
import { useCloneProfile } from '../hooks';
import type { ProfileSummary } from '@/shared/schemas';

interface CloneProfileModalProps {
  /** Profile to clone */
  profile: ProfileSummary | null;
  /** Whether modal is open */
  isOpen: boolean;
  /** Called when modal closes */
  onClose: () => void;
  /** Called when clone succeeds */
  onSuccess?: (newProfileId: string) => void;
}

/**
 * Clone Profile Modal
 *
 * Allows user to create a copy of a profile with a new name.
 *
 * @example
 * ```tsx
 * <CloneProfileModal
 *   profile={selectedProfile}
 *   isOpen={isCloneOpen}
 *   onClose={() => setIsCloneOpen(false)}
 *   onSuccess={(id) => navigate(`/profiles/${id}/edit`)}
 * />
 * ```
 */
export const CloneProfileModal = ({
  profile,
  isOpen,
  onClose,
  onSuccess,
}: CloneProfileModalProps) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const { mutate: cloneProfile, isPending } = useCloneProfile();

  // Reset form when modal opens
  const handleOpen = () => {
    if (profile) {
      setName(`${profile.name} (Copy)`);
      setDescription(profile.description ?? '');
    }
  };

  // Use effect to reset on profile change
  if (isOpen && profile && name === '') {
    handleOpen();
  }

  const handleClose = () => {
    setName('');
    setDescription('');
    onClose();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile || !name.trim()) return;

    cloneProfile(
      {
        id: profile.id,
        data: {
          new_name: name.trim(),
          description: description.trim() || null,
        },
      },
      {
        onSuccess: (newProfile) => {
          handleClose();
          onSuccess?.(newProfile.id);
        },
      }
    );
  };

  if (!profile) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Clone Profile"
      size="md"
    >
      <form onSubmit={handleSubmit}>
        <ModalBody className="space-y-4">
          <Text color="muted" size="sm">
            Create a copy of "{profile.name}" with a new name.
            You can then customize the cloned profile.
          </Text>

          <div>
            <label
              htmlFor="clone-name"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              New Profile Name
            </label>
            <Input
              id="clone-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter profile name"
              required
              autoFocus
            />
          </div>

          <div>
            <label
              htmlFor="clone-description"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
            >
              Description (optional)
            </label>
            <Textarea
              id="clone-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe this profile"
              rows={3}
            />
          </div>
        </ModalBody>

        <ModalFooter>
          <Button
            type="button"
            variant="ghost"
            onClick={handleClose}
            disabled={isPending}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            isLoading={isPending}
            disabled={!name.trim() || isPending}
          >
            Clone Profile
          </Button>
        </ModalFooter>
      </form>
    </Modal>
  );
};
