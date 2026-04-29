import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
interface Props { questions: { text: string; infoGain: number }[] }
export const UoTQuestionList: React.FC<Props> = ({ questions }) => (
  <ScrollView style={styles.container}>
    {questions.map((q, i) => (
      <View key={i} style={styles.item}>
        <Text style={styles.text}>{q.text}</Text>
        <Text style={styles.gain}>IG: {q.infoGain.toFixed(4)}</Text>
      </View>
    ))}
  </ScrollView>
);
const styles = StyleSheet.create({
  container:{padding:10},
  item:{padding:12,marginVertical:4,borderRadius:8,backgroundColor:'#1E293B'},
  text:{color:'#E2E8F0',fontSize:14},
  gain:{color:'#34D399',fontSize:12,marginTop:4,fontWeight:'600'},
});
