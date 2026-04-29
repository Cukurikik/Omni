import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
interface Props { modelName: string; halIndex: number; adherence: number; }
export const HalIndexCard: React.FC<Props> = ({ modelName, halIndex, adherence }) => (
  <View style={styles.card}>
    <Text style={styles.title}>{modelName}</Text>
    <Text style={[styles.score, halIndex < 0.3 ? styles.good : styles.warn]}>
      Hallucination: {(halIndex * 100).toFixed(1)}%
    </Text>
    <Text style={styles.sub}>Adherence: {(adherence * 100).toFixed(1)}%</Text>
  </View>
);
const styles = StyleSheet.create({
  card:{padding:14,borderRadius:10,marginVertical:6,backgroundColor:'#0F172A'},
  title:{color:'#FFF',fontSize:16,fontWeight:'700'},
  score:{fontSize:14,fontWeight:'600',marginTop:6}, sub:{color:'#9CA3AF',fontSize:12,marginTop:4},
  good:{color:'#4ADE80'}, warn:{color:'#EF4444'},
});
