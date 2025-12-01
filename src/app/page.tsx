'use client';

import { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { Header } from '@/components/Header';
import { TypingIndicator } from '@/components/TypingIndicator';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
  feedbackGiven?: 'up' | 'down' | null;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content.trim(),
          session_id: sessionId,
          conversation_history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg_${Date.now()}_assistant`,
        role: 'assistant',
        content: data.response || 'I apologize, but I encountered an issue. Please try again.',
        sources: data.sources || [],
        timestamp: new Date(),
        feedbackGiven: null,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: `msg_${Date.now()}_error`,
        role: 'assistant',
        content: 'I apologize, but I encountered a connection issue. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = async (messageId: string, feedback: 'up' | 'down', comment?: string) => {
    try {
      await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message_id: messageId,
          feedback,
          comment,
        }),
      });

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, feedbackGiven: feedback } : msg
        )
      );
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const resetConversation = async () => {
    try {
      await fetch('/api/chat/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId }),
      });
      setMessages([]);
      setSessionId(`session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    } catch (error) {
      console.error('Error resetting conversation:', error);
    }
  };

  return (
    <main className="flex min-h-screen flex-col bg-dark-900 dark:bg-dark-900 light:bg-gray-50">
      <Header onReset={resetConversation} />
      
      <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-4">
        <div className="flex-1 overflow-y-auto py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex-1 flex items-center justify-center min-h-[50vh]">
              <div className="text-center text-gray-500 dark:text-gray-400">
                <p className="text-lg">Welcome to R.A.C.E.N</p>
                <p className="text-sm mt-2">Ask me anything about JoveHeal's services and programs</p>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onFeedback={handleFeedback}
            />
          ))}
          
          {isLoading && <TypingIndicator />}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="sticky bottom-0 pb-6 pt-2 bg-gradient-to-t from-dark-900 via-dark-900 to-transparent dark:from-dark-900 dark:via-dark-900">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </main>
  );
}
