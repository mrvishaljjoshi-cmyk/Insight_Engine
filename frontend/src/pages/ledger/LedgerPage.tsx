import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, History, RefreshCw, FileText, Search } from 'lucide-react';

interface TradeRecord {
  id?: string;
  order_id?: string;
  symbol: string;
  quantity: number;
  average_price?: number;
  price?: number;
  transaction_type?: string;
  side?: string;
  product?: string;
  order_timestamp?: string;
  exchange?: string;
  broker?: string;
  status?: string;
}

const LedgerPage: React.FC = () => {
  const [trades, setTrades] = useState<TradeRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/trades/history', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setTrades(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const filteredTrades = trades.filter(t => 
    t.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    t.broker?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-800 rounded-lg transition">
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <History className="w-6 h-6 text-blue-400" /> Trade Ledger
            </h1>
          </div>
          <button
            onClick={fetchHistory}
            className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg font-bold text-sm transition flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-4 border-b border-slate-800 bg-slate-950 flex items-center justify-between">
            <div className="relative">
              <Search className="w-5 h-5 text-slate-500 absolute left-3 top-1/2 transform -translate-y-1/2" />
              <input 
                type="text" 
                placeholder="Search trades..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-blue-500 w-64"
              />
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <FileText className="w-4 h-4" />
              <span>{filteredTrades.length} Records found</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-950 text-slate-400 text-xs uppercase tracking-wider">
                  <th className="p-4 font-bold border-b border-slate-800">Time</th>
                  <th className="p-4 font-bold border-b border-slate-800">Symbol</th>
                  <th className="p-4 font-bold border-b border-slate-800">Type</th>
                  <th className="p-4 font-bold border-b border-slate-800 text-right">Qty</th>
                  <th className="p-4 font-bold border-b border-slate-800 text-right">Price</th>
                  <th className="p-4 font-bold border-b border-slate-800 text-right">Value</th>
                  <th className="p-4 font-bold border-b border-slate-800">Broker</th>
                  <th className="p-4 font-bold border-b border-slate-800 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-slate-500">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" />
                      Loading history...
                    </td>
                  </tr>
                ) : filteredTrades.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="p-8 text-center text-slate-500">
                      No trades found.
                    </td>
                  </tr>
                ) : (
                  filteredTrades.map((trade, idx) => {
                    const price = trade.average_price || trade.price || 0;
                    const side = (trade.transaction_type || trade.side || 'BUY').toUpperCase();
                    return (
                      <tr key={idx} className="hover:bg-slate-800/50 transition">
                        <td className="p-4 text-sm text-slate-400">
                          {trade.order_timestamp ? new Date(trade.order_timestamp).toLocaleString() : 'N/A'}
                        </td>
                        <td className="p-4 font-bold text-white">
                          {trade.symbol}
                          <span className="block text-xs text-slate-500 font-normal">{trade.exchange || 'NSE'} | {trade.product || 'MIS'}</span>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-xs font-bold ${side === 'BUY' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                            {side}
                          </span>
                        </td>
                        <td className="p-4 text-right font-mono">{trade.quantity}</td>
                        <td className="p-4 text-right font-mono">₹{price.toFixed(2)}</td>
                        <td className="p-4 text-right font-mono">₹{(trade.quantity * price).toFixed(2)}</td>
                        <td className="p-4 text-sm text-slate-300">{trade.broker || 'N/A'}</td>
                        <td className="p-4 text-center">
                          <span className={`px-2 py-1 rounded text-xs font-bold bg-blue-500/20 text-blue-400`}>
                            {trade.status || 'COMPLETE'}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LedgerPage;
