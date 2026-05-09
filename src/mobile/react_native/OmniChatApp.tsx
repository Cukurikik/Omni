// OMNI Framework - Chat App for LLMs (React Native)
// Mobile interface for interacting with the Omni LLM Router

import React, { useState } from 'react';
import { View, Text, TextInput, Button, FlatList, StyleSheet, SafeAreaView } from 'react-native';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'omni';
}

export default function OmniChatApp() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');

  const sendMessage = () => {
    if (!inputText.trim()) return;

    const newUserMsg: Message = { id: Date.now().toString(), text: inputText, sender: 'user' };
    setMessages(prev => [...prev, newUserMsg]);
    setInputText('');

    // Simulate network delay and LLM response
    setTimeout(() => {
      const newOmniMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        text: "I am OMNI. I have received your message.", 
        sender: 'omni' 
      };
      setMessages(prev => [...prev, newOmniMsg]);
    }, 1000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <View style={[styles.messageBubble, item.sender === 'user' ? styles.userBubble : styles.omniBubble]}>
            <Text style={styles.messageText}>{item.text}</Text>
          </View>
        )}
      />
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Ask OMNI..."
        />
        <Button title="Send" onPress={sendMessage} color="#673ab7" />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  messageBubble: { padding: 12, marginVertical: 4, marginHorizontal: 16, borderRadius: 16, maxWidth: '80%' },
  userBubble: { backgroundColor: '#673ab7', alignSelf: 'flex-end' },
  omniBubble: { backgroundColor: '#e0e0e0', alignSelf: 'flex-start' },
  messageText: { color: '#fff' }, // Note: omni text needs dark color in reality
  inputContainer: { flexDirection: 'row', padding: 8, backgroundColor: '#fff' },
  input: { flex: 1, borderWidth: 1, borderColor: '#ccc', borderRadius: 20, paddingHorizontal: 16, marginRight: 8 }
});
