/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBase: '#0d1117',
        darkCard: '#161b22',
        darkBorder: '#30363d',
        darkText: '#c9d1d9',
        darkMuted: '#8b949e',
        brandBlue: '#1f6feb',
        brandCyan: '#38bdf8',
        brandGreen: '#238636',
        brandYellow: '#d29922',
        brandRed: '#da3633'
      }
    },
  },
  plugins: [],
}

