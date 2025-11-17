# Bifrost React Dashboard

Modern React dashboard for Bifrost log analysis platform.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/      # React components
│   │   ├── Dashboard.jsx
│   │   ├── AnalysisForm.jsx
│   │   ├── HistoryTable.jsx
│   │   └── MetricsCard.jsx
│   ├── services/        # API services
│   │   └── api.js
│   ├── utils/           # Utilities
│   │   └── helpers.js
│   ├── App.jsx          # Main app component
│   ├── App.css
│   └── index.js         # Entry point
├── package.json
└── README.md
```

## 🎨 Features

- ✅ Real-time log analysis
- ✅ Analysis history with search/filter
- ✅ Metrics visualization (Chart.js)
- ✅ Prompt template editor
- ✅ MLflow experiment tracking
- ✅ Multi-language support (i18n)
- ✅ Dark mode
- ✅ Responsive design

## 🛠️ Tech Stack

- **React 18** - UI framework
- **Axios** - HTTP client
- **Chart.js** - Data visualization
- **React Router** - Routing
- **Tailwind CSS** - Styling
- **React Query** - Data fetching

## 📦 Dependencies

See `package.json` for full list.

## 🔗 API Integration

Backend API: `http://localhost:8000`

See `src/services/api.js` for API endpoints.

## 🎯 Development

```bash
# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

## 📝 License

MIT License - see parent project
