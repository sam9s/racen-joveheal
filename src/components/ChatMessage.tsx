'use client';

import { useState } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: Date;
  feedbackGiven?: 'up' | 'down' | null;
}

interface ChatMessageProps {
  message: Message;
  onFeedback: (messageId: string, feedback: 'up' | 'down', comment?: string) => void;
}

export function ChatMessage({ message, onFeedback }: ChatMessageProps) {
  const [showFeedbackInput, setShowFeedbackInput] = useState(false);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [pendingFeedback, setPendingFeedback] = useState<'up' | 'down' | null>(null);

  const isUser = message.role === 'user';

  const handleFeedbackClick = (feedback: 'up' | 'down') => {
    if (message.feedbackGiven) return;
    
    if (feedback === 'down') {
      setPendingFeedback(feedback);
      setShowFeedbackInput(true);
    } else {
      onFeedback(message.id, feedback);
    }
  };

  const submitFeedback = () => {
    if (pendingFeedback) {
      onFeedback(message.id, pendingFeedback, feedbackComment);
      setShowFeedbackInput(false);
      setFeedbackComment('');
      setPendingFeedback(null);
    }
  };

  return (
    <div
      className={`message-enter flex ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-3 transition-colors duration-300 ${
          isUser
            ? 'bg-primary-500/20 border border-primary-500/30 text-theme'
            : 'bg-theme-card border border-primary-500/10 text-theme'
        }`}
      >
        <div className="whitespace-pre-wrap text-sm md:text-base leading-relaxed">
          {message.content}
        </div>
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-primary-500/10">
            <p className="text-xs text-theme-muted mb-1">Sources:</p>
            <div className="flex flex-wrap gap-1">
              {message.sources.map((source, index) => (
                <span
                  key={index}
                  className="text-xs px-2 py-0.5 rounded bg-primary-500/10 text-primary-500"
                >
                  {source}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {!isUser && (
          <div className="mt-3 pt-3 border-t border-primary-500/10">
            <div className="flex items-center gap-2">
              <span className="text-xs text-theme-muted">Was this helpful?</span>
              <button
                onClick={() => handleFeedbackClick('up')}
                disabled={!!message.feedbackGiven}
                className={`p-1.5 rounded transition-colors ${
                  message.feedbackGiven === 'up'
                    ? 'text-green-500 bg-green-500/10'
                    : 'text-theme-muted hover:text-green-500 hover:bg-green-500/10'
                } disabled:cursor-not-allowed`}
                aria-label="Thumbs up"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
              </button>
              <button
                onClick={() => handleFeedbackClick('down')}
                disabled={!!message.feedbackGiven}
                className={`p-1.5 rounded transition-colors ${
                  message.feedbackGiven === 'down'
                    ? 'text-red-500 bg-red-500/10'
                    : 'text-theme-muted hover:text-red-500 hover:bg-red-500/10'
                } disabled:cursor-not-allowed`}
                aria-label="Thumbs down"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5" />
                </svg>
              </button>
            </div>
            
            {showFeedbackInput && (
              <div className="mt-3 space-y-2">
                <textarea
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  placeholder="What could be improved? (optional)"
                  className="w-full px-3 py-2 text-sm bg-theme-surface border border-primary-500/20 rounded-lg text-theme placeholder-gray-500 focus:outline-none focus:border-primary-500/50 resize-none transition-colors duration-300"
                  rows={2}
                />
                <div className="flex gap-2">
                  <button
                    onClick={submitFeedback}
                    className="px-3 py-1 text-xs bg-primary-500/20 hover:bg-primary-500/30 text-primary-500 rounded transition-colors"
                  >
                    Submit
                  </button>
                  <button
                    onClick={() => {
                      setShowFeedbackInput(false);
                      setFeedbackComment('');
                      setPendingFeedback(null);
                    }}
                    className="px-3 py-1 text-xs bg-theme-surface hover:bg-primary-500/10 text-theme-muted rounded transition-colors border border-primary-500/10"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
