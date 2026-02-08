import React, { useEffect, useRef } from 'react';
import { Animated, BackHandler, StyleSheet, Text, View } from 'react-native';
import { router } from 'expo-router';
import { Screen } from '@/src/components/Screen';
import { tokens } from '@/src/design/tokens';
import { useAppState } from '@/src/state/app-state';

export default function GenerationRoute() {
  const { draft, actions } = useAppState();
  const pulse = useRef(new Animated.Value(0.25)).current;
  const startedRef = useRef(false);
  const navigatedRef = useRef(false);

  // Spec: back disabled on Generation
  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => true);
    return () => sub.remove();
  }, []);

  useEffect(() => {
    const anim = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, { toValue: 0.9, duration: 700, useNativeDriver: true }),
        Animated.timing(pulse, { toValue: 0.25, duration: 700, useNativeDriver: true }),
      ])
    );
    anim.start();
    return () => anim.stop();
  }, [pulse]);

  useEffect(() => {
    // Guard: if user somehow reaches here without inputs, send them back
    if (!draft.assetType) {
      router.replace('/(flow)/asset-type');
      return;
    }
    if (!draft.message.trim()) {
      router.replace('/(flow)/message');
      return;
    }

    let cancelled = false;
    navigatedRef.current = false;

    // Fail-safe: never sit here forever.
    const failSafe = setTimeout(() => {
      if (cancelled) return;
      if (navigatedRef.current) return;
      startedRef.current = false;
      router.replace('/(flow)/message');
    }, 8000);

    (async () => {
      // Ensure we only trigger generation once per screen entry.
      if (startedRef.current) return;
      // Note: don't depend on `generating` here. Including it in the effect deps
      // cancels the async flow mid-flight when it flips true/false.

      startedRef.current = true;
      try {
        const asset = await actions.generateFromDraft();
        if (cancelled) return;
        navigatedRef.current = true;
        router.replace({ pathname: '/(flow)/preview-hub', params: { id: asset.id } });
      } catch {
        // Fall back to the message screen rather than silently looping.
        if (cancelled) return;
        startedRef.current = false;
        router.replace('/(flow)/message');
      }
    })();

    return () => {
      cancelled = true;
      clearTimeout(failSafe);
    };
  }, [actions, draft.assetType, draft.message]);

  return (
    <Screen style={styles.container}>
      <View style={styles.content}>
        <Animated.View style={[styles.dot, { opacity: pulse }]} />
        <Text style={styles.title}>Creating your asset</Text>
        <Text style={styles.subtitle}>A calm moment. Something good is taking shape.</Text>
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
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: tokens.colors.text.primary,
  },
  title: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
  },
  subtitle: {
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
    textAlign: 'center',
    maxWidth: 320,
  },
});

