import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
// Omni GraphTranslator Mobile — Graph-to-LLM alignment display
// Ref: alibaba/GraphTranslator
interface Props { nodeCount: number; edgeCount: number; alignmentScore: number; }
export const GraphTranslatorCard: React.FC<Props> = ({ nodeCount, edgeCount, alignmentScore }) => (
  <View style={styles.card}>
    <Text style={styles.title}>🔗 Graph Alignment</Text>
    <Text style={styles.stat}>Nodes: {nodeCount} | Edges: {edgeCount}</Text>
    <Text style={[styles.score, alignmentScore > 0.7 ? styles.good : styles.warn]}>
      Score: {(alignmentScore * 100).toFixed(1)}%
    </Text>
  </View>
);
const styles = StyleSheet.create({
  card:{padding:14,borderRadius:10,marginVertical:6,backgroundColor:'#1A1A2E'},
  title:{color:'#FFF',fontSize:16,fontWeight:'700'}, stat:{color:'#9CA3AF',fontSize:12,marginTop:4},
  score:{fontSize:14,fontWeight:'600',marginTop:6}, good:{color:'#4ADE80'}, warn:{color:'#FBBF24'},
});
