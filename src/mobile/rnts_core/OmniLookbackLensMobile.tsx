// Omni Lookback Lens Mobile (React Native TSX)
// Mobile Layer: Hallucination confidence display.
// Ref: voidism/Lookback-Lens — EMNLP 2024
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
interface Props { lookbackRatio: number; isHallucination: boolean; }
export const HallucinationCard: React.FC<Props> = ({ lookbackRatio, isHallucination }) => (
  <View style={[styles.card, isHallucination ? styles.warn : styles.safe]}>
    <Text style={styles.label}>{isHallucination ? '⚠️ Hallucination' : '✅ Grounded'}</Text>
    <Text style={styles.ratio}>Lookback: {(lookbackRatio * 100).toFixed(1)}%</Text>
  </View>
);
const styles = StyleSheet.create({
  card: { padding: 12, borderRadius: 8, marginBottom: 8 },
  warn: { backgroundColor: '#3D1F1F' }, safe: { backgroundColor: '#1F3D1F' },
  label: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  ratio: { color: '#8B949E', fontSize: 13, marginTop: 4 },
});
