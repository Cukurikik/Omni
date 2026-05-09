import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, Button, ScrollView, StyleSheet } from 'react-native';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  expertRouting?: string[]; // E.g., ["NLP Expert", "Math Expert"]
}

/**
 * BangumiMoEClient - React Native component for a mobile anime/community client.
 * Connects to the OMNI MoE backend to generate context-aware AI replies.
 * Inspired by czy0729/Bangumi UI concepts.
 */
export const BangumiMoEClient: React.FC = () => {
  const [inputText, setInputText] = useState('');
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMsg: Message = { role: 'user', content: inputText };
    setChatHistory((prev) => [...prev, userMsg]);
    setInputText('');
    setIsGenerating(true);

    try {
      // Mock API call to OMNI Server (e.g. omni_sglang_router)
      const response = await fetch('http://omni-server:8082/v1/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userMsg.content, max_tokens: 200 })
      });

      if (!response.ok) throw new Error('OMNI Network Error');
      
      const data = await response.json();
      
      const botMsg: Message = { 
        role: 'assistant', 
        content: data.text || "This is a production-simulated response.",
        expertRouting: data.experts_used || ["Bangumi Lore Expert", "Translation Expert"]
      };
      
      setChatHistory((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Failed to connect to OMNI MoE Backend", error);
      const errorMsg: Message = { role: 'assistant', content: "[Error: OMNI Connection Failed]" };
      setChatHistory((prev) => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>OMNI ACG Assistant (MoE Powered)</Text>
      <ScrollView style={styles.chatArea}>
        {chatHistory.map((msg, idx) => (
          <View key={idx} style={msg.role === 'user' ? styles.userBubble : styles.botBubble}>
            <Text style={styles.msgText}>{msg.content}</Text>
            {msg.expertRouting && (
              <Text style={styles.expertInfo}>⚡ Routed via: {msg.expertRouting.join(', ')}</Text>
            )}
          </View>
        ))}
      </ScrollView>
      <View style={styles.inputArea}>
        <TextInput 
          style={styles.input} 
          value={inputText} 
          onChangeText={setInputText} 
          placeholder="Ask about anime lore..." 
          placeholderTextColor="#888"
        />
        <Button title="Send" onPress={handleSend} disabled={isGenerating} color="#FF69B4" />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#121212', paddingTop: 40 },
  header: { fontSize: 20, color: '#FF69B4', textAlign: 'center', fontWeight: 'bold', marginBottom: 10 },
  chatArea: { flex: 1, padding: 10 },
  userBubble: { alignSelf: 'flex-end', backgroundColor: '#333', padding: 12, borderRadius: 8, marginBottom: 10, maxWidth: '80%' },
  botBubble: { alignSelf: 'flex-start', backgroundColor: '#1E1E2E', padding: 12, borderRadius: 8, marginBottom: 10, maxWidth: '80%', borderWidth: 1, borderColor: '#444' },
  msgText: { color: '#E0E0E0', fontSize: 16 },
  expertInfo: { color: '#FF69B4', fontSize: 10, marginTop: 5, fontStyle: 'italic' },
  inputArea: { flexDirection: 'row', padding: 10, borderTopWidth: 1, borderTopColor: '#333', backgroundColor: '#000' },
  input: { flex: 1, backgroundColor: '#222', color: '#FFF', borderRadius: 20, paddingHorizontal: 15, marginRight: 10 }
});

export default BangumiMoEClient;
