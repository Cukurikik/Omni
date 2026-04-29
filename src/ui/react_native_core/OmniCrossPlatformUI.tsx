import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export type UiResult<T> = 
  | { success: true; component: T }
  | { success: false; error: string };

interface OmniProps {
  dataStream: ReadonlyArray<number>;
  theme: 'dark' | 'light';
}

/**
 * Omni Cross-Platform UI Component (React Native)
 * Strictly typed, zero-mock UI logic.
 */
export const OmniCrossPlatformUI: React.FC<OmniProps> = ({ dataStream, theme }) => {
  if (dataStream.length === 0) {
    return <Text style={styles.errorText}>Error: Data stream cannot be empty</Text>;
  }

  const containerStyle = theme === 'dark' ? styles.darkContainer : styles.lightContainer;
  const processedHash = dataStream.reduce((acc, val) => acc + val, 0).toString(16);

  return (
    <View style={containerStyle}>
      <Text>Omni Tensor UI Bridge</Text>
      <Text>Data Hash: {processedHash}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  darkContainer: { backgroundColor: '#000000', padding: 16 },
  lightContainer: { backgroundColor: '#FFFFFF', padding: 16 },
  errorText: { color: '#FF0000', fontWeight: 'bold' }
});
