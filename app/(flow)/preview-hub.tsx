import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Modal,
  PanResponder,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  useWindowDimensions,
  View,
} from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Screen } from '@/src/components/Screen';
import { PrimaryButton } from '@/src/components/PrimaryButton';
import { ContextPreview } from '@/src/components/ContextPreview';
import { tokens } from '@/src/design/tokens';
import { useAppState } from '@/src/state/app-state';
import { VariationSheet } from '@/src/components/VariationSheet';

export default function PreviewHubRoute() {
  const { id, page: pageParam } = useLocalSearchParams<{ id?: string; page?: string }>();
  const { recents, selectedAssetId, actions } = useAppState();
  const assetId = typeof id === 'string' ? id : selectedAssetId ?? undefined;
  const { width: windowWidth } = useWindowDimensions();

  const asset = useMemo(() => {
    if (!assetId) return undefined;
    return recents.find((a) => a.id === assetId);
  }, [assetId, recents]);

  const scrollRef = useRef<ScrollView | null>(null);
  const [page, setPage] = useState(0);
  const [layoutW, setLayoutW] = useState<number | null>(null);
  const [zoomOpen, setZoomOpen] = useState(false);
  const [variationsOpen, setVariationsOpen] = useState(false);

  const panResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 12 && Math.abs(g.dx) < 12,
      onPanResponderRelease: (_, g) => {
        if (g.dy < -40) setVariationsOpen(true);
      },
    })
  ).current;

  const previewCount = asset?.previews.length ?? 0;
  const lastPreviewIndex = asset?.lastPreviewIndex ?? 0;

  const initialPage = useMemo(() => {
    if (previewCount <= 0) return 0;
    const maxIndex = previewCount - 1;

    const n = pageParam ? Number(pageParam) : NaN;
    if (Number.isFinite(n)) return Math.max(0, Math.min(maxIndex, n));

    return Math.max(0, Math.min(maxIndex, lastPreviewIndex));
  }, [lastPreviewIndex, pageParam, previewCount]);

  const pageWidth = useMemo(() => {
    // ScrollView is inside <Screen padding={lg}>, so the content width is smaller than window width.
    // We prefer the measured width, but fall back to a reasonable estimate.
    if (layoutW && layoutW > 0) return layoutW;
    return Math.max(0, windowWidth - tokens.spacing.lg * 2);
  }, [layoutW, windowWidth]);

  useEffect(() => {
    if (!layoutW) return;
    if (!scrollRef.current) return;
    if (previewCount <= 0) return;
    // jump to the last/desired preview page without animation
    scrollRef.current.scrollTo({ x: layoutW * initialPage, animated: false });
    setPage(initialPage);
  }, [initialPage, layoutW, previewCount]);

  if (!asset) {
    return (
      <Screen style={styles.center}>
        <Text style={styles.title}>Preview</Text>
        <Text style={styles.subtitle}>Nothing to preview yet.</Text>
        <PrimaryButton title="Create something new" onPress={() => router.replace('/(flow)/asset-type')} />
      </Screen>
    );
  }

  const selectedMessage =
    asset.variations.find((v) => v.id === asset.selectedVariationId)?.message ?? asset.message;

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.title}>Preview</Text>
        <Text style={styles.subtitle}>
          {asset.assetType}
        </Text>
      </View>

      <ScrollView
        ref={(r) => {
          scrollRef.current = r;
        }}
        onLayout={(e) => setLayoutW(e.nativeEvent.layout.width)}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(e) => {
          const w = e.nativeEvent.layoutMeasurement.width;
          const x = e.nativeEvent.contentOffset.x;
          const next = Math.round(x / w);
          setPage(next);
          actions.setLastPreviewIndex(asset.id, next);
        }}
        contentContainerStyle={styles.pager}
      >
        {asset.previews.map((p) => (
          <View key={p.id} style={[styles.page, { width: pageWidth }]}>
            <Pressable
              onLongPress={() => setZoomOpen(true)}
              delayLongPress={220}
              style={styles.previewFrame}
              {...panResponder.panHandlers}
            >
              <Text style={styles.previewContext}>{p.context}</Text>

              <View style={styles.contextStage}>
                <ContextPreview
                  context={p.context}
                  message={selectedMessage}
                  seed={asset.id}
                  imageUri={asset.imageUri}
                />
              </View>

              <Text style={styles.previewHint}>Long-press to zoom • Swipe up</Text>
            </Pressable>
          </View>
        ))}
      </ScrollView>

      <View style={styles.controls}>
        <Pressable
          onPress={() => {
            // keep draft as-is; go re-generate
            actions.selectAsset(asset.id);
            router.push('/(flow)/generation');
          }}
          style={({ pressed }) => [styles.textButton, pressed && styles.pressed]}
        >
          <Text style={styles.textButtonLabel}>Regenerate</Text>
        </Pressable>

        <View style={styles.dots}>
          {asset.previews.map((p, i) => (
            <View key={p.id} style={[styles.dot, i === page && styles.dotActive]} />
          ))}
        </View>
      </View>

      <View style={styles.footer}>
        <PrimaryButton
          title="Publish"
          onPress={() =>
            router.push({
              pathname: '/(flow)/publish',
              params: { id: asset.id, page: String(page) },
            })
          }
        />
      </View>

      <VariationSheet
        visible={variationsOpen}
        variations={asset.variations}
        selectedVariationId={asset.selectedVariationId}
        onSelect={(variationId) => actions.selectVariation(asset.id, variationId)}
        onClose={() => setVariationsOpen(false)}
      />

      <Modal visible={zoomOpen} transparent animationType="fade" onRequestClose={() => setZoomOpen(false)}>
        <Pressable style={styles.zoomBackdrop} onPress={() => setZoomOpen(false)}>
          <View style={styles.zoomCard}>
            <Text style={styles.zoomTitle}>{asset.previews[page]?.context ?? 'Preview'}</Text>
            <Text style={styles.zoomMessage}>
              {selectedMessage}
            </Text>
          </View>
        </Pressable>
      </Modal>
    </Screen>
  );
}

