import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Activity, Target, ShieldAlert, Zap, AlertCircle } from 'lucide-react';

interface AIAnalysis {
  symbol: string;
  analysis: string;
  target_1: number;
  target_2: number;
  target_3: number;
  stop_loss: number;
  recommendation: string;
  confidence: number;
  risk_level: string;
}

interface AISummaryResponse {
  summary: string;
  analyses: AIAnalysis[];
}

const AISummaryPage: React.FC = () => {
  const [data, setData] = useState<AISummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/ai/summary/holdings', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!res.ok) {
        throw new Error('Failed to fetch AI summary');
      }

      const result = await res.json();
      setData(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationColor = (rec: string) => {
    if (rec === 'BUY') return 'text-green-400 bg-green-500/20';
    if (rec === 'SELL') return 'text-red-400 bg-red-500/20';
    return 'text-yellow-400 bg-yellow-500/20';
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-800 rounded-lg transition">
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Zap className="w-6 h-6 text-yellow-400" /> AI Portfolio Summary
            </h1>
          </div>
          <button
            onClick={fetchSummary}
            className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg font-bold text-sm transition flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-20">
            <RefreshCw className="w-12 h-12 text-blue-500 animate-spin" />
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-2xl text-center">
            <AlertCircle className="w-10 h-10 text-red-400 mx-auto mb-2" />
            <p className="text-red-400">{error}</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
              <h2 className="text-lg font-bold mb-2">Overall Summary</h2>
              <p className="text-slate-400">{data?.summary}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data?.analyses.map((analysis, idx) => (
                <div key={idx} className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-bold">{analysis.symbol}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getRecommendationColor(analysis.recommendation)}`}>
                        {analysis.recommendation}
                      </span>
                    </div>
                    <p className="text-slate-400 text-sm mb-4 h-16 overflow-y-auto">{analysis.analysis}</p>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500 flex items-center gap-1"><Target className="w-4 h-4"/> Target 1</span>
                        <span className="font-mono text-green-400">₹{analysis.target_1}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500 flex items-center gap-1"><Target className="w-4 h-4"/> Target 2</span>
                        <span className="font-mono text-green-400">₹{analysis.target_2}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500 flex items-center gap-1"><Target className="w-4 h-4"/> Target 3</span>
                        <span className="font-mono text-green-400">₹{analysis.target_3}</span>
                      </div>
                      <div className="flex justify-between text-sm mt-3 pt-3 border-t border-slate-800">
                        <span className="text-slate-500 flex items-center gap-1"><ShieldAlert className="w-4 h-4"/> Stop Loss</span>
                        <span className="font-mono text-red-400">₹{analysis.stop_loss}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-between text-xs text-slate-500 mt-2">
                    <span>Confidence: {analysis.confidence}%</span>
                    <span>Risk: <span className={analysis.risk_level === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}>{analysis.risk_level}</span></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AISummaryPage;
