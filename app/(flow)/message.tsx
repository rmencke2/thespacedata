import React, { useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, TextInput, View } from 'react-native';
import { router } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import { Image } from 'expo-image';
import { Screen } from '@/src/components/Screen';
import { PrimaryButton } from '@/src/components/PrimaryButton';
import { tokens } from '@/src/design/tokens';
import { Tone, useAppState } from '@/src/state/app-state';
import { suggestTextFromImage } from '@/src/utils/suggest-text';

export default function MessageRoute() {
  const { draft, actions } = useAppState();
  const [message, setMessage] = useState(draft.message);
  const [tone, setTone] = useState<Tone>(draft.tone);
  const [imageUri, setImageUri] = useState<string | null>(draft.imageUri);

  const canGenerate = useMemo(() => message.trim().length > 0, [message]);

  const pickImage = async () => {
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) return;

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 1,
      allowsEditing: true,
    });

    if (result.canceled) return;
    const uri = result.assets?.[0]?.uri ?? null;
    setImageUri(uri);
    actions.setImageUri(uri);
  };

  const suggestions = useMemo(() => {
    if (!imageUri) return [];
    return suggestTextFromImage({ assetType: draft.assetType, tone, imageUri });
  }, [draft.assetType, imageUri, tone]);

  return (
    <Screen>
      <Text style={styles.title}>What should it say?</Text>

      <TextInput
        value={message}
        onChangeText={setMessage}
        placeholder="Grand opening this Saturday"
        placeholderTextColor={tokens.colors.text.tertiary}
        multiline
        textAlignVertical="top"
        style={styles.input}
      />

      <View style={styles.imageBlock}>
        <View style={styles.imageHeader}>
          <Text style={styles.imageLabel}>Image (optional)</Text>
          <Pressable onPress={pickImage} style={({ pressed }) => [styles.linkButton, pressed && styles.pressed]}>
            <Text style={styles.linkButtonLabel}>{imageUri ? 'Change' : 'Upload'}</Text>
          </Pressable>
        </View>

        {imageUri ? (
          <View style={styles.thumbRow}>
            <Image source={{ uri: imageUri }} style={styles.thumb} contentFit="cover" />
            <Pressable
              onPress={() => {
                setImageUri(null);
                actions.setImageUri(null);
              }}
              style={({ pressed }) => [styles.removeButton, pressed && styles.pressed]}
            >
              <Text style={styles.removeButtonLabel}>Remove</Text>
            </Pressable>
          </View>
        ) : (
          <Text style={styles.imageHint}>
            Upload a photo and we’ll make it look intentional with clean type and contrast.
          </Text>
        )}

        {imageUri && suggestions.length > 0 ? (
          <View style={styles.suggestions}>
            <Text style={styles.suggestionsLabel}>Suggested text</Text>
            {suggestions.map((s) => (
              <Pressable
                key={s}
                onPress={() => setMessage(s)}
                style={({ pressed }) => [styles.suggestionCard, pressed && styles.pressed]}
              >
                <Text style={styles.suggestionText}>{s}</Text>
                <Text style={styles.suggestionHint}>Tap to use</Text>
              </Pressable>
            ))}
          </View>
        ) : null}
      </View>

      <View style={styles.toneBlock}>
        <Text style={styles.toneLabel}>Tone (optional)</Text>
        <View style={styles.toneRow}>
          {(['Neutral', 'Confident', 'Friendly'] as Tone[]).map((t) => {
            const selected = tone === t;
            return (
              <Pressable
                key={t}
                onPress={() => setTone(t)}
                style={({ pressed }) => [
                  styles.toneChip,
                  selected && styles.toneChipSelected,
                  pressed && styles.pressed,
                ]}
              >
                <Text style={[styles.toneChipText, selected && styles.toneChipTextSelected]}>
                  {t}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </View>

      <View style={styles.footer}>
        <PrimaryButton
          title="Generate"
          disabled={!canGenerate}
          onPress={() => {
            actions.setMessage(message);
            actions.setTone(tone);
            actions.setImageUri(imageUri);
            router.push('/(flow)/generation');
          }}
        />
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
  input: {
    minHeight: 160,
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.lg,
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.primary,
    marginBottom: tokens.spacing.lg,
  },
  toneBlock: {
    gap: tokens.spacing.sm,
  },
  imageBlock: {
    marginBottom: tokens.spacing.lg,
    gap: tokens.spacing.sm,
  },
  imageHeader: {
    flexDirection: 'row',
    alignItems: 'baseline',
    justifyContent: 'space-between',
  },
  imageLabel: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  linkButton: {
    paddingVertical: tokens.spacing.sm,
    paddingHorizontal: tokens.spacing.sm,
  },
  linkButtonLabel: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.text.primary,
  },
  imageHint: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
    maxWidth: 360,
  },
  thumbRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: tokens.spacing.md,
  },
  thumb: {
    width: 76,
    height: 76,
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
  },
  removeButton: {
    flex: 1,
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    paddingVertical: tokens.spacing.md,
    alignItems: 'center',
  },
  removeButtonLabel: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.medium,
    color: tokens.colors.text.primary,
  },
  suggestions: {
    marginTop: tokens.spacing.sm,
    gap: tokens.spacing.sm,
  },
  suggestionsLabel: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  suggestionCard: {
    borderRadius: tokens.borderRadius.lg,
    backgroundColor: tokens.colors.surface,
    padding: tokens.spacing.md,
    gap: 4,
  },
  suggestionText: {
    fontSize: tokens.typography.fontSize.md,
    fontWeight: tokens.typography.fontWeight.semibold,
    color: tokens.colors.text.primary,
  },
  suggestionHint: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.tertiary,
  },
  toneLabel: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.secondary,
  },
  toneRow: {
    flexDirection: 'row',
    gap: tokens.spacing.sm,
    flexWrap: 'wrap',
  },
  toneChip: {
    paddingVertical: tokens.spacing.sm,
    paddingHorizontal: tokens.spacing.md,
    borderRadius: tokens.borderRadius.xl,
    backgroundColor: tokens.colors.surface,
  },
  toneChipSelected: {
    backgroundColor: tokens.colors.text.primary,
  },
  toneChipText: {
    fontSize: tokens.typography.fontSize.sm,
    color: tokens.colors.text.primary,
    fontWeight: tokens.typography.fontWeight.medium,
  },
  toneChipTextSelected: {
    color: tokens.colors.background,
  },
  pressed: {
    opacity: 0.85,
  },
  footer: {
    marginTop: tokens.spacing.xl,
  },
});

