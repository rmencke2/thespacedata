import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Image } from 'expo-image';
import { tokens } from '@/src/design/tokens';
import type { PreviewContext } from '@/src/state/app-state';

type ContextPreviewProps = {
  context: PreviewContext;
  message: string;
  seed?: string;
  imageUri?: string | null;
};

function hashToPalette(seed: string) {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  const hue1 = h % 360;
  const hue2 = (hue1 + 28 + ((h >>> 8) % 36)) % 360;
  const c1 = `hsl(${hue1}, 72%, 56%)`;
  const c2 = `hsl(${hue2}, 78%, 48%)`;
  return { c1, c2 };
}

function GeneratedArtwork({
  seed = 'influzer',
  message,
  imageUri,
}: {
  seed?: string;
  message: string;
  imageUri?: string | null;
}) {
  const { c1, c2 } = hashToPalette(seed);
  const headline = message.trim() || 'Something good is taking shape.';
  const hasImage = Boolean(imageUri);

  return (
    <View style={styles.artRoot}>
      {imageUri ? (
        <Image source={{ uri: imageUri }} style={StyleSheet.absoluteFillObject} contentFit="cover" />
      ) : null}

      {/* Brand accents: subtle if photo exists, bold if not */}
      <View
        style={[
          styles.artBg,
          { backgroundColor: c1, opacity: hasImage ? 0.16 : 0.92 },
        ]}
      />
      <View
        style={[
          styles.artBg2,
          { backgroundColor: c2, opacity: hasImage ? 0.18 : 0.85 },
        ]}
      />

      {/* Scrim: helps text contrast on photos */}
      <View style={[styles.artOverlay, { opacity: hasImage ? 1 : 0 }]} />

      <View style={styles.artInner}>
        <Text numberOfLines={3} style={styles.artHeadline}>
          {headline}
        </Text>
        <View style={styles.artBottomRow}>
          <View style={styles.artMetaRow}>
            <View style={styles.artPill} />
            <View style={styles.artPill} />
          </View>

          <View style={styles.watermark}>
            <Text style={styles.watermarkText}>Influzer</Text>
          </View>
        </View>
      </View>
    </View>
  );
}

