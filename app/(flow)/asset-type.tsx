import React from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { router } from 'expo-router';
import { Screen } from '@/src/components/Screen';
import { tokens } from '@/src/design/tokens';
import { AssetType, useAppState } from '@/src/state/app-state';

export default function AssetTypeRoute() {
  const { actions } = useAppState();

  const options: AssetType[] = [
    'Instagram Post',
    'Instagram Story',
    'LinkedIn Banner',
    'Logo Variation',
  ];

  return (
    <Screen>
      <Text style={styles.title}>What are you creating?</Text>
      <View style={styles.list}>
        {options.map((opt) => (
          <Pressable
            key={opt}
            onPress={() => {
              actions.setAssetType(opt);
              router.push('/(flow)/message');
            }}
            style={({ pressed }) => [styles.card, pressed && styles.pressed]}
          >
            <Text style={styles.cardTitle}>{opt}</Text>
          </Pressable>
        ))}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
    marginBottom: tokens.spacing.lg,
  },
  list: {
    gap: tokens.spacing.md,
  },
  card: {
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.lg,
  },
  pressed: {
    opacity: 0.85,
  },
  cardTitle: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
  },
});

