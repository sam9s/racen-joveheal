'use client';

import { useState, useRef, useEffect } from 'react';
import { useSession } from 'next-auth/react';
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
  const { data: session, status } = useSession();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (status === 'loading') {
      return;
    }
    if (status === 'authenticated' && session?.user?.email) {
      setSessionId(`user_${session.user.email}`);
    } else if (status === 'unauthenticated') {
      setSessionId(`guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    }
  }, [status, session]);

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
          user: session?.user ? {
            email: session.user.email,
            name: session.user.name,
            image: session.user.image,
          } : null,
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
      if (status === 'authenticated' && session?.user?.email) {
        setSessionId(`user_${session.user.email}_${Date.now()}`);
      } else {
        setSessionId(`guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
      }
    } catch (error) {
      console.error('Error resetting conversation:', error);
    }
  };

  const getUserFirstName = () => {
    if (status === 'authenticated' && session?.user?.name) {
      return session.user.name.split(' ')[0];
    }
    return null;
  };

  return (
    <main className="flex min-h-screen flex-col bg-theme transition-colors duration-300">
      <Header onReset={resetConversation} />
      
      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full px-4">
        <div className="flex-1 overflow-y-auto py-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex-1 flex items-center justify-center min-h-[60vh]">
              <div className="text-center max-w-md">
                <p className="text-xl font-light text-theme-muted">
                  {getUserFirstName() ? `Hi ${getUserFirstName()}, I'm RACEN` : "Hi, I'm RACEN"}
                </p>
                <p className="text-sm mt-2 text-theme-muted opacity-80">
                  Your real-time guide for healing and coaching at JoveHeal
                </p>
                <div className="mt-6 text-left text-sm text-theme-muted opacity-70 space-y-1">
                  <p className="font-medium opacity-90 mb-2">I can help you explore:</p>
                  <p>• Program details (Balance Mastery+, Elevate 360)</p>
                  <p>• Healing philosophy and approach</p>
                  <p>• Membership and pricing info</p>
                  <p>• How to get started</p>
                </div>
                <p className="text-sm mt-6 text-theme-muted opacity-60">
                  What brings you here today?
                </p>
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
        
        <div className="sticky bottom-0 pb-6 pt-4">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </main>
  );
}
