import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f7ff',
          100: '#b3e5fc',
          200: '#81d4fa',
          300: '#4fc3f7',
          400: '#29b6f6',
          500: '#03a9f4',
          600: '#039be5',
          700: '#0288d1',
          800: '#0277bd',
          900: '#01579b',
        },
        dark: {
          50: '#f5f5f5',
          100: '#e0e0e0',
          200: '#9e9e9e',
          300: '#616161',
          400: '#424242',
          500: '#212121',
          600: '#1a1a1a',
          700: '#141414',
          800: '#0d0d0d',
          900: '#080808',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(3, 169, 244, 0.3)',
        'glow-lg': '0 0 40px rgba(3, 169, 244, 0.4)',
      },
    },
  },
  plugins: [],
};
export default config;
