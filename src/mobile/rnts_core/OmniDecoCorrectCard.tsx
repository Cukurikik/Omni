// Omni DeCo Correction Card (React Native)
// Mobile Layer: Visual hallucination correction display.
// Ref: zjunlp/Deco — ICLR 2025
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
interface Props { correctionRate: number; confidence: number; }
export const DecoCard: React.FC<Props> = ({ correctionRate, confidence }) => (
  <View style={[styles.card, correctionRate > 0.3 ? styles.alert : styles.safe]}>
    <Text style={styles.title}>{correctionRate > 0.3 ? '🔧 Corrections Active' : '✅ Clean Output'}</Text>
    <Text style={styles.stat}>Rate: {(correctionRate * 100).toFixed(1)}% | Conf: {(confidence * 100).toFixed(1)}%</Text>
  </View>
);
const styles = StyleSheet.create({
  card: { padding: 14, borderRadius: 10, marginVertical: 6 },
  alert: { backgroundColor: '#4A2020' }, safe: { backgroundColor: '#1A3A1A' },
  title: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  stat: { color: '#9CA3AF', fontSize: 12, marginTop: 4 },
});
