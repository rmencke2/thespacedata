import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';

import { AppStateProvider } from '@/src/state/app-state';

export const unstable_settings = {
  anchor: '(flow)',
};

export default function RootLayout() {
  return (
    <AppStateProvider>
      <Stack>
        <Stack.Screen name="(flow)" options={{ headerShown: false }} />
      </Stack>
      <StatusBar style="auto" />
    </AppStateProvider>
  );
}
