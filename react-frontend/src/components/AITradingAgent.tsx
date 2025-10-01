import React, { useState, useEffect } from 'react';
import { 
  ExclamationTriangleIcon, 
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MinusIcon, 
  CpuChipIcon, 
  ClockIcon, 
  TagIcon,
  StopIcon 
} from '@heroicons/react/24/outline';

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
  analysis_time_ms?: number;
  cached?: boolean;
}

interface AITradingAgentProps {
  symbol: string;
  onPredictionUpdate?: (prediction: TradingPrediction) => void;
  onRunBacktestResult?: (res: any) => void;
  onBacktestLoading?: (v: boolean) => void;
}

const AITradingAgent: React.FC<AITradingAgentProps> = ({ symbol, onPredictionUpdate, onRunBacktestResult, onBacktestLoading }) => {
  const [prediction, setPrediction] = useState<TradingPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchPrediction = async (forceRefresh = false) => {
    setLoading(true);
    setError(null);

    try {
      // Use AI agent endpoint (fallback to port 8001 for testing, 8000 for production)
      const baseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8001' : 'http://localhost:8000';
      const url = `${baseUrl}/agent/predict/${symbol}${forceRefresh ? '?force_refresh=true' : ''}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch prediction: ${response.status}`);
      }

      const data = await response.json();
      setPrediction(data);
      
      if (onPredictionUpdate) {
        onPredictionUpdate(data);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Error fetching AI prediction:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (symbol) {
      fetchPrediction();
    }
  }, [symbol]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (autoRefresh && symbol) {
      interval = setInterval(() => {
        fetchPrediction();
      }, 60000); // Refresh every minute
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [autoRefresh, symbol]);

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return <ArrowTrendingUpIcon className="h-5 w-5 text-green-500" />;
      case 'SELL':
        return <ArrowTrendingDownIcon className="h-5 w-5 text-red-500" />;
      case 'HOLD':
        return <MinusIcon className="h-5 w-5 text-yellow-500" />;
      default:
        return <ExclamationTriangleIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'SELL':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'HOLD':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toUpperCase()) {
      case 'LOW':
        return 'bg-green-100 text-green-800';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800';
      case 'HIGH':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading && !prediction) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center space-x-2 mb-4">
          <CpuChipIcon className="h-6 w-6 text-blue-500 animate-pulse" />
          <h3 className="text-lg font-semibold text-gray-900">AI Trading Analysis</h3>
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600">Analyzing {symbol}...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border border-red-200">
        <div className="flex items-center space-x-2 mb-4">
          <CpuChipIcon className="h-6 w-6 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-900">AI Trading Analysis</h3>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Analysis Failed</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => fetchPrediction(true)}
                  className="text-sm bg-red-100 text-red-800 px-3 py-1 rounded-md hover:bg-red-200 transition-colors"
                >
                  Retry Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 border">
        <div className="flex items-center space-x-2 mb-4">
          <CpuChipIcon className="h-6 w-6 text-gray-400" />
          <h3 className="text-lg font-semibold text-gray-900">AI Trading Analysis</h3>
        </div>
        <p className="text-gray-600">No prediction available for {symbol}</p>
        <button
          onClick={() => fetchPrediction()}
          className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
        >
          Generate Prediction
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border">
      {/* Run Backtest Button */}
      <div className="flex justify-end mb-4">
        <button
          onClick={async () => {
            if (onBacktestLoading) onBacktestLoading(true);
            try {
              const baseUrl = process.env.NODE_ENV === 'development' ? 'http://localhost:8001' : 'http://localhost:8000';
              const res = await fetch(`${baseUrl}/agent/backtest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol, start_date: new Date(new Date().setFullYear(new Date().getFullYear()-1)).toISOString().slice(0,10), end_date: new Date().toISOString().slice(0,10) })
              });
              const data = await res.json();
              if (onRunBacktestResult) onRunBacktestResult(data);
            } catch (err) {
              console.error('Backtest failed', err);
            } finally {
              if (onBacktestLoading) onBacktestLoading(false);
            }
          }}
          className="ml-2 bg-indigo-600 text-white px-3 py-1 rounded-md hover:bg-indigo-700 text-sm"
        >
          Run Backtest
        </button>
      </div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <CpuChipIcon className="h-6 w-6 text-blue-500" />
          <h3 className="text-lg font-semibold text-gray-900">AI Trading Analysis</h3>
          {prediction.cached && (
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
              Cached
            </span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-600">Auto-refresh</span>
          </label>
          <button
            onClick={() => fetchPrediction(true)}
            disabled={loading}
            className="text-sm bg-gray-100 text-gray-700 px-3 py-1 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Signal and Confidence */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Trading Signal</span>
            {getSignalIcon(prediction.signal)}
          </div>
          <div className={`mt-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getSignalColor(prediction.signal)}`}>
            {prediction.signal}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-600">Confidence</span>
            <span className={`text-lg font-bold ${getConfidenceColor(prediction.confidence)}`}>
              {prediction.confidence}%
            </span>
          </div>
          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                prediction.confidence >= 80 ? 'bg-green-500' :
                prediction.confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${prediction.confidence}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Price Targets */}
      {(prediction.entry_price || prediction.stop_loss || prediction.target_price) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {prediction.entry_price && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center space-x-2">
                <TagIcon className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium text-blue-800">Entry Price</span>
              </div>
              <p className="text-lg font-bold text-blue-900 mt-1">
                ${prediction.entry_price.toFixed(2)}
              </p>
            </div>
          )}

          {prediction.stop_loss && (
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <div className="flex items-center space-x-2">
                <StopIcon className="h-4 w-4 text-red-500" />
                <span className="text-sm font-medium text-red-800">Stop Loss</span>
              </div>
              <p className="text-lg font-bold text-red-900 mt-1">
                ${prediction.stop_loss.toFixed(2)}
              </p>
            </div>
          )}

          {prediction.target_price && (
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-center space-x-2">
                <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium text-green-800">Target Price</span>
              </div>
              <p className="text-lg font-bold text-green-900 mt-1">
                ${prediction.target_price.toFixed(2)}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Risk Level and Analysis Info */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Risk Level:</span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(prediction.risk_level)}`}>
            {prediction.risk_level}
          </span>
        </div>
        <div className="flex items-center space-x-4 text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <ClockIcon className="h-3 w-3" />
            <span>
              {new Date(prediction.timestamp).toLocaleTimeString()}
            </span>
          </div>
          {prediction.analysis_time_ms && (
            <span>{prediction.analysis_time_ms}ms</span>
          )}
        </div>
      </div>

      {/* Reasoning */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-2">Analysis Reasoning</h4>
        <ul className="space-y-1">
          {prediction.reasoning.map((reason, index) => (
            <li key={index} className="text-sm text-gray-700 flex items-start">
              <span className="text-blue-500 mr-2">•</span>
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AITradingAgent;
