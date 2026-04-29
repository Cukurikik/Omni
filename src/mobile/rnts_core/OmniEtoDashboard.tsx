// Omni ETO Mobile Dashboard (React Native TS)
// Mobile Layer: Trajectory exploration results rendering.
// Ref: Yifan-Song793/ETO

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface TrajectoryProps { rank: number; reward: number; steps: number; }

export const TrajectoryCard: React.FC<TrajectoryProps> = ({ rank, reward, steps }) => (
  <View style={styles.card}>
    <Text style={styles.rank}>#{rank}</Text>
    <Text style={styles.metric}>Return: {reward.toFixed(4)}</Text>
    <Text style={styles.metric}>Steps: {steps}</Text>
  </View>
);

const styles = StyleSheet.create({
  card: { padding: 12, backgroundColor: '#161B22', borderRadius: 8, marginBottom: 8 },
  rank: { color: '#58A6FF', fontSize: 20, fontWeight: 'bold' },
  metric: { color: '#8B949E', fontSize: 14, marginTop: 4 },
});
