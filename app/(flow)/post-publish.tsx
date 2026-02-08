import React, { useEffect, useMemo } from 'react';
import { BackHandler, StyleSheet, Text, View } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Screen } from '@/src/components/Screen';
import { PrimaryButton } from '@/src/components/PrimaryButton';
import { tokens } from '@/src/design/tokens';
import { useAppState } from '@/src/state/app-state';

export default function PostPublishRoute() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const { recents, selectedAssetId } = useAppState();
  const assetId = typeof id === 'string' ? id : selectedAssetId ?? undefined;
  const asset = useMemo(() => recents.find((a) => a.id === assetId), [assetId, recents]);

  const suggestion = useMemo(() => {
    if (!asset) return 'Try a second version with a slightly different tone.';
    switch (asset.assetType) {
      case 'Instagram Post':
        return 'This would work well as a Story.';
      case 'Instagram Story':
        return 'This could be re-used as a Feed post.';
      case 'LinkedIn Banner':
        return 'This pairs nicely with a short LinkedIn post.';
      case 'Logo Variation':
        return 'This would look great on a business card.';
    }
  }, [asset]);

  // Spec: PostPublish back goes Home
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      router.replace('/(flow)/home');
      return true;
    });
    return () => sub.remove();
  }, []);

  return (
    <Screen style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Published.</Text>
        <Text style={styles.subtitle}>Clean. Consistent. On-brand.</Text>
        <Text style={styles.suggestion}>{suggestion}</Text>
        <PrimaryButton title="Back to Home" onPress={() => router.replace('/(flow)/home')} />
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
  },
  content: {
    alignItems: 'center',
    gap: tokens.spacing.xl,
  },
  title: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
  },
  subtitle: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
  },
  suggestion: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.primary,
    opacity: 0.85,
    textAlign: 'center',
    maxWidth: 320,
  },
});

