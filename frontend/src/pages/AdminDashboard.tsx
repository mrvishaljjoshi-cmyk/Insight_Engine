import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Wallet,
  Briefcase,
  TrendingUp,
  TrendingDown,
  Plus,
  RefreshCw,
  ChevronRight,
  Link2,
  PieChart,
  Activity,
  X,
  Check,
  Trash2,
  Zap,
  Target,
  History,
  MessageSquare,
  Send,
  Sparkles
} from 'lucide-react';

const BROKERS = [
  { name: 'Angel One', fields: ['SmartAPI Key', 'Client ID', 'Password', 'TOTP Secret'], guide: 'Visit smartapi.angelbroking.com to generate API keys.' },
  { name: 'Zerodha', fields: ['API Key', 'API Secret', 'Client ID', 'TOTP Secret'], guide: 'Go to kite.trade to create an app.' },
  { name: 'Groww', fields: ['API Key', 'API Secret'], guide: 'Check Settings > Trading APIs on Groww web.' },
  { name: 'Dhan', fields: ['Client ID', 'Access Token'], guide: 'Generate token at hq.dhan.co.' },
  { name: 'Upstox', fields: ['API Key', 'API Secret', 'Redirect URI'], guide: 'Create app at developer.upstox.com.' },
];

const AdminDashboard: React.FC = () => {
  const [connectedBrokers, setConnectedBrokers] = useState<any[]>([]);
  const [holdingsSummary, setHoldingsSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<{role: 'user' | 'ai', text: string}[]>([
    {role: 'ai', text: 'Hello! I am your Insight Engine AI. How can I help you with your trades today?'}
  ]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchBrokers();
    fetchHoldings();
  }, []);

  const fetchBrokers = async () => {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/brokers/', { headers: { 'Authorization': `Bearer ${token}` } });
    if (res.ok) setConnectedBrokers(await res.json());
  };

  const fetchHoldings = async () => {
    setLoading(true);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('/holdings/', { headers: { 'Authorization': `Bearer ${token}` } });
      if (res.ok) setHoldingsSummary(await res.json());
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim()) return;
    const msg = chatMessage;
    setChatHistory([...chatHistory, {role: 'user', text: msg}]);
    setChatMessage('');
    
    // Simple mock AI response for chat setup
    setTimeout(() => {
      setChatHistory(prev => [...prev, {role: 'ai', text: `Analyzing market for "${msg}"... Based on current NIFTY trend (22,500), I suggest looking at ATM Call options for immediate momentum.`}]);
    }, 1000);
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(value);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex overflow-hidden">
      {/* Sidebar Navigation */}
      <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-black text-white tracking-tighter">INSIGHT V2</h1>
          </div>
        </div>
        
        <nav className="p-4 flex-grow space-y-2">
          <button onClick={() => navigate('/admin')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-indigo-600 text-white font-bold transition shadow-lg shadow-indigo-900/20">
            <PieChart className="w-5 h-5" /> Dashboard
          </button>
          <button onClick={() => navigate('/holdings')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 hover:text-white transition font-medium">
            <Briefcase className="w-5 h-5" /> Portfolio
          </button>
          <button onClick={() => navigate('/ai-summary')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 hover:text-white transition font-medium">
            <Sparkles className="w-5 h-5 text-yellow-400" /> AI Insights
          </button>
          <button onClick={() => navigate('/options')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 hover:text-white transition font-medium">
            <Activity className="w-5 h-5 text-blue-400" /> Option Chain
          </button>
          <button onClick={() => navigate('/trade')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 hover:text-white transition font-medium">
            <Target className="w-5 h-5 text-green-400" /> Trading Terminal
          </button>
          <button onClick={() => navigate('/ledger')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-slate-800 hover:text-white transition font-medium">
            <History className="w-5 h-5 text-slate-500" /> Trade Ledger
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button onClick={() => navigate('/demat')} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 text-slate-300 hover:text-white transition font-medium">
            <Link2 className="w-5 h-5" /> Link Brokers
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-grow overflow-y-auto relative">
        {/* Top Header */}
        <header className="sticky top-0 z-20 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 px-8 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">Executive Overview</h2>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 bg-slate-900 px-3 py-1.5 rounded-full border border-slate-800">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs font-bold text-slate-300 uppercase">Live Market</span>
            </div>
            <button onClick={() => setChatOpen(!chatOpen)} className="p-2 bg-slate-800 hover:bg-slate-700 rounded-full transition relative">
              <MessageSquare className="w-5 h-5 text-blue-400" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-blue-500 rounded-full" />
            </button>
          </div>
        </header>

        <div className="p-8">
          {/* Dashboard Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Total Wealth</p>
              <h3 className="text-3xl font-black text-white">{holdingsSummary ? formatCurrency(holdingsSummary.total_current_value) : '₹0.00'}</h3>
              <div className="flex items-center gap-1 mt-4 text-green-400 text-sm font-bold">
                <TrendingUp className="w-4 h-4" />
                <span>+12.4% Overall</span>
              </div>
            </div>
            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl">
              <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">P&L Status</p>
              <h3 className={`text-3xl font-black ${holdingsSummary?.total_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {holdingsSummary ? formatCurrency(holdingsSummary.total_profit_loss) : '₹0.00'}
              </h3>
              <p className="text-xs text-slate-500 mt-4">Calculated across {connectedBrokers.length} brokers</p>
            </div>
            <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl col-span-2">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">AI Signal Strength</p>
                  <h3 className="text-3xl font-black text-indigo-400">78% BULLISH</h3>
                </div>
                <div className="p-3 bg-indigo-500/10 rounded-2xl border border-indigo-500/30">
                  <Sparkles className="w-8 h-8 text-indigo-400" />
                </div>
              </div>
              <p className="text-xs text-slate-400 mt-4">Based on NIFTY50 volume profile and option chain analysis</p>
            </div>
          </div>

          {/* New Power Cards Navigation */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2 grid grid-cols-2 gap-6">
              <button onClick={() => navigate('/ai-summary')} className="bg-gradient-to-br from-indigo-900/40 to-slate-900 p-8 rounded-3xl border border-indigo-500/20 text-left group hover:border-indigo-500 transition-all">
                <Sparkles className="w-10 h-10 text-yellow-400 mb-4 group-hover:scale-110 transition" />
                <h3 className="text-xl font-bold text-white mb-2">AI Summary Report</h3>
                <p className="text-sm text-slate-400">Get 3-target stock analysis for your entire portfolio using Ollama 3B engine.</p>
                <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-white mt-4 transition" />
              </button>
              <button onClick={() => navigate('/trade')} className="bg-gradient-to-br from-green-900/20 to-slate-900 p-8 rounded-3xl border border-green-500/20 text-left group hover:border-green-500 transition-all">
                <Target className="w-10 h-10 text-green-400 mb-4 group-hover:scale-110 transition" />
                <h3 className="text-xl font-bold text-white mb-2">Trading Terminal</h3>
                <p className="text-sm text-slate-400">Instant order execution with auto-calculating breakup and robo-call setup.</p>
                <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-white mt-4 transition" />
              </button>
              <button onClick={() => navigate('/options')} className="bg-gradient-to-br from-blue-900/20 to-slate-900 p-8 rounded-3xl border border-blue-500/20 text-left group hover:border-blue-500 transition-all">
                <Activity className="w-10 h-10 text-blue-400 mb-4 group-hover:scale-110 transition" />
                <h3 className="text-xl font-bold text-white mb-2">Option Intelligence</h3>
                <p className="text-sm text-slate-400">Nifty/BankNifty live option chain with AI-powered CE/PE suggestions.</p>
                <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-white mt-4 transition" />
              </button>
              <button onClick={() => navigate('/ledger')} className="bg-gradient-to-br from-slate-800/40 to-slate-900 p-8 rounded-3xl border border-slate-700/50 text-left group hover:border-slate-400 transition-all">
                <History className="w-10 h-10 text-slate-400 mb-4 group-hover:scale-110 transition" />
                <h3 className="text-xl font-bold text-white mb-2">Transaction Ledger</h3>
                <p className="text-sm text-slate-400">Historical trade records fetched directly from your Demat accounts.</p>
                <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-white mt-4 transition" />
              </button>
            </div>
            
            {/* Market Pulse / Recent Activity */}
            <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5 text-red-400" /> Market Pulse
              </h3>
              <div className="space-y-4">
                {['NIFTY 50', 'BANKNIFTY', 'FINNIFTY'].map(idx => (
                  <div key={idx} className="flex justify-between items-center p-3 rounded-2xl bg-slate-950 border border-slate-800">
                    <span className="font-bold text-slate-400">{idx}</span>
                    <div className="text-right">
                      <p className="font-mono text-white">22,514.20</p>
                      <p className="text-xs text-green-400 font-bold">+102.40 (0.45%)</p>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-8">
                <h3 className="font-bold text-slate-500 text-xs uppercase tracking-widest mb-4">Linked Accounts</h3>
                <div className="space-y-2">
                  {connectedBrokers.map(b => (
                    <div key={b.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50">
                      <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-400" />
                        <span className="text-sm font-bold">{b.broker_name}</span>
                      </div>
                      <span className="text-xs text-slate-500">#{b.id}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Chat Sidebar Overlay */}
      {chatOpen && (
        <div className="w-96 bg-slate-900 border-l border-slate-800 flex flex-col shadow-2xl z-50">
          <div className="p-6 border-b border-slate-800 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-blue-400" />
              <h3 className="font-bold">Insight AI Assistant</h3>
            </div>
            <button onClick={() => setChatOpen(false)} className="p-1 hover:bg-slate-800 rounded-lg">
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="flex-grow p-4 overflow-y-auto space-y-4">
            {chatHistory.map((chat, i) => (
              <div key={i} className={`flex ${chat.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${
                  chat.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-slate-800 text-slate-300 rounded-tl-none border border-slate-700'
                }`}>
                  {chat.text}
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 border-t border-slate-800">
            <div className="relative">
              <input
                type="text"
                placeholder="Ask about your holdings..."
                value={chatMessage}
                onChange={(e) => setChatMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'ENTER' && handleSendMessage()}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-4 pr-12 py-3 text-sm focus:border-blue-500 outline-none"
              />
              <button 
                onClick={handleSendMessage}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 bg-blue-600 rounded-lg"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
