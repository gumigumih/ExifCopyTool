module.exports = {
  content: ['./docs/index.html'],
  theme: {
    extend: {
      colors: {
        ink: '#172033',
        mist: '#eff4fb',
        panel: '#ffffff',
        line: '#d4deee',
        muted: '#617086',
        brand: '#245cff',
        'brand-deep': '#183fb7',
        accent: '#0f766e',
        night: '#0f172a'
      },
      fontFamily: {
        sans: ['Space Grotesk', 'IBM Plex Sans JP', 'Segoe UI', 'sans-serif']
      },
      boxShadow: {
        surface: '0 18px 50px rgba(23, 32, 51, 0.08)',
        card: '0 14px 34px rgba(23, 32, 51, 0.06)',
        screenshot: '0 14px 34px rgba(23, 32, 51, 0.08)'
      },
      letterSpacing: {
        eyebrow: '0.14em'
      }
    }
  },
  plugins: []
}