const styles = StyleSheet.create({
  center: {
    justifyContent: 'center',
    alignItems: 'center',
    gap: tokens.spacing.md,
  },
  header: {
    gap: tokens.spacing.xs,
    marginBottom: tokens.spacing.lg,
  },
  title: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
  },
  subtitle: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  pager: {
    // spacing handled by page itself
  },
  page: {
    // width is set dynamically to the ScrollView width
  },
  previewFrame: {
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.lg,
    minHeight: 360,
    justifyContent: 'space-between',
  },
  contextStage: {
    flex: 1,
    justifyContent: 'center',
  },
  previewContext: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  previewHint: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
    opacity: 0.7,
  },
  controls: {
    marginTop: tokens.spacing.lg,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  textButton: {
    paddingVertical: tokens.spacing.sm,
    paddingHorizontal: tokens.spacing.sm,
  },
  pressed: {
    opacity: 0.8,
  },
  textButtonLabel: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.primary,
    fontWeight: tokens.typography.fontWeight.medium,
  },
  dots: {
    flexDirection: 'row',
    gap: tokens.spacing.xs,
    alignItems: 'center',
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: tokens.colors.text.tertiary,
  },
  dotActive: {
    backgroundColor: tokens.colors.text.primary,
  },
  footer: {
    marginTop: tokens.spacing.xl,
  },
  zoomBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.55)',
    justifyContent: 'center',
    padding: tokens.spacing.lg,
  },
  zoomCard: {
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: tokens.colors.background,
    padding: tokens.spacing.lg,
    gap: tokens.spacing.md,
  },
  zoomTitle: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  zoomMessage: {
    fontSize: tokens.typography.fontSize.xl,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
    lineHeight: 28,
  },
});

