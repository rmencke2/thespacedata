import React from 'react';
import { StyleSheet, View, ViewStyle } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { tokens } from '@/src/design/tokens';

type ScreenProps = {
  children: React.ReactNode;
  style?: ViewStyle;
  safeArea?: boolean;
};

export function Screen({ children, style, safeArea = true }: ScreenProps) {
  const content = <View style={[styles.container, style]}>{children}</View>;

  if (!safeArea) return content;

  return <SafeAreaView style={styles.safeArea}>{content}</SafeAreaView>;
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: tokens.colors.background,
  },
  container: {
    flex: 1,
    backgroundColor: tokens.colors.background,
    padding: tokens.spacing.lg,
  },
});

