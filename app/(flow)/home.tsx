import React from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { router } from 'expo-router';
import { Screen } from '@/src/components/Screen';
import { PrimaryButton } from '@/src/components/PrimaryButton';
import { tokens } from '@/src/design/tokens';
import { useAppState } from '@/src/state/app-state';

export default function HomeRoute() {
  const { recents, actions } = useAppState();

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.title}>Home</Text>
      </View>

      <PrimaryButton
        title="Create something new"
        onPress={() => {
          actions.resetDraft();
          router.push('/(flow)/asset-type');
        }}
      />

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent</Text>
        {recents.length === 0 ? (
          <Text style={styles.empty}>
            Nothing yet. Create your first asset — we’ll keep it here for quick access.
          </Text>
        ) : (
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.recentsRow}
          >
            {recents.map((a) => (
              <Pressable
                key={a.id}
                onPress={() => {
                  actions.selectAsset(a.id);
                  router.push({
                    pathname: '/(flow)/preview-hub',
                    params: { id: a.id, page: String(a.lastPreviewIndex ?? 0) },
                  });
                }}
                style={({ pressed }) => [styles.recentCard, pressed && styles.pressed]}
              >
                <View style={styles.recentTopRow}>
                  <Text style={styles.recentType}>{a.assetType}</Text>
                  <View style={[styles.statusPill, a.status === 'published' && styles.statusPillPublished]}>
                    <Text style={[styles.statusText, a.status === 'published' && styles.statusTextPublished]}>
                      {a.status === 'published' ? 'Published' : 'Saved'}
                    </Text>
                  </View>
                </View>
                <Text numberOfLines={2} style={styles.recentMessage}>
                  {a.message}
                </Text>
              </Pressable>
            ))}
          </ScrollView>
        )}
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: {
    marginBottom: tokens.spacing.xl,
  },
  title: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
  },
  section: {
    marginTop: tokens.spacing.xl,
    gap: tokens.spacing.md,
  },
  sectionTitle: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
  },
  empty: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
    maxWidth: 340,
  },
  recentsRow: {
    gap: tokens.spacing.md,
    paddingVertical: tokens.spacing.sm,
  },
  recentCard: {
    width: 220,
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.md,
    gap: tokens.spacing.sm,
  },
  recentTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: tokens.spacing.sm,
  },
  pressed: {
    opacity: 0.85,
  },
  recentType: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
    flexShrink: 1,
  },
  statusPill: {
    paddingHorizontal: tokens.spacing.sm,
    paddingVertical: 4,
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: 'rgba(0,0,0,0.06)',
  },
  statusPillPublished: {
    backgroundColor: 'rgba(52, 199, 89, 0.14)',
  },
  statusText: {
    fontSize: tokens.typography.fontSize.xs,
    color: tokens.colors.text.secondary,
    fontWeight: tokens.typography.fontWeight.medium,
  },
  statusTextPublished: {
    color: '#0A7A2F',
  },
  recentMessage: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.text.primary,
  },
});

