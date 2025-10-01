import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import AITradingAgent from '../components/AITradingAgent';
import { 
  CpuChipIcon, 
  ArrowTrendingUpIcon, 
  MagnifyingGlassIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface TradingPrediction {
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string[];
  entry_price?: number;
  stop_loss?: number;
  target_price?: number;
  timestamp: string;
  timeframe: string;
  risk_level: string;
}

const AITradingPage: React.FC = () => {
  const { user } = useAuth();
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [customSymbol, setCustomSymbol] = useState('');
  const [predictions, setPredictions] = useState<Record<string, TradingPrediction>>({});
  const [backtestResult, setBacktestResult] = useState<any | null>(null);

  const popularSymbols = [
    'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX',
    'BTC-USD', 'ETH-USD', 'SPY', 'QQQ', 'VTI', 'ARKK'
  ];

  const handleSymbolChange = (symbol: string) => {
    setSelectedSymbol(symbol.toUpperCase());
  };

  const handleCustomSymbolSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customSymbol.trim()) {
      const symbol = customSymbol.trim().toUpperCase();
      setSelectedSymbol(symbol);
      setCustomSymbol('');
    }
  };

  const handlePredictionUpdate = (prediction: TradingPrediction) => {
    setPredictions(prev => ({
      ...prev,
      [prediction.symbol]: prediction
    }));
  };

  const clearAllPredictions = () => {
    setPredictions({});
    toast.success('All predictions cleared');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <CpuChipIcon className="h-8 w-8 text-blue-500" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">AI Trading Assistant</h1>
                <p className="text-sm text-gray-500">Advanced trading predictions powered by AI</p>
              </div>
            </div>
            <div className="text-sm text-gray-600">
              Welcome, {user?.email}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Symbol Selection */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border">
          <div className="flex items-center space-x-2 mb-4">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Select Trading Symbol</h2>
          </div>

          {/* Popular Symbols */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Popular Symbols
            </label>
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-12 gap-2">
              {popularSymbols.map((symbol) => (
                <button
                  key={symbol}
                  onClick={() => handleSymbolChange(symbol)}
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    selectedSymbol === symbol
                      ? 'bg-blue-100 text-blue-800 border-2 border-blue-300'
                      : 'bg-gray-100 text-gray-700 border-2 border-gray-200 hover:bg-gray-200'
                  }`}
                >
                  {symbol}
                </button>
              ))}
            </div>
          </div>

          {/* Custom Symbol Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Or Enter Custom Symbol
            </label>
            <form onSubmit={handleCustomSymbolSubmit} className="flex space-x-2">
              <input
                type="text"
                value={customSymbol}
                onChange={(e) => setCustomSymbol(e.target.value)}
                placeholder="e.g., TSLA, BTC-USD, EURUSD"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Analyze
              </button>
            </form>
          </div>

          {/* Current Selection */}
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="h-4 w-4 text-blue-500" />
              <span className="text-sm font-medium text-blue-800">
                Currently analyzing: <strong>{selectedSymbol}</strong>
              </span>
            </div>
          </div>
        </div>

        {/* AI Trading Agent */}
        <div className="mb-6">
          <AITradingAgent
            symbol={selectedSymbol}
            onPredictionUpdate={handlePredictionUpdate}
            onRunBacktestResult={(res: any) => setBacktestResult(res)}
          />
        </div>

        {/* Prediction History */}
        {Object.keys(predictions).length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <ArrowTrendingUpIcon className="h-5 w-5 text-green-500" />
                <h2 className="text-lg font-semibold text-gray-900">Recent Predictions</h2>
              </div>
              <button
                onClick={clearAllPredictions}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Clear All
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(predictions)
                .sort(([, a], [, b]) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
                .slice(0, 6) // Show last 6 predictions
                .map(([symbol, prediction]) => (
                  <div key={symbol} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">{symbol}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        prediction.signal === 'BUY'
                          ? 'bg-green-100 text-green-800'
                          : prediction.signal === 'SELL'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {prediction.signal}
                      </span>
                    </div>
                    <div className="space-y-1 text-sm text-gray-600">
                      <div className="flex justify-between">
                        <span>Confidence:</span>
                        <span className="font-medium">{prediction.confidence}%</span>
                      </div>
                      {prediction.entry_price && (
                        <div className="flex justify-between">
                          <span>Entry:</span>
                          <span className="font-medium">${prediction.entry_price.toFixed(2)}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span>Risk:</span>
                        <span className={`font-medium ${
                          prediction.risk_level === 'LOW' ? 'text-green-600' :
                          prediction.risk_level === 'HIGH' ? 'text-red-600' : 'text-yellow-600'
                        }`}>
                          {prediction.risk_level}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 mt-2">
                        {new Date(prediction.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Features Info */}
        {/* Backtest Results */}
        {backtestResult && (
          <div className="mt-6 bg-white rounded-lg shadow-md p-6 border">
            <h3 className="text-lg font-semibold mb-3">Backtest Results ({backtestResult?.metrics?.total_return_pct?.toFixed ? backtestResult.metrics.total_return_pct.toFixed(2) : ''}%)</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded">
                <div className="text-sm text-gray-600">Total Return</div>
                <div className="text-2xl font-bold">{backtestResult.metrics.total_return_pct.toFixed(2)}%</div>
              </div>
              <div className="p-4 border rounded">
                <div className="text-sm text-gray-600">Win Rate</div>
                <div className="text-2xl font-bold">{backtestResult.metrics.win_rate_pct.toFixed(2)}%</div>
              </div>
              <div className="p-4 border rounded">
                <div className="text-sm text-gray-600">Max Drawdown</div>
                <div className="text-2xl font-bold">{backtestResult.metrics.max_drawdown_pct.toFixed(2)}%</div>
              </div>
              <div className="p-4 border rounded">
                <div className="text-sm text-gray-600">Sharpe Ratio</div>
                <div className="text-2xl font-bold">{backtestResult.metrics.sharpe_ratio.toFixed(2)}</div>
              </div>
            </div>

            {/* Simple equity curve */}
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Equity Curve</h4>
              <div className="w-full h-48 bg-gray-50 border rounded p-2 overflow-auto">
                <svg viewBox="0 0 400 120" className="w-full h-full">
                  {(() => {
                    const series = backtestResult.equity_curve.map((p: any) => p.value);
                    if (series.length === 0) return null;
                    const min = Math.min(...series);
                    const max = Math.max(...series);
                    const points = series.map((v: number, i: number) => {
                      const x = (i / (series.length - 1 || 1)) * 400;
                      const y = 120 - ((v - min) / ((max - min) || 1)) * 100 - 10;
                      return `${x},${y}`;
                    }).join(' ');
                    return <polyline fill="none" stroke="#2563eb" strokeWidth={2} points={points} />;
                  })()}
                </svg>
              </div>
            </div>
          </div>
        )}
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Trading Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <ChartBarIcon className="h-4 w-4 text-blue-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Technical Analysis</h4>
                <p className="text-sm text-gray-600">RSI, MACD, Moving Averages, Bollinger Bands</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <CpuChipIcon className="h-4 w-4 text-green-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Sentiment Analysis</h4>
                <p className="text-sm text-gray-600">News sentiment using FinBERT AI model</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                <ArrowTrendingUpIcon className="h-4 w-4 text-purple-600" />
              </div>
              <div>
                <h4 className="font-medium text-gray-900">GPT Analysis</h4>
                <p className="text-sm text-gray-600">Advanced reasoning with GPT-4 (when configured)</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AITradingPage;
