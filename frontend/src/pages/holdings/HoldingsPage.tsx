import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Wallet,
  ChevronDown,
  ChevronUp,
  Eye,
  Briefcase,
  PieChart,
  ArrowDownUp,
  X,
  Filter,
  Star
} from 'lucide-react';

interface Holding {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  total_value: number;
  profit_loss: number;
  profit_loss_percent: number;
  exchange: string;
  product_type: string;
  broker_name: string;
  symbol_token?: string;
  payout?: number;
  day_change?: number;
  day_change_percent?: number;
}

interface HoldingsSummary {
  total_invested: number;
  total_current_value: number;
  total_profit_loss: number;
  total_profit_loss_percent: number;
  holdings: Holding[];
  by_broker: Record<string, Holding[]>;
}

const HoldingsPage: React.FC = () => {
  const [holdings, setHoldings] = useState<HoldingsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showBroker, setShowBroker] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<'value' | 'pnl' | 'name'>('value');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [filterBroker, setFilterBroker] = useState<string>('all');
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [selectedHoldings, setSelectedHoldings] = useState<Set<string>>(new Set());

  const navigate = useNavigate();

  useEffect(() => {
    fetchHoldings();
  }, []);

  const fetchHoldings = async () => {
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/holdings/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Failed to fetch holdings');
      }

      const data = await res.json();
      setHoldings(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load holdings');
    } finally {
      setLoading(false);
    }
  };

  const toggleSort = (field: 'value' | 'pnl' | 'name') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const sortedHoldings = React.useMemo(() => {
    if (!holdings) return [];

    let filtered = filterBroker === 'all'
      ? holdings.holdings
      : holdings.holdings.filter(h => h.broker_name === filterBroker);

    return [...filtered].sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'value') comparison = a.total_value - b.total_value;
      else if (sortBy === 'pnl') comparison = a.profit_loss - b.profit_loss;
      else if (sortBy === 'name') comparison = a.symbol.localeCompare(b.symbol);
      return sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [holdings, sortBy, sortOrder, filterBroker]);

  const toggleHoldingSelection = (symbol: string) => {
    const newSelected = new Set(selectedHoldings);
    if (newSelected.has(symbol)) {
      newSelected.delete(symbol);
    } else {
      newSelected.add(symbol);
    }
    setSelectedHoldings(newSelected);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value: number) => {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Fetching your portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="bg-slate-900 border border-red-500/30 rounded-2xl p-8 max-w-md w-full text-center">
          <div className="p-3 bg-red-500/20 rounded-full w-fit mx-auto mb-4">
            <Wallet className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Unable to Load Holdings</h2>
          <p className="text-slate-400 mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={fetchHoldings}
              className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition"
            >
              Retry
            </button>
            <button
              onClick={() => navigate('/demat')}
              className="w-full bg-slate-800 hover:bg-slate-700 py-3 rounded-xl font-bold transition"
            >
              Link Broker Account
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!holdings || holdings.holdings.length === 0) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-md w-full text-center">
          <div className="p-3 bg-slate-800 rounded-full w-fit mx-auto mb-4">
            <Wallet className="w-8 h-8 text-slate-400" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">No Holdings Found</h2>
          <p className="text-slate-400 mb-6">Link a broker account and fetch your holdings to see them here.</p>
          <button
            onClick={() => navigate('/demat')}
            className="w-full bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold transition"
          >
            Link Broker Account
          </button>
        </div>
      </div>
    );
  }

  const brokers = Object.keys(holdings.by_broker).filter(k => !holdings.by_broker[k]?.error);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/admin')}
              className="p-2 hover:bg-slate-800 rounded-lg transition"
            >
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-600 rounded-lg">
                <PieChart className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Portfolio Holdings</h1>
                <p className="text-xs text-slate-500">
                  {holdings.holdings.length} holdings across {brokers.length} broker(s)
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={fetchHoldings}
            className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg font-bold text-sm transition flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Wallet className="w-5 h-5 text-blue-400" />
              </div>
              <span className="text-slate-500 text-sm">Total Invested</span>
            </div>
            <h3 className="text-2xl font-bold text-white">{formatCurrency(holdings.total_invested)}</h3>
          </div>

          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 bg-indigo-500/20 rounded-lg">
                <PieChart className="w-5 h-5 text-indigo-400" />
              </div>
              <span className="text-slate-500 text-sm">Current Value</span>
            </div>
            <h3 className="text-2xl font-bold text-white">{formatCurrency(holdings.total_current_value)}</h3>
          </div>

          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${holdings.total_profit_loss >= 0 ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                {holdings.total_profit_loss >= 0 ? (
                  <TrendingUp className="w-5 h-5 text-green-400" />
                ) : (
                  <TrendingDown className="w-5 h-5 text-red-400" />
                )}
              </div>
              <span className="text-slate-500 text-sm">Total P&L</span>
            </div>
            <h3 className={`text-2xl font-bold ${holdings.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatCurrency(holdings.total_profit_loss)}
            </h3>
          </div>

          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${holdings.total_profit_loss_percent >= 0 ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                <ArrowDownUp className={`w-5 h-5 ${holdings.total_profit_loss_percent >= 0 ? 'text-green-400' : 'text-red-400'}`} />
              </div>
              <span className="text-slate-500 text-sm">Return</span>
            </div>
            <h3 className={`text-2xl font-bold ${holdings.total_profit_loss_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatPercent(holdings.total_profit_loss_percent)}
            </h3>
          </div>
        </div>

        {/* Broker Tabs */}
        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-2 mb-6">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setFilterBroker('all')}
              className={`px-4 py-2 rounded-lg font-bold text-sm transition ${
                filterBroker === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              All Brokers ({holdings.holdings.length})
            </button>
            {brokers.map(broker => (
              <button
                key={broker}
                onClick={() => setFilterBroker(broker)}
                className={`px-4 py-2 rounded-lg font-bold text-sm transition ${
                  filterBroker === broker
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                {broker} ({(holdings.by_broker[broker] || []).length})
              </button>
            ))}
          </div>
        </div>

        {/* Holdings Table */}
        <div className="bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
          {/* Table Header */}
          <div className="grid grid-cols-12 gap-4 px-6 py-4 bg-slate-950 border-b border-slate-800 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <div className="col-span-1 flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedHoldings.size === sortedHoldings.length && sortedHoldings.length > 0}
                onChange={() => {
                  if (selectedHoldings.size === sortedHoldings.length) {
                    setSelectedHoldings(new Set());
                  } else {
                    setSelectedHoldings(new Set(sortedHoldings.map(h => h.symbol)));
                  }
                }}
                className="rounded border-slate-600"
              />
            </div>
            <div className="col-span-2 cursor-pointer flex items-center gap-1" onClick={() => toggleSort('name')}>
              Symbol {sortBy === 'name' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
            </div>
            <div className="col-span-1 text-center">Qty</div>
            <div className="col-span-2 text-right">Avg Price</div>
            <div className="col-span-2 text-right">Current</div>
            <div className="col-span-2 cursor-pointer text-right flex items-center justify-end gap-1" onClick={() => toggleSort('value')}>
              Value {sortBy === 'value' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
            </div>
            <div className="col-span-2 cursor-pointer text-right flex items-center justify-end gap-1" onClick={() => toggleSort('pnl')}>
              P&L {sortBy === 'pnl' && (sortOrder === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
            </div>
          </div>

          {/* Table Body */}
          <div className="divide-y divide-slate-800">
            {sortedHoldings.map((holding, idx) => (
              <div key={`${holding.symbol}-${holding.broker_name}-${idx}`}>
                <div
                  className={`grid grid-cols-12 gap-4 px-6 py-4 items-center hover:bg-slate-800/50 transition cursor-pointer ${
                    selectedHoldings.has(holding.symbol) ? 'bg-blue-500/10' : ''
                  }`}
                  onClick={() => setExpandedRow(expandedRow === `${holding.symbol}-${idx}` ? null : `${holding.symbol}-${idx}`)}
                >
                  <div className="col-span-1" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selectedHoldings.has(holding.symbol)}
                      onChange={() => toggleHoldingSelection(holding.symbol)}
                      className="rounded border-slate-600"
                    />
                  </div>
                  <div className="col-span-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white">{holding.symbol}</span>
                      <span className="text-xs text-slate-500">{holding.exchange}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs text-slate-600 bg-slate-800 px-2 py-0.5 rounded">{holding.broker_name}</span>
                      <span className="text-xs text-slate-600">{holding.product_type}</span>
                    </div>
                  </div>
                  <div className="col-span-1 text-center font-mono">{holding.quantity}</div>
                  <div className="col-span-2 text-right font-mono">{formatCurrency(holding.avg_price)}</div>
                  <div className="col-span-2 text-right font-mono">{formatCurrency(holding.current_price)}</div>
                  <div className="col-span-2 text-right font-mono">{formatCurrency(holding.total_value)}</div>
                  <div className="col-span-2 text-right">
                    <div className={`flex flex-col items-end ${holding.profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      <span className="font-bold">{formatCurrency(holding.profit_loss)}</span>
                      <span className="text-xs">{formatPercent(holding.profit_loss_percent)}</span>
                    </div>
                  </div>
                </div>

                {/* Expanded Row Details */}
                {expandedRow === `${holding.symbol}-${idx}` && (
                  <div className="bg-slate-950 px-6 py-6 border-t border-slate-800">
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Symbol Token</p>
                        <p className="text-sm font-mono text-white">{holding.symbol_token || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Exchange</p>
                        <p className="text-sm text-white">{holding.exchange}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Product Type</p>
                        <p className="text-sm text-white">{holding.product_type}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Payout</p>
                        <p className="text-sm text-white">{formatCurrency(holding.payout || 0)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Day Change</p>
                        <p className={`text-sm ${(holding.day_change || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {formatCurrency(holding.day_change || 0)} ({formatPercent(holding.day_change_percent || 0)})
                        </p>
                      </div>
                      <div>
                        <p className="text-xs text-slate-500 mb-1">Broker</p>
                        <p className="text-sm text-white">{holding.broker_name}</p>
                      </div>
                    </div>
                    <div className="mt-6 flex gap-3">
                      <button className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm font-bold transition flex items-center gap-2">
                        <Eye className="w-4 h-4" /> View Chart
                      </button>
                      <button className="bg-slate-800 hover:bg-slate-700 px-4 py-2 rounded-lg text-sm font-bold transition flex items-center gap-2">
                        <ArrowDownUp className="w-4 h-4" /> Trade
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Selected Summary */}
        {selectedHoldings.size > 0 && (
          <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-blue-600 px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-4">
            <span className="text-white font-bold">{selectedHoldings.size} selected</span>
            <div className="h-6 w-px bg-blue-400" />
            <button
              onClick={() => setSelectedHoldings(new Set())}
              className="text-blue-200 hover:text-white text-sm"
            >
              Clear
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default HoldingsPage;
