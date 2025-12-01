'use client';

export function TypingIndicator() {
  return (
    <div className="flex justify-start message-enter">
      <div className="bg-dark-700/50 border border-gray-700/50 rounded-2xl px-5 py-4">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-primary-400 rounded-full typing-dot" />
          <div className="w-2 h-2 bg-primary-400 rounded-full typing-dot" />
          <div className="w-2 h-2 bg-primary-400 rounded-full typing-dot" />
        </div>
      </div>
    </div>
  );
}
