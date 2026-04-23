import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Activity, TrendingUp, TrendingDown, RefreshCw, Zap, Crosshair } from 'lucide-react';

interface OptionSuggestion {
  symbol: string;
  strike_price: number;
  option_type: string;
  ltp: number;
  target: number;
  stop_loss: number;
  suggestion: string;
  reason: string;
}

const OptionsPage: React.FC = () => {
  const [index, setIndex] = useState('NIFTY');
  const [spotPrice, setSpotPrice] = useState(22500);
  const [suggestions, setSuggestions] = useState<OptionSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Mock WebSocket for realtime market data
  useEffect(() => {
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(`ws://localhost:8000/ws/market-data/${index}`);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.price) {
          setSpotPrice(data.price);
        }
      };
    } catch (e) {
      console.error('WebSocket connection failed', e);
    }
    
    return () => {
      if (ws) ws.close();
    };
  }, [index]);

  useEffect(() => {
    fetchSuggestions();
  }, [index, spotPrice]); // Ideally we'd debounce this or fetch on demand

  const fetchSuggestions = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/ai/options/suggestions/${index}?spot_price=${spotPrice}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setSuggestions(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTrade = (suggestion: OptionSuggestion) => {
    // Navigating to trade page with pre-filled details would be ideal
    // For now we'll just mock the trade execution
    alert(`Placing Order for ${suggestion.symbol} ${suggestion.strike_price} ${suggestion.option_type} at LTP ${suggestion.ltp}. Target: ${suggestion.target}, SL: ${suggestion.stop_loss}`);
    navigate('/trade');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-800 rounded-lg transition">
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <h1 className="text-2xl font-bold text-white">Options & Live AI Suggestions</h1>
          </div>
          <div className="flex gap-2 bg-slate-900 p-1 rounded-xl border border-slate-800">
            {['NIFTY', 'BANKNIFTY', 'FINNIFTY'].map(idx => (
              <button
                key={idx}
                onClick={() => setIndex(idx)}
                className={`px-6 py-2 rounded-lg font-bold text-sm transition ${index === idx ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'}`}
              >
                {idx}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Live Chart/Data Area */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
              <div>
                <h2 className="text-xl font-bold text-slate-400">{index} Live</h2>
                <div className="flex items-center gap-4 mt-2">
                  <span className="text-4xl font-mono font-bold text-white">{spotPrice.toFixed(2)}</span>
                  <span className="flex items-center gap-1 text-green-400 bg-green-500/10 px-3 py-1 rounded-full text-sm font-bold">
                    <TrendingUp className="w-4 h-4" /> +0.45%
                  </span>
                </div>
              </div>
              <Activity className="w-12 h-12 text-blue-500 opacity-50" />
            </div>

            <div className="h-96 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-center relative overflow-hidden">
              {/* Mock Chart UI */}
              <div className="absolute inset-0 opacity-20">
                <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full stroke-blue-500" strokeWidth="0.5" fill="none">
                  <path d="M0,100 L10,80 L20,90 L30,60 L40,70 L50,40 L60,50 L70,20 L80,30 L90,10 L100,20" />
                </svg>
              </div>
              <div className="z-10 text-center">
                <Activity className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                <p className="text-slate-500 font-bold">Live Chart View</p>
                <p className="text-xs text-slate-600 mt-2">Real-time OHLC candles streaming...</p>
              </div>
            </div>
          </div>

          {/* AI Suggestions Area */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" /> AI Suggestions
              </h2>
              <button onClick={fetchSuggestions} disabled={loading}>
                <RefreshCw className={`w-5 h-5 text-slate-400 hover:text-white transition ${loading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            <div className="space-y-4">
              {suggestions.length === 0 && !loading && (
                <p className="text-slate-500 text-center py-8">No specific high-conviction trades right now. Waiting for setup...</p>
              )}
              
              {suggestions.map((suggestion, idx) => (
                <div key={idx} className={`p-4 rounded-xl border ${suggestion.option_type === 'CE' ? 'border-green-500/30 bg-green-500/10' : 'border-red-500/30 bg-red-500/10'}`}>
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <span className={`font-bold px-2 py-1 rounded text-xs ${suggestion.option_type === 'CE' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'}`}>
                        {suggestion.strike_price} {suggestion.option_type}
                      </span>
                      <p className="text-sm mt-2 text-slate-300">{suggestion.reason}</p>
                    </div>
                    <span className="font-mono font-bold text-lg">₹{suggestion.ltp}</span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 my-4">
                    <div className="bg-slate-950/50 p-2 rounded-lg text-center">
                      <p className="text-xs text-slate-500 mb-1">Target</p>
                      <p className="font-mono text-green-400 font-bold">₹{suggestion.target}</p>
                    </div>
                    <div className="bg-slate-950/50 p-2 rounded-lg text-center">
                      <p className="text-xs text-slate-500 mb-1">Stop Loss</p>
                      <p className="font-mono text-red-400 font-bold">₹{suggestion.stop_loss}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => handleTrade(suggestion)}
                    className={`w-full py-3 rounded-lg font-bold transition flex justify-center items-center gap-2 ${
                      suggestion.option_type === 'CE' 
                        ? 'bg-green-600 hover:bg-green-500' 
                        : 'bg-red-600 hover:bg-red-500'
                    }`}
                  >
                    <Crosshair className="w-4 h-4" /> Execute Trade
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OptionsPage;
