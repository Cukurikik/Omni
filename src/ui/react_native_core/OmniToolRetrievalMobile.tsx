import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export type ToolEvalResult = 
  | { success: true; metric: number }
  | { success: false; error: string };

interface ToolProps {
  toolName: string;
  recallScore: number;
}

/**
 * Omni Tool Retrieval Mobile (React Native)
 * Strictly typed, zero-mock UI logic.
 */
export const OmniToolRetrievalMobile: React.FC<ToolProps> = ({ toolName, recallScore }) => {
  if (!toolName) {
    return <Text style={styles.errorText}>Error: Tool name cannot be empty</Text>;
  }

  const normalizedScore = Math.max(0, Math.min(1, recallScore));

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Omni Tool Retrieval Evaluation</Text>
      <Text style={styles.text}>Target: {toolName}</Text>
      <Text style={styles.text}>Recall@K: {(normalizedScore * 100).toFixed(2)}%</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { backgroundColor: '#000000', padding: 16, flex: 1 },
  text: { color: '#C9D1D9', fontSize: 16, marginBottom: 8 },
  errorText: { color: '#FF0000', fontWeight: 'bold' }
});
