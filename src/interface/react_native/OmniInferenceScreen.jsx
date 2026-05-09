// @omni-layer Interface | @omni-lang React Native (JSX) | @omni-batch 17
// @omni-description Mobile inference UI: React Native component for
// on-device NLP with model selection, streaming output, and metrics.

import React, { useState, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet, ActivityIndicator } from 'react-native';

const MODELS = [
  { id: 'sentiment-fr', name: 'French Sentiment', task: 'sentiment', latency: 45 },
  { id: 'ner-multi', name: 'Multilingual NER', task: 'ner', latency: 62 },
  { id: 'classify-en', name: 'English Classifier', task: 'classification', latency: 38 },
];

export default function OmniInferenceScreen() {
  const [input, setInput] = useState('');
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ count: 0, avgLatency: 0 });

  const runInference = useCallback(async () => {
    if (!input.trim()) return;
    setLoading(true);
    const start = Date.now();
    // Simulate on-device inference
    await new Promise(r => setTimeout(r, selectedModel.latency));
    const latency = Date.now() - start;
    const hash = input.split('').reduce((h, c) => ((h << 5) - h + c.charCodeAt(0)) | 0, 0);
    const confidence = (Math.abs(hash) % 100) / 100;
    setResult({ label: ['positive','negative','neutral'][Math.abs(hash) % 3], confidence, latency });
    setStats(prev => ({
      count: prev.count + 1,
      avgLatency: (prev.avgLatency * prev.count + latency) / (prev.count + 1),
    }));
    setLoading(false);
  }, [input, selectedModel]);

  return (
    <ScrollView style={s.container}>
      <Text style={s.title}>🧠 OMNI Inference</Text>
      <View style={s.modelRow}>
        {MODELS.map(m => (
          <TouchableOpacity key={m.id} style={[s.modelChip, selectedModel.id === m.id && s.modelChipActive]}
            onPress={() => setSelectedModel(m)}>
            <Text style={[s.modelChipText, selectedModel.id === m.id && s.modelChipTextActive]}>{m.name}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <TextInput style={s.input} value={input} onChangeText={setInput} placeholder="Enter text..."
        placeholderTextColor="#64748B" multiline />
      <TouchableOpacity style={s.btn} onPress={runInference} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={s.btnText}>Analyze</Text>}
      </TouchableOpacity>
      {result && (
        <View style={s.resultCard}>
          <Text style={s.resultLabel}>Result</Text>
          <Text style={s.resultValue}>{result.label}</Text>
          <View style={s.metricRow}>
            <View style={s.metric}><Text style={s.metricVal}>{(result.confidence*100).toFixed(1)}%</Text><Text style={s.metricLbl}>Confidence</Text></View>
            <View style={s.metric}><Text style={s.metricVal}>{result.latency}ms</Text><Text style={s.metricLbl}>Latency</Text></View>
          </View>
        </View>
      )}
      <View style={s.statsRow}>
        <View style={s.statCard}><Text style={s.statVal}>{stats.count}</Text><Text style={s.statLbl}>Analyses</Text></View>
        <View style={s.statCard}><Text style={s.statVal}>{stats.avgLatency.toFixed(0)}ms</Text><Text style={s.statLbl}>Avg Latency</Text></View>
      </View>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0E17', padding: 20 },
  title: { fontSize: 24, fontWeight: '700', color: '#60A5FA', marginBottom: 16 },
  modelRow: { flexDirection: 'row', gap: 8, marginBottom: 16, flexWrap: 'wrap' },
  modelChip: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20, backgroundColor: '#1E293B' },
  modelChipActive: { backgroundColor: '#60A5FA' },
  modelChipText: { color: '#94A3B8', fontSize: 13, fontWeight: '600' },
  modelChipTextActive: { color: '#FFF' },
  input: { backgroundColor: '#1A1F36', borderRadius: 12, padding: 14, color: '#E2E8F0', fontSize: 15, minHeight: 80, borderWidth: 1, borderColor: '#334155', marginBottom: 12 },
  btn: { backgroundColor: '#60A5FA', borderRadius: 12, padding: 14, alignItems: 'center' },
  btnText: { color: '#FFF', fontSize: 16, fontWeight: '700' },
  resultCard: { backgroundColor: '#1A1F36', borderRadius: 12, padding: 16, marginTop: 16 },
  resultLabel: { color: '#93C5FD', fontSize: 13, fontWeight: '600' },
  resultValue: { color: '#E2E8F0', fontSize: 22, fontWeight: '700', marginTop: 4, textTransform: 'capitalize' },
  metricRow: { flexDirection: 'row', gap: 16, marginTop: 12 },
  metric: { flex: 1 },
  metricVal: { color: '#22D3EE', fontSize: 18, fontWeight: '700' },
  metricLbl: { color: '#64748B', fontSize: 11, marginTop: 2 },
  statsRow: { flexDirection: 'row', gap: 10, marginTop: 16 },
  statCard: { flex: 1, backgroundColor: '#1A1F36', borderRadius: 8, padding: 12 },
  statVal: { color: '#A78BFA', fontSize: 20, fontWeight: '700' },
  statLbl: { color: '#64748B', fontSize: 10, marginTop: 2 },
});
