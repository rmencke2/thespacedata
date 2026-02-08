import React from 'react';
import { Redirect } from 'expo-router';

export default function IndexRoute() {
  // MVP: linear guided flow only (no tabs)
  return <Redirect href="/(flow)/launch" />;
}

