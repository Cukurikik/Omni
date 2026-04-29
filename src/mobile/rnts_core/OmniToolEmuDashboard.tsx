// Omni ToolEmu Dashboard (React Native TS)
// Mobile Layer: Deterministic rendering logic for tool risk analysis metrics.

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ToolRiskProps {
  toolName: string;
  riskScore: number;
}

export const ToolEmuRiskCard: React.FC<ToolRiskProps> = ({ toolName, riskScore }) => {
  const isSafe = riskScore < 0.8;
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{toolName}</Text>
      <Text style={[styles.status, { color: isSafe ? '#2EA043' : '#F85149' }]}>
        {isSafe ? 'VERIFIED_SAFE' : 'RISK_THRESHOLD_EXCEEDED'}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 16, backgroundColor: '#161B22', borderRadius: 8 },
  title: { color: '#C9D1D9', fontSize: 18, fontWeight: 'bold' },
  status: { marginTop: 8, fontSize: 14 }
});
