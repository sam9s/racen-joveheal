'use client';

import { useTheme } from './ThemeProvider';
import Image from 'next/image';

interface HeaderProps {
  onReset: () => void;
}

export function Header({ onReset }: HeaderProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-dark-900/80 dark:bg-dark-900/80 border-b border-primary-500/10">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            <div className="flex flex-col items-center">
              <h1 className="text-3xl md:text-4xl font-light tracking-[0.5em] text-white glow-text">
                R.A.C.E.N
              </h1>
              <p className="text-[10px] md:text-xs tracking-[0.3em] text-primary-400/80 mt-1 uppercase">
                Real Time Advisor for Coaching, Education & Navigation
              </p>
            </div>
            <div className="hidden md:block">
              <Image
                src="/logo.png"
                alt="R.A.C.E.N Logo"
                width={50}
                height={50}
                className="opacity-90"
              />
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-dark-700/50 hover:bg-dark-600/50 transition-colors border border-primary-500/20"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <svg
                  className="w-5 h-5 text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                  />
                </svg>
              ) : (
                <svg
                  className="w-5 h-5 text-primary-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                  />
                </svg>
              )}
            </button>
            
            <button
              onClick={onReset}
              className="px-3 py-2 text-sm rounded-lg bg-dark-700/50 hover:bg-dark-600/50 transition-colors border border-primary-500/20 text-gray-300 hover:text-white"
            >
              New Chat
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
