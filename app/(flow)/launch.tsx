import React, { useEffect, useRef } from 'react';
import { Animated, StyleSheet, Text } from 'react-native';
import { router } from 'expo-router';
import { Screen } from '@/src/components/Screen';
import { tokens } from '@/src/design/tokens';

export default function LaunchRoute() {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.timing(opacity, {
      toValue: 1,
      duration: 550,
      useNativeDriver: true,
    }).start();

    const t = setTimeout(() => {
      router.replace('/(flow)/home');
    }, 2100);

    return () => clearTimeout(t);
  }, [opacity]);

  return (
    <Screen style={styles.container}>
      <Animated.View style={[styles.content, { opacity }]}>
        <Text style={styles.brand}>Influzer</Text>
        <Text style={styles.tagline}>
          Create, preview, and publish brand assets that look professional — in under 60 seconds.
        </Text>
      </Animated.View>
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
  brand: {
    fontSize: tokens.typography.fontSize.xxl,
    fontWeight: tokens.typography.fontWeight.bold,
    color: tokens.colors.text.primary,
  },
  tagline: {
    maxWidth: 320,
    textAlign: 'center',
    fontSize: tokens.typography.fontSize.md,
    color: tokens.colors.text.secondary,
  },
});