export function ContextPreview({ context, message, seed, imageUri }: ContextPreviewProps) {
  return (
    <View style={styles.root} accessibilityLabel={`${context} preview`}>
      {context === 'Instagram feed' && (
        <View style={styles.feedFrame}>
          <View style={styles.feedTopBar} />
          <View style={styles.feedMedia}>
            <GeneratedArtwork seed={seed} message={message} imageUri={imageUri} />
          </View>
          <View style={styles.feedCaption}>
            <Text numberOfLines={2} style={styles.contextMessage}>
              {message}
            </Text>
          </View>
        </View>
      )}

      {context === 'Instagram story' && (
        <View style={styles.storyFrame}>
          <View style={styles.storyTopBar} />
          <View style={styles.storyHero}>
            <GeneratedArtwork seed={seed} message={message} imageUri={imageUri} />
          </View>
          <View style={styles.storyTextBlock}>
            <Text numberOfLines={3} style={styles.contextMessageStory}>
              {message}
            </Text>
          </View>
        </View>
      )}

      {context === 'Business card' && (
        <View style={styles.cardStage}>
          <View style={styles.businessCard}>
            <View style={styles.businessLogo} />
            <Text numberOfLines={2} style={styles.contextMessageCard}>
              {message}
            </Text>
            <View style={styles.businessMetaRow}>
              <View style={styles.businessMeta} />
              <View style={styles.businessMeta} />
            </View>
          </View>
        </View>
      )}

      {context === 'Website hero' && (
        <View style={styles.heroFrame}>
          <View style={styles.heroNav} />
          <View style={styles.heroBody}>
            <View style={styles.heroCopy}>
              <Text numberOfLines={2} style={styles.contextMessageHero}>
                {message}
              </Text>
              <View style={styles.heroCta} />
            </View>
            <View style={styles.heroMedia}>
              <GeneratedArtwork seed={seed} message={message} imageUri={imageUri} />
            </View>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    justifyContent: 'center',
  },
  feedFrame: {
    alignSelf: 'center',
    width: '92%',
    aspectRatio: 1,
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.background,
    overflow: 'hidden',
  },
  feedTopBar: {
    height: 40,
    backgroundColor: 'rgba(0,0,0,0.04)',
  },
  feedMedia: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.06)',
    padding: tokens.spacing.md,
  },
  feedCaption: {
    padding: tokens.spacing.md,
  },
  storyFrame: {
    alignSelf: 'center',
    width: '80%',
    aspectRatio: 9 / 16,
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: tokens.colors.background,
    overflow: 'hidden',
  },
  storyTopBar: {
    height: 32,
    backgroundColor: 'rgba(0,0,0,0.04)',
  },
  storyHero: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.06)',
    padding: tokens.spacing.md,
  },
  storyTextBlock: {
    padding: tokens.spacing.md,
  },
  cardStage: {
    alignItems: 'center',
  },
  businessCard: {
    width: '86%',
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.background,
    padding: tokens.spacing.lg,
    gap: tokens.spacing.md,
  },
  businessLogo: {
    width: 44,
    height: 10,
    borderRadius: 6,
    backgroundColor: 'rgba(0,0,0,0.12)',
  },
  businessMetaRow: {
    flexDirection: 'row',
    gap: tokens.spacing.sm,
  },
  businessMeta: {
    flex: 1,
    height: 10,
    borderRadius: 6,
    backgroundColor: 'rgba(0,0,0,0.08)',
  },
  heroFrame: {
    alignSelf: 'center',
    width: '92%',
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.background,
    overflow: 'hidden',
  },
  heroNav: {
    height: 40,
    backgroundColor: 'rgba(0,0,0,0.04)',
  },
  heroBody: {
    flexDirection: 'row',
    padding: tokens.spacing.lg,
    gap: tokens.spacing.lg,
    alignItems: 'center',
  },
  heroCopy: {
    flex: 1,
    gap: tokens.spacing.md,
  },
  heroCta: {
    width: 120,
    height: 28,
    borderRadius: tokens.borderRadius.md,
    backgroundColor: 'rgba(0,0,0,0.10)',
  },
  heroMedia: {
    width: 110,
    height: 110,
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: 'rgba(0,0,0,0.06)',
    overflow: 'hidden',
  },
  contextMessage: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
    lineHeight: 22,
  },
  contextMessageStory: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
    lineHeight: 24,
  },
  contextMessageCard: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.text.primary,
    lineHeight: 22,
  },
  contextMessageHero: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
    lineHeight: 24,
  },
  // ---- Generated Artwork (the "asset") ----
  artRoot: {
    flex: 1,
    borderRadius: tokens.borderRadius.lg,
    overflow: 'hidden',
    minHeight: 140,
  },
  artBg: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.92,
  },
  artBg2: {
    ...StyleSheet.absoluteFillObject,
    left: '42%',
    opacity: 0.85,
    transform: [{ rotate: '-10deg' }],
  },
  artOverlay: {
    ...StyleSheet.absoluteFillObject,
    // Helps text contrast, especially on uploaded photos
    backgroundColor: 'rgba(0,0,0,0.35)',
  },
  artInner: {
    flex: 1,
    padding: tokens.spacing.md,
    justifyContent: 'space-between',
  },
  artHeadline: {
    fontSize: tokens.typography.fontSize.xl,
    lineHeight: 28,
    color: '#FFFFFF',
    fontWeight: tokens.typography.fontWeight.bold,
    textShadowColor: 'rgba(0,0,0,0.14)',
    textShadowRadius: 10,
  },
  artBottomRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    justifyContent: 'space-between',
    gap: tokens.spacing.sm,
  },
  artMetaRow: {
    flexDirection: 'row',
    gap: tokens.spacing.sm,
    flex: 1,
  },
  artPill: {
    flex: 1,
    height: 10,
    borderRadius: 6,
    backgroundColor: 'rgba(255,255,255,0.55)',
  },
  watermark: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 999,
    backgroundColor: 'rgba(0,0,0,0.18)',
  },
  watermarkText: {
    fontSize: 11,
    letterSpacing: 0.2,
    color: 'rgba(255,255,255,0.88)',
    fontWeight: tokens.typography.fontWeight.semibold,
  },
});

