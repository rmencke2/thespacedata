import React from 'react';
import { Modal, Pressable, StyleSheet, Text, View } from 'react-native';
import { PrimaryButton } from '@/src/components/PrimaryButton';
import { tokens } from '@/src/design/tokens';

type SignUpModalProps = {
  visible: boolean;
  onClose: () => void;
  onSignUp: () => void;
  /** Optional: e.g. "download your logo" */
  actionLabel?: string;
};

export function SignUpModal({
  visible,
  onClose,
  onSignUp,
  actionLabel = 'download and share your creation',
}: SignUpModalProps) {
  const handleSignUp = () => {
    onSignUp();
    onClose();
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.card} onPress={() => {}}>
          <Text style={styles.title}>Sign up to continue</Text>
          <Text style={styles.subtitle}>
            Create a free account to {actionLabel}.
          </Text>
          <PrimaryButton title="Sign up" onPress={handleSignUp} />
          <Pressable
            onPress={onClose}
            style={({ pressed }) => [styles.cancel, pressed && styles.pressed]}
          >
            <Text style={styles.cancelLabel}>Maybe later</Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: tokens.spacing.lg,
  },
  card: {
    width: '100%',
    maxWidth: 340,
    backgroundColor: tokens.colors.background,
    borderRadius: tokens.borderRadius.xl,
    padding: tokens.spacing.xl,
    gap: tokens.spacing.lg,
  },
  title: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
  },
  subtitle: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
    lineHeight: 22,
  },
  cancel: {
    paddingVertical: tokens.spacing.sm,
    alignItems: 'center',
  },
  cancelLabel: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
  },
  pressed: {
    opacity: 0.85,
  },
});
