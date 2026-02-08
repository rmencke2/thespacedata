import { Stack } from 'expo-router';
import React from 'react';

export default function FlowLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    >
      <Stack.Screen name="launch" />
      <Stack.Screen name="home" />
      <Stack.Screen name="asset-type" />
      <Stack.Screen name="message" />
      <Stack.Screen
        name="generation"
        options={{
          gestureEnabled: false,
        }}
      />
      <Stack.Screen name="preview-hub" />
      <Stack.Screen name="publish" />
      <Stack.Screen
        name="post-publish"
        options={{
          gestureEnabled: false,
        }}
      />
    </Stack>
  );
}

