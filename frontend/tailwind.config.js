/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#FFFFFF',
        secondaryBg: '#F7F8FA',
        primaryText: '#171717',
        secondaryText: '#858585',
        primaryAccent: '#FF665C',
        income: '#3498F3',
        expense: '#FF665C',
        borderSubtle: '#EEEEEE',
        cardBg: '#FFFFFF',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'realbyte': '0 10px 30px -5px rgba(0, 0, 0, 0.05), 0 4px 10px -2px rgba(0, 0, 0, 0.03)',
        'realbyte-hover': '0 20px 40px -10px rgba(0, 0, 0, 0.08), 0 8px 16px -4px rgba(0, 0, 0, 0.04)',
        'phone': '0 25px 60px -15px rgba(0, 0, 0, 0.18), 0 10px 25px -5px rgba(0, 0, 0, 0.1)',
        'floating': '0 30px 70px -10px rgba(255, 102, 92, 0.25)',
      }
    },
  },
  plugins: [],
}
