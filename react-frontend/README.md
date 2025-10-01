# Hermes Trading Companion - React Frontend

A modern React TypeScript frontend for the Hermes trading companion, featuring Firebase authentication and real-time trading data.

## Features

- ✅ **Authentication**: Firebase Auth with email/password
- ✅ **Real-time Data**: Connect to FastAPI backend for market data
- ✅ **AI Predictions**: Generate trading predictions with confidence scores
- ✅ **Responsive Design**: Mobile-first UI with Tailwind CSS
- ✅ **Error Handling**: Comprehensive error boundaries and loading states
- ✅ **Type Safety**: Full TypeScript implementation
- ✅ **Mock Mode**: Development mode with sample data

## Quick Start

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase and API configurations
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

4. **Start FastAPI Backend** (Required)
   ```bash
   cd ../backend
   source .venv-311-test/bin/activate
   python run_app.py
   ```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_BASE_URL` | FastAPI backend URL | Yes |
| `VITE_FIREBASE_API_KEY` | Firebase API key | Yes* |
| `VITE_FIREBASE_AUTH_DOMAIN` | Firebase auth domain | Yes* |
| `VITE_FIREBASE_PROJECT_ID` | Firebase project ID | Yes* |
| `VITE_MOCK_MODE` | Enable mock mode for development | No |

*Required for production, optional in mock mode

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── components/        # Reusable UI components
├── pages/            # Page components
├── contexts/         # React contexts (Auth, etc.)
├── services/         # API services and utilities
├── config/          # Configuration and environment
└── styles/          # Global styles and Tailwind
```

## Authentication Flow

1. **Public Routes**: `/login`, `/register`
2. **Protected Routes**: `/dashboard` (requires authentication)
3. **Auto-redirect**: Unauthenticated users → Login
4. **Mock Mode**: Skip Firebase, use local auth simulation

## API Integration

The app connects to your FastAPI backend at `VITE_API_BASE_URL`:

- **Health Check**: `GET /health`
- **Market Data**: `GET /market`
- **Predictions**: `POST /predictions/generate`
- **News**: `GET /news`

## Production Deployment

1. **Build the app**
   ```bash
   npm run build
   ```

2. **Configure environment**
   - Set production Firebase config
   - Set production API URL
   - Disable mock mode

3. **Deploy** using your preferred hosting:
   - Vercel, Netlify, or traditional hosting
   - Ensure HTTPS for Firebase Auth

## Mock Mode

For development without Firebase:

```bash
# .env
VITE_MOCK_MODE=true
```

This enables:
- Local authentication simulation
- Sample trading data
- Offline development

## Security Notes

- Environment variables prefixed with `VITE_` are exposed to the client
- Never put sensitive server-side keys in frontend env
- Use Firebase security rules for database protection
- API calls include automatic token handling

## Troubleshooting

**"Module not found" errors**: Ensure all dependencies are installed
**Firefox errors**: Check your Firebase configuration
**API connection issues**: Verify FastAPI backend is running
**Build errors**: Check TypeScript types and imports
