import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api, mockData } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import AITradingAgent from '../components/AITradingAgent';
import config from '../config';
import toast from 'react-hot-toast';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
}

interface Prediction {
  symbol: string;
  signal: string;
  confidence: number;
  entry_price: number;
  target_price: number;
  stop_loss: number;
  reasoning: string[];
  timestamp: string;
  recommendation: string;
}

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingPrediction, setGeneratingPrediction] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      if (config.mockMode) {
        // Use mock data for development
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMarketData(mockData.marketData);
        setPrediction(mockData.prediction);
      } else {
        // Load real data from API
        const [marketResponse] = await Promise.all([
          api.market.getMarketData('BTCUSDT'),
        ]);
        
        setMarketData(marketResponse.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load market data');
      
      // Fallback to mock data
      setMarketData(mockData.marketData);
      setPrediction(mockData.prediction);
    } finally {
      setLoading(false);
    }
  };

  const generatePrediction = async () => {
    try {
      setGeneratingPrediction(true);
      
      if (config.mockMode) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        setPrediction(mockData.prediction);
        toast.success('New prediction generated!');
      } else {
        const response = await api.predictions.generate();
        setPrediction(response.data);
        toast.success('New prediction generated!');
      }
    } catch (error) {
      console.error('Failed to generate prediction:', error);
      toast.error('Failed to generate prediction');
    } finally {
      setGeneratingPrediction(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" message="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Hermes Dashboard</h1>
              <p className="text-sm text-gray-500">Welcome back, {user?.email}</p>
            </div>
            <div className="hidden sm:block">
              <a href="/dev-control" className="text-sm text-indigo-600 hover:underline">Dev Control</a>
            </div>
            <button
              onClick={handleLogout}
              className="btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Market Data Card */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Market Overview</h2>
            {marketData && (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Symbol</span>
                  <span className="text-lg font-bold text-gray-900">{marketData.symbol}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Price</span>
                  <span className="text-lg font-bold text-gray-900">
                    ${marketData.price.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Change</span>
                  <span className={`text-lg font-bold ${
                    marketData.change >= 0 ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {marketData.change >= 0 ? '+' : ''}
                    ${marketData.change.toLocaleString()} ({marketData.changePercent.toFixed(2)}%)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Volume</span>
                  <span className="text-lg font-bold text-gray-900">
                    {marketData.volume.toLocaleString()}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Traditional AI Prediction Card */}
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Basic AI Prediction</h2>
              <button
                onClick={generatePrediction}
                disabled={generatingPrediction}
                className="btn-primary text-sm"
              >
                {generatingPrediction ? <LoadingSpinner size="sm" message="" /> : 'Generate New'}
              </button>
            </div>
            
            {prediction ? (
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Signal</span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    prediction.signal === 'BUY' 
                      ? 'bg-success-100 text-success-800'
                      : prediction.signal === 'SELL'
                      ? 'bg-danger-100 text-danger-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {prediction.signal}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Confidence</span>
                  <span className="text-lg font-bold text-gray-900">{prediction.confidence}%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Entry Price</span>
                  <span className="text-lg font-bold text-gray-900">
                    ${prediction.entry_price.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Target</span>
                  <span className="text-lg font-bold text-success-600">
                    ${prediction.target_price.toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-500">Stop Loss</span>
                  <span className="text-lg font-bold text-danger-600">
                    ${prediction.stop_loss.toLocaleString()}
                  </span>
                </div>
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700">{prediction.recommendation}</p>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No prediction available</p>
                <button
                  onClick={generatePrediction}
                  className="mt-2 btn-primary"
                >
                  Generate Prediction
                </button>
              </div>
            )}
          </div>
        </div>

        {/* AI Trading Agent Section */}
        <div className="mt-6">
          <AITradingAgent 
            symbol={marketData?.symbol || 'AAPL'}
            onPredictionUpdate={(aiPrediction) => {
              console.log('AI Prediction updated:', aiPrediction);
              // Optionally update state or show notification
              toast.success(`AI analysis updated: ${aiPrediction.signal} signal with ${aiPrediction.confidence}% confidence`);
            }}
          />
        </div>

        {/* API Status */}
        <div className="mt-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  config.mockMode ? 'bg-yellow-400' : 'bg-success-400'
                }`}></div>
                <span className="text-sm text-gray-600">
                  {config.mockMode ? 'Demo Mode' : 'Live Trading'}
                </span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-success-400 mr-2"></div>
                <span className="text-sm text-gray-600">API Connected</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
