import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
interface Props { modelName: string; perplexity: number; flops: number; }
export const BlaGPTBenchCard: React.FC<Props> = ({ modelName, perplexity, flops }) => (
  <View style={styles.card}>
    <Text style={styles.title}>{modelName}</Text>
    <Text style={styles.metric}>PPL: {perplexity.toFixed(2)}</Text>
    <Text style={styles.sub}>FLOPs: {(flops / 1e9).toFixed(1)}G</Text>
  </View>
);
const styles = StyleSheet.create({
  card:{padding:14,borderRadius:10,marginVertical:6,backgroundColor:'#1E1B4B'},
  title:{color:'#E0E7FF',fontSize:16,fontWeight:'700'},
  metric:{color:'#A78BFA',fontSize:14,fontWeight:'600',marginTop:4},
  sub:{color:'#6B7280',fontSize:12,marginTop:2},
});
