import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Wallet, TrendingUp, TrendingDown, Percent, Settings, Zap } from 'lucide-react';

const TradingPage: React.FC = () => {
  const [balances, setBalances] = useState<any>({});
  const [symbol, setSymbol] = useState('RELIANCE');
  const [price, setPrice] = useState(2500.50);
  const [quantity, setQuantity] = useState(1);
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderType, setOrderType] = useState('MARKET');
  const [brokerId, setBrokerId] = useState(1); // Default, should ideally be selected
  const navigate = useNavigate();

  useEffect(() => {
    fetchBalances();
  }, []);

  const fetchBalances = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/trades/balance', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setBalances(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleTrade = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/trades/place', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          broker_id: brokerId,
          symbol,
          quantity,
          side,
          order_type: orderType,
          price: orderType === 'LIMIT' ? price : null
        })
      });
      
      const data = await res.json();
      if (res.ok) {
        alert('Order placed successfully! ID: ' + data.order_id);
      } else {
        alert('Order failed: ' + data.detail);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Simple mock of available balance calculation
  const getAvailableBalance = () => {
    let total = 0;
    Object.values(balances).forEach((b: any) => {
      if (b && typeof b === 'object' && b.available) {
        total += b.available;
      } else if (b && typeof b === 'object' && b.net) {
        total += b.net;
      }
    });
    return total || 150000; // Fallback for UI demo
  };

  const totalValue = price * quantity;
  const estimatedCharges = totalValue * 0.001; // Mock 0.1% charges
  const finalAmount = side === 'BUY' ? totalValue + estimatedCharges : totalValue - estimatedCharges;
  const availableBalance = getAvailableBalance();
  const maxQty = Math.floor(availableBalance / price);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <button onClick={() => navigate(-1)} className="p-2 hover:bg-slate-800 rounded-lg transition">
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <h1 className="text-2xl font-bold text-white">Trading Terminal</h1>
          </div>
          <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">
            <Wallet className="w-5 h-5 text-blue-400" />
            <div>
              <p className="text-xs text-slate-500">Available Margin</p>
              <p className="font-mono font-bold text-white">₹{availableBalance.toFixed(2)}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Trading Panel */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold">Order Setup</h2>
              <div className="flex bg-slate-800 rounded-lg p-1">
                <button
                  className={`px-6 py-2 rounded-md font-bold text-sm transition ${side === 'BUY' ? 'bg-green-600 text-white' : 'text-slate-400 hover:text-white'}`}
                  onClick={() => setSide('BUY')}
                >
                  BUY
                </button>
                <button
                  className={`px-6 py-2 rounded-md font-bold text-sm transition ${side === 'SELL' ? 'bg-red-600 text-white' : 'text-slate-400 hover:text-white'}`}
                  onClick={() => setSide('SELL')}
                >
                  SELL
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm text-slate-400 mb-2">Symbol</label>
                <input
                  type="text"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-2">Order Type</label>
                <select
                  value={orderType}
                  onChange={(e) => setOrderType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 appearance-none"
                >
                  <option value="MARKET">MARKET</option>
                  <option value="LIMIT">LIMIT</option>
                  <option value="SL">SL</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm text-slate-400">Quantity</label>
                  <button 
                    onClick={() => setQuantity(maxQty)}
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    Max: {maxQty}
                  </button>
                </div>
                <div className="flex">
                  <button onClick={() => setQuantity(Math.max(1, quantity - 1))} className="bg-slate-800 px-4 py-3 rounded-l-xl border-y border-l border-slate-700">-</button>
                  <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                    className="w-full bg-slate-950 border-y border-slate-700 px-4 py-3 text-center text-white focus:outline-none"
                  />
                  <button onClick={() => setQuantity(quantity + 1)} className="bg-slate-800 px-4 py-3 rounded-r-xl border-y border-r border-slate-700">+</button>
                </div>
              </div>
              <div>
                <label className="block text-sm text-slate-400 mb-2">Price (LTP: ₹{price})</label>
                <input
                  type="number"
                  value={price}
                  onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
                  disabled={orderType === 'MARKET'}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            {/* AI Robo Call Option */}
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 rounded-lg">
                  <Zap className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-bold text-blue-400">Robo Call Option</h3>
                  <p className="text-xs text-blue-200/70">Execute AI suggested trades automatically</p>
                </div>
              </div>
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-bold transition">
                Enable Auto-Trade
              </button>
            </div>
            
            <button
              onClick={handleTrade}
              className={`w-full py-4 rounded-xl font-bold text-lg transition shadow-lg ${
                side === 'BUY' 
                  ? 'bg-green-600 hover:bg-green-500 shadow-green-900/20' 
                  : 'bg-red-600 hover:bg-red-500 shadow-red-900/20'
              }`}
            >
              {side} {quantity} {symbol}
            </button>
          </div>

          {/* Order Breakup Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex flex-col">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Settings className="w-5 h-5 text-slate-400" /> Order Breakup
            </h2>

            <div className="space-y-4 flex-grow">
              <div className="flex justify-between items-center pb-4 border-b border-slate-800">
                <span className="text-slate-400">Trade Value</span>
                <span className="font-mono text-white">₹{totalValue.toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b border-slate-800">
                <span className="text-slate-400">Brokerage</span>
                <span className="font-mono text-white">₹20.00</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b border-slate-800">
                <span className="text-slate-400">Exchange Charges</span>
                <span className="font-mono text-white">₹{(estimatedCharges - 20).toFixed(2)}</span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b border-slate-800">
                <span className="text-slate-400">GST (18%)</span>
                <span className="font-mono text-white">₹{(estimatedCharges * 0.18).toFixed(2)}</span>
              </div>
              
              <div className="pt-4 mt-auto">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-lg font-bold text-white">{side === 'BUY' ? 'Required Margin' : 'Amount Receivable'}</span>
                  <span className={`text-xl font-mono font-bold ${side === 'BUY' ? 'text-red-400' : 'text-green-400'}`}>
                    ₹{finalAmount.toFixed(2)}
                  </span>
                </div>
                {side === 'BUY' && finalAmount > availableBalance && (
                  <div className="bg-red-500/20 text-red-400 text-sm p-3 rounded-lg flex items-start gap-2 mt-4">
                    <TrendingDown className="w-4 h-4 mt-0.5 shrink-0" />
                    <span>Insufficient funds. Please add ₹{(finalAmount - availableBalance).toFixed(2)} to execute this trade.</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TradingPage;
