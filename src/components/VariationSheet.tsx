import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Animated,
  Modal,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { tokens } from '@/src/design/tokens';
import type { Variation } from '@/src/state/app-state';

type VariationSheetProps = {
  visible: boolean;
  variations: Variation[];
  selectedVariationId: string;
  onSelect: (variationId: string) => void;
  onClose: () => void;
};

export function VariationSheet({
  visible,
  variations,
  selectedVariationId,
  onSelect,
  onClose,
}: VariationSheetProps) {
  const translateY = useRef(new Animated.Value(40)).current;
  const backdrop = useRef(new Animated.Value(0)).current;
  const [picked, setPicked] = useState<string | null>(null);
  const opacities = useRef<Record<string, Animated.Value>>({}).current;

  const ids = useMemo(() => variations.map((v) => v.id), [variations]);

  // Ensure opacity values exist for current ids
  useEffect(() => {
    ids.forEach((id) => {
      if (!opacities[id]) opacities[id] = new Animated.Value(1);
    });
  }, [ids, opacities]);

  useEffect(() => {
    if (!visible) return;

    setPicked(null);
    ids.forEach((id) => opacities[id]?.setValue(1));
    translateY.setValue(40);
    backdrop.setValue(0);

    Animated.parallel([
      Animated.timing(backdrop, { toValue: 1, duration: 180, useNativeDriver: true }),
      Animated.timing(translateY, { toValue: 0, duration: 220, useNativeDriver: true }),
    ]).start();
  }, [backdrop, ids, opacities, translateY, visible]);

  const commitSelection = (id: string) => {
    if (picked) return;
    setPicked(id);

    const fades = ids
      .filter((x) => x !== id)
      .map((x) =>
        Animated.timing(opacities[x]!, { toValue: 0.2, duration: 180, useNativeDriver: true })
      );

    Animated.parallel(fades).start(() => {
      onSelect(id);
      onClose();
    });
  };

  return (
    <Modal visible={visible} transparent animationType="none" onRequestClose={onClose}>
      <View style={styles.root}>
        <Pressable onPress={onClose} style={StyleSheet.absoluteFill}>
          <Animated.View style={[styles.backdrop, { opacity: backdrop }]} />
        </Pressable>

        <Animated.View style={[styles.sheet, { transform: [{ translateY }] }]}>
          <View style={styles.handle} />
          <Text style={styles.title}>Choose the one that feels right.</Text>

          <View style={styles.list}>
            {variations.slice(0, 3).map((v) => {
              const selected = (picked ?? selectedVariationId) === v.id;
              return (
                <Animated.View key={v.id} style={{ opacity: opacities[v.id] ?? 1 }}>
                  <Pressable
                    onPress={() => commitSelection(v.id)}
                    style={({ pressed }) => [
                      styles.card,
                      selected && styles.cardSelected,
                      pressed && styles.pressed,
                    ]}
                  >
                    <Text style={[styles.cardLabel, selected && styles.cardLabelSelected]}>
                      {v.label}
                    </Text>
                    <Text style={[styles.cardMessage, selected && styles.cardMessageSelected]}>
                      {v.message}
                    </Text>
                  </Pressable>
                </Animated.View>
              );
            })}
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.45)',
  },
  sheet: {
    backgroundColor: tokens.colors.background,
    borderTopLeftRadius: tokens.borderRadius.xl,
    borderTopRightRadius: tokens.borderRadius.xl,
    padding: tokens.spacing.lg,
    gap: tokens.spacing.lg,
  },
  handle: {
    alignSelf: 'center',
    width: 44,
    height: 5,
    borderRadius: 3,
    backgroundColor: tokens.colors.text.tertiary,
    opacity: 0.6,
  },
  title: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
  },
  list: {
    gap: tokens.spacing.md,
  },
  card: {
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.lg,
    gap: tokens.spacing.sm,
  },
  cardSelected: {
    backgroundColor: tokens.colors.text.primary,
  },
  pressed: {
    opacity: 0.9,
  },
  cardLabel: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  cardLabelSelected: {
    color: tokens.colors.background,
    opacity: 0.8,
  },
  cardMessage: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
  },
  cardMessageSelected: {
    color: tokens.colors.background,
  },
});

