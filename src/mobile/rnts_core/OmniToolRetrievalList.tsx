import React from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
interface Tool { name: string; description: string; score: number; }
interface Props { tools: Tool[]; query: string; }
export const ToolRetrievalList: React.FC<Props> = ({ tools, query }) => (
  <View style={s.container}>
    <Text style={s.query}>Query: {query}</Text>
    <FlatList data={tools} keyExtractor={(t) => t.name}
      renderItem={({ item }) => (
        <View style={s.item}>
          <Text style={s.name}>{item.name}</Text>
          <Text style={s.desc}>{item.description}</Text>
          <Text style={s.score}>Relevance: {(item.score * 100).toFixed(1)}%</Text>
        </View>
      )} />
  </View>
);
const s = StyleSheet.create({
  container:{padding:12}, query:{color:'#94A3B8',fontSize:13,marginBottom:8},
  item:{padding:10,marginVertical:4,borderRadius:8,backgroundColor:'#1E293B'},
  name:{color:'#F1F5F9',fontSize:15,fontWeight:'700'},
  desc:{color:'#94A3B8',fontSize:12,marginTop:2},
  score:{color:'#34D399',fontSize:12,marginTop:4,fontWeight:'600'},
});
