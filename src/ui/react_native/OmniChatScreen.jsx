// OMNI Interface Layer — React Native Inference Client
// Cross-platform mobile inference SDK for OMNI transformer models.
import React, { useState, useCallback, useRef, useEffect } from 'react';
import { View, Text, TextInput, FlatList, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';

const API_URL = 'http://localhost:8080/api/v1';

const useInference = () => {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ total: 0, avgLatency: 0 });
  const abortRef = useRef(null);

  const infer = useCallback(async (prompt, options = {}) => {
    setLoading(true);
    const start = Date.now();
    abortRef.current = new AbortController();
    try {
      const res = await fetch(`${API_URL}/infer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, max_tokens: options.maxTokens || 256, temperature: options.temperature || 0.7 }),
        signal: abortRef.current.signal,
      });
      const data = await res.json();
      const latency = Date.now() - start;
      setStats(s => ({ total: s.total + 1, avgLatency: (s.avgLatency * s.total + latency) / (s.total + 1) }));
      return { ...data, latencyMs: latency };
    } catch (e) {
      if (e.name !== 'AbortError') throw e;
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const cancel = useCallback(() => { abortRef.current?.abort(); }, []);
  return { infer, cancel, loading, stats };
};

const OmniChatScreen = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const { infer, loading } = useInference();

  const send = async () => {
    if (!input.trim() || loading) return;
    const userMsg = { role: 'user', text: input, id: Date.now().toString() };
    setMessages(m => [...m, userMsg]);
    setInput('');
    const result = await infer(input);
    if (result) {
      setMessages(m => [...m, { role: 'assistant', text: result.generated_text || 'No response', id: `${Date.now()}` }]);
    }
  };

  const renderMessage = ({ item }) => (
    <View style={[styles.bubble, item.role === 'user' ? styles.userBubble : styles.aiBubble]}>
      <Text style={styles.bubbleText}>{item.text}</Text>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.header}>⚡ OMNI Chat</Text>
      <FlatList data={messages} renderItem={renderMessage} keyExtractor={i => i.id} style={styles.list} />
      {loading && <ActivityIndicator size="small" color="#6366f1" />}
      <View style={styles.inputRow}>
        <TextInput style={styles.input} value={input} onChangeText={setInput} placeholder="Ask anything..." placeholderTextColor="#666" />
        <TouchableOpacity style={styles.sendBtn} onPress={send} disabled={loading}>
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0e1a', paddingTop: 50 },
  header: { fontSize: 24, fontWeight: 'bold', color: '#6366f1', textAlign: 'center', marginBottom: 16 },
  list: { flex: 1, paddingHorizontal: 16 },
  bubble: { padding: 12, borderRadius: 12, marginBottom: 8, maxWidth: '80%' },
  userBubble: { backgroundColor: '#6366f1', alignSelf: 'flex-end' },
  aiBubble: { backgroundColor: '#1e2740', alignSelf: 'flex-start' },
  bubbleText: { color: '#e2e8f0', fontSize: 15 },
  inputRow: { flexDirection: 'row', padding: 12, borderTopWidth: 1, borderTopColor: '#1e2740' },
  input: { flex: 1, backgroundColor: '#131829', color: '#e2e8f0', borderRadius: 8, paddingHorizontal: 16, fontSize: 16, marginRight: 8 },
  sendBtn: { backgroundColor: '#6366f1', paddingHorizontal: 20, paddingVertical: 12, borderRadius: 8, justifyContent: 'center' },
  sendText: { color: '#fff', fontWeight: '600' },
});

export default OmniChatScreen;
