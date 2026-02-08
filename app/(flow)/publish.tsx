import React, { useCallback, useMemo, useRef, useState } from 'react';
import { Alert, Pressable, Share, StyleSheet, Text, View } from 'react-native';
import * as Clipboard from 'expo-clipboard';
import { router, useLocalSearchParams } from 'expo-router';
import { captureRef } from 'react-native-view-shot';
import { FontAwesome } from '@expo/vector-icons';
import { Screen } from '@/src/components/Screen';
import { PrimaryButton } from '@/src/components/PrimaryButton';
import { SignUpModal } from '@/src/components/SignUpModal';
import { ContextPreview } from '@/src/components/ContextPreview';
import { tokens } from '@/src/design/tokens';
import { useAppState } from '@/src/state/app-state';

function getExportSize(assetType: string) {
  // Keep it simple and consistent: export at common social sizes.
  switch (assetType) {
    case 'Instagram Story':
      return { width: 1080, height: 1920 };
    case 'LinkedIn Banner':
      return { width: 1584, height: 396 };
    case 'Logo Variation':
      return { width: 1024, height: 1024 };
    case 'Instagram Post':
    default:
      return { width: 1080, height: 1080 };
  }
}

export default function PublishRoute() {
  const { id, page: pageParam } = useLocalSearchParams<{ id?: string; page?: string }>();
  const { recents, selectedAssetId, actions, user } = useAppState();
  const assetId = typeof id === 'string' ? id : selectedAssetId ?? undefined;
  const asset = useMemo(() => recents.find((a) => a.id === assetId), [assetId, recents]);
  const [copied, setCopied] = useState(false);
  const [signUpModalVisible, setSignUpModalVisible] = useState(false);
  const [signUpActionLabel, setSignUpActionLabel] = useState('download and share your creation');
  const pendingActionRef = useRef<(() => void) | null>(null);
  const exportRef = useRef<View | null>(null);

  const requireSignUp = useCallback(
    (action: () => void, actionLabel: string) => {
      if (user) {
        action();
        return;
      }
      pendingActionRef.current = action;
      setSignUpActionLabel(actionLabel);
      setSignUpModalVisible(true);
    },
    [user]
  );

  const handleSignUpAndContinue = useCallback(() => {
    actions.signIn();
    pendingActionRef.current?.();
    pendingActionRef.current = null;
    setSignUpModalVisible(false);
  }, [actions]);

  const handleCloseSignUpModal = useCallback(() => {
    pendingActionRef.current = null;
    setSignUpModalVisible(false);
  }, []);

  const caption = useMemo(() => {
    if (!asset) return '';
    const v =
      asset.variations.find((x) => x.id === asset.selectedVariationId)?.message ?? asset.message;
    return v;
  }, [asset]);

  const handleCopyCaption = async () => {
    if (!caption) return;
    await Clipboard.setStringAsync(caption);
    setCopied(true);
    setTimeout(() => setCopied(false), 1100);
  };

  const handleShare = async () => {
    if (!caption) return;
    await Share.share({ message: caption });
  };

  const exportImage = async () => {
    if (!asset) return;
    if (!exportRef.current) return;

    try {
      const { width, height } = getExportSize(asset.assetType);
      const uri = await captureRef(exportRef.current, {
        format: 'png',
        quality: 1,
        result: 'tmpfile',
        width,
        height,
      });
      return uri;
    } catch {
      Alert.alert('Could not export', 'Please try again.', [{ text: 'OK' }]);
      return null;
    }
  };

  const handleShareTo = useCallback(
    async (target: 'instagram' | 'linkedin') => {
      const uri = await exportImage();
      if (!uri) return;
      await Share.share(
        { url: uri, message: caption },
        {
          dialogTitle: target === 'instagram' ? 'Share to Instagram' : 'Share to LinkedIn',
        }
      );
    },
    [asset, caption]
  );

  const handleDownload = useCallback(async () => {
    const uri = await exportImage();
    if (!uri) return;
    await Share.share({ url: uri, message: caption }, { dialogTitle: 'Save or share' });
  }, [asset, caption]);

  const handleShareNow = useCallback(async () => {
    await Share.share({ message: caption });
    actions.markPublished(asset!.id);
    router.push({ pathname: '/(flow)/post-publish', params: { id: asset!.id } });
  }, [actions, asset, caption]);

  if (!asset) {
    return (
      <Screen style={styles.container}>
        <View style={styles.content}>
          <Text style={styles.title}>Publish</Text>
          <Text style={styles.subtitle}>Nothing to publish yet.</Text>
          <PrimaryButton title="Create something new" onPress={() => router.replace('/(flow)/asset-type')} />
        </View>
      </Screen>
    );
  }

  const previewCount = asset.previews.length;
  const maxIndex = Math.max(0, previewCount - 1);
  const pageFromParam = pageParam ? Number(pageParam) : NaN;
  const exportPage = Number.isFinite(pageFromParam)
    ? Math.max(0, Math.min(maxIndex, pageFromParam))
    : Math.max(0, Math.min(maxIndex, asset.lastPreviewIndex ?? 0));
  const exportContext = asset.previews[exportPage]?.context ?? 'Instagram feed';

  return (
    <Screen>
      <View style={styles.header}>
        <Text style={styles.title}>Publish</Text>
        <Text style={styles.subtitle}>{asset.assetType}</Text>
      </View>

      <View style={styles.previewWrap}>
        <View
          ref={(r) => {
            exportRef.current = r;
          }}
          collapsable={false}
          style={styles.exportStage}
        >
          <View style={styles.exportHeaderRow}>
            <Text style={styles.exportBrand}>Influzer</Text>
            <Text style={styles.exportContextLabel}>{exportContext}</Text>
          </View>

          <ContextPreview context={exportContext} message={caption} seed={asset.id} imageUri={asset.imageUri} />
        </View>
      </View>

      <View style={styles.actionsRow}>
        <View style={styles.actionGrid}>
          <Pressable
            onPress={() =>
              requireSignUp(
                () => void handleDownload(),
                asset.assetType === 'Logo Variation' ? 'download your logo' : 'download your creation'
              )
            }
            style={({ pressed }) => [styles.action, pressed && styles.pressed]}
          >
            <FontAwesome name="download" size={18} color={tokens.colors.text.primary} />
            <Text style={styles.actionLabel}>Download</Text>
          </Pressable>

          <Pressable
            onPress={() =>
              requireSignUp(
                () => void handleShareTo('instagram'),
                'share to Instagram'
              )
            }
            style={({ pressed }) => [styles.action, pressed && styles.pressed]}
          >
            <FontAwesome name="instagram" size={18} color={tokens.colors.text.primary} />
            <Text style={styles.actionLabel}>Instagram</Text>
          </Pressable>

          <Pressable
            onPress={() =>
              requireSignUp(
                () => void handleShareTo('linkedin'),
                'share to LinkedIn'
              )
            }
            style={({ pressed }) => [styles.action, pressed && styles.pressed]}
          >
            <FontAwesome name="linkedin" size={18} color={tokens.colors.text.primary} />
            <Text style={styles.actionLabel}>LinkedIn</Text>
          </Pressable>

          <Pressable
            onPress={handleCopyCaption}
            style={({ pressed }) => [styles.action, pressed && styles.pressed]}
          >
            <FontAwesome name="copy" size={18} color={tokens.colors.text.primary} />
            <Text style={styles.actionLabel}>{copied ? 'Copied' : 'Copy caption'}</Text>
          </Pressable>
        </View>
      </View>

      <View style={styles.captionCard}>
        <Text style={styles.captionLabel}>Caption</Text>
        <Text style={styles.captionText}>{caption}</Text>
      </View>

      <View style={styles.footer}>
        <PrimaryButton
          title="Share now"
          onPress={() =>
            requireSignUp(
              () => void handleShareNow(),
              asset.assetType === 'Logo Variation' ? 'share your logo' : 'share your creation'
            )
          }
        />

        <Pressable
          onPress={() => {
            // Spec: save for later should not imply "published"
            router.replace('/(flow)/home');
          }}
          style={({ pressed }) => [styles.secondaryCta, pressed && styles.pressed]}
        >
          <Text style={styles.secondaryCtaLabel}>Save for later</Text>
        </Pressable>
      </View>

      <SignUpModal
        visible={signUpModalVisible}
        onClose={handleCloseSignUpModal}
        onSignUp={handleSignUpAndContinue}
        actionLabel={signUpActionLabel}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
  },
  content: {
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
  actionsRow: {
    marginTop: tokens.spacing.sm,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: tokens.spacing.sm,
  },
  previewWrap: {
    marginBottom: tokens.spacing.lg,
    alignItems: 'center',
  },
  exportStage: {
    width: '100%',
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.lg,
    gap: tokens.spacing.sm,
    minHeight: 320,
  },
  exportHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: tokens.spacing.sm,
    alignItems: 'baseline',
  },
  exportBrand: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
    fontWeight: tokens.typography.fontWeight.semibold,
    letterSpacing: 0.3,
  },
  exportContextLabel: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.tertiary,
  },
  action: {
    width: '48%',
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    paddingVertical: tokens.spacing.md,
    paddingHorizontal: tokens.spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  actionLabel: {
    fontSize: tokens.typography.fontSize.sm,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.text.primary,
  },
  pressed: {
    opacity: 0.85,
  },
  captionCard: {
    marginTop: tokens.spacing.lg,
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.lg,
    gap: tokens.spacing.sm,
  },
  captionLabel: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  captionText: {
    fontSize: tokens.typography.fontSize.lg,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
    lineHeight: 26,
  },
  footer: {
    marginTop: tokens.spacing.xl,
    gap: tokens.spacing.md,
  },
  secondaryCta: {
    paddingVertical: tokens.spacing.md,
    alignItems: 'center',
  },
  secondaryCtaLabel: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.text.primary,
  },
});

