import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { 
  BrowserRouter as Router, Routes, Route, Link, useNavigate, Navigate
} from 'react-router-dom'
import { 
  PieChart, ShieldCheck, LogIn, Plus, CheckCircle, TrendingUp, Zap, MessageSquare,
  ArrowRight, DollarSign, Clock, Download, Send, Bot, User as UserIcon, LogOut, Settings, 
  Bell, ChevronRight, Target, AlertTriangle, Activity, RefreshCw, Menu, X, ExternalLink,
  ShieldAlert, ChevronLeft, Check, Copy, Search, Info, History as HistoryIcon,
  TrendingDown, FileText, LayoutGrid, Receipt, User, Filter, SortAsc, ArrowUpDown
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const API = axios.create({ baseURL: '' })

// --- Route Guard ---
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('token'); if (!token) return <Navigate to="/login" replace />; return <>{children}</>
}

const LandingPage = () => {
  const token = localStorage.getItem('token'); if (token) return <Navigate to="/dashboard" replace />
  return (
    <div className="bg-[#020617] text-slate-100 min-h-screen font-sans">
      <nav className="fixed top-0 w-full z-50 bg-[#020617]/80 backdrop-blur-xl border-b border-slate-800/50 h-20 flex items-center justify-between px-6">
        <div className="flex items-center gap-3"><Zap className="w-8 h-8 text-blue-600" /><span className="text-2xl font-black uppercase tracking-widest">Alpha Engine</span></div>
        <div className="flex gap-6 font-bold"><Link to="/login">Sign In</Link><Link to="/register" className="bg-blue-600 px-6 py-2 rounded-xl">Start Free</Link></div>
      </nav>
      <header className="pt-48 pb-32 text-center px-6">
        <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-7xl md:text-9xl font-black mb-8 tracking-tighter">Alpha <span className="text-blue-600">Engine</span></motion.h1>
        <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-16 uppercase tracking-[0.3em] font-medium">Next-Gen Portfolio Automation</p>
        <Link to="/register" className="bg-blue-600 text-white px-12 py-6 rounded-3xl font-black text-xl shadow-2xl items-center gap-4 inline-flex transition-all hover:scale-105 active:scale-95 group">Initialize <ArrowRight /></Link>
      </header>
    </div>
  )
}

const AuthPage = ({ type }: { type: 'login' | 'register' }) => {
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [loading, setLoading] = useState(false); const [error, setError] = useState<string | null>(null); const navigate = useNavigate()
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError(null)
    try {
      if (type === 'register') await API.post('/api/register', { email, password })
      const params = new URLSearchParams(); params.append('username', email); params.append('password', password)
      const res = await API.post('/api/token', params, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      localStorage.setItem('token', res.data.access_token); localStorage.setItem('email', email); navigate('/dashboard')
    } catch (err: any) { setError('Access Denied. Check credentials.') } finally { setLoading(false) }
  }
  return (
    <div className="min-h-screen bg-[#020617] flex items-center justify-center p-6">
      <div className="bg-slate-900 border border-slate-800 p-10 rounded-[3rem] w-full max-w-md shadow-3xl text-center">
        <h1 className="text-3xl font-black mb-8 uppercase tracking-tighter">{type === 'register' ? 'Join Alpha' : 'Demat Access'}</h1>
        <form onSubmit={handleSubmit} className="space-y-6 text-left">
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-6 py-5 outline-none text-white font-mono focus:border-blue-600 transition-all" placeholder="Email" required />
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full bg-slate-950 border border-slate-800 rounded-2xl px-6 py-5 outline-none text-white font-mono focus:border-blue-600 transition-all" placeholder="Password" required />
          <button type="submit" disabled={loading} className="w-full bg-blue-600 py-6 rounded-2xl font-black text-xl shadow-2xl active:scale-95 transition-all">{loading ? 'Processing...' : (type === 'login' ? 'Authorize' : 'Initialize')}</button>
          {error && <div className="text-red-400 font-bold text-center mt-4 p-3 bg-red-400/10 rounded-xl">{error}</div>}
        </form>
        <p className="mt-8 text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em]">{type === 'login' ? "New Terminal? " : "Active? "}<Link to={type === 'login' ? "/register" : "/login"} className="text-blue-500 underline underline-offset-4">{type === 'login' ? "Register" : "Login"}</Link></p>
      </div>
    </div>
  )
}

const Dashboard = () => {
  const [subscription, setSubscription] = useState<any>(null); const [summary, setSummary] = useState<any>(null); const [loading, setLoading] = useState(false); const [history, setHistory] = useState<any[]>([])
  const [analyzing, setAnalyzing] = useState<string | null>(null); const [shareAnalysis, setShareAnalysis] = useState<any>(null); const [tradingShare, setTradingShare] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'portfolio' | 'history' | 'chat' | 'settings' | 'report' | 'profile'>((sessionStorage.getItem('activeTab') as any) || 'portfolio')
  const [sidebarOpen, setSidebarOpen] = useState(false); const [selectedBroker, setSelectedBroker] = useState<string | null>(null)
  const navigate = useNavigate(); const email = localStorage.getItem('email'); const token = localStorage.getItem('token')
  const [apiKey, setApiKey] = useState(sessionStorage.getItem('apiKey') || ''); const [clientCode, setClientCode] = useState(sessionStorage.getItem('clientCode') || ''); const [pin, setPin] = useState(sessionStorage.getItem('pin') || ''); const [totpSecret, setTotpSecret] = useState(sessionStorage.getItem('totpSecret') || '')
  const [connecting, setConnecting] = useState(false); const [chatInput, setChatInput] = useState(''); const [messages, setMessages] = useState<any[]>([{ role: 'assistant', content: "Alpha Engine Active." }]); const chatEndRef = useRef<HTMLDivElement>(null)

  const [profileEmail, setProfileEmail] = useState(''); const [profileTelegram, setProfileTelegram] = useState(''); const [savingProfile, setSavingProfile] = useState(false)
  const [tradeQty, setTradeQty] = useState(1); const [executing, setExecuting] = useState(false)
  const [searchTerm, setSearchBar] = useState('')
  const [sortBy, setSortBy] = useState<'symbol' | 'pnl' | 'value'>('pnl')

  useEffect(() => {
    sessionStorage.setItem('activeTab', activeTab); sessionStorage.setItem('apiKey', apiKey); sessionStorage.setItem('clientCode', clientCode); sessionStorage.setItem('pin', pin); sessionStorage.setItem('totpSecret', totpSecret)
  }, [activeTab, apiKey, clientCode, pin, totpSecret])

  const fetchWithAuth = async (url: string, method: 'get' | 'post' = 'get', data?: any) => {
    if (!token) return navigate('/login'); return API({ url, method, data, headers: { Authorization: `Bearer ${token}` }})
  }

  const handleSync = async () => {
    setLoading(true); try { const res = await fetchWithAuth('/api/portfolio/sync', 'post'); if (res) setSummary(res.data) } catch (err) {} setLoading(false)
  }

  const handleAnalyzeShare = async (symbol: string) => {
    setAnalyzing(symbol); try { const res = await fetchWithAuth(`/api/portfolio/analyze-share?symbol=${symbol}`, 'post'); if (res?.data?.processing) { alert(res.data.message); } else if (res) { setShareAnalysis(res.data); } } catch (err: any) { alert(err.response?.data?.detail || 'Limit Reached') } setAnalyzing(null)
  }

  const handleExecuteTrade = async (symbol: string, target: number, sl: number) => {
    setExecuting(true); try { const res = await fetchWithAuth(`/api/trade/robo?symbol=${symbol}&qty=${tradeQty}&target=${target}&sl=${sl}`, 'post'); if (res) { alert(`Deployed: ${res.data.message}\nNet: ₹${res.data.breakup.net}`); setTradingShare(null); fetchHistory() } } catch (err: any) { alert('Execution Failed') } setExecuting(false)
  }

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault(); setSavingProfile(true); try { await fetchWithAuth('/api/profile/verify', 'post', { email: profileEmail, telegram_id: profileTelegram }); alert('Notifications Verified!'); fetchStatus() } catch (err) {} setSavingProfile(false)
  }

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault(); setConnecting(true); try { await fetchWithAuth('/api/connect/angelone', 'post', { api_key: apiKey, client_code: clientCode, pin, totp_secret: totpSecret }); sessionStorage.clear(); alert('Linked!'); setActiveTab('portfolio'); await handleSync() } catch (err: any) { alert('Link Failed') } finally { setConnecting(false) }
  }

  const handleSendMessage = async (e: any) => {
    e.preventDefault(); if (!chatInput.trim()) return; const msg = chatInput; setChatInput(''); setMessages(prev => [...prev, { role: 'user', content: msg }])
    try { const res = await fetchWithAuth(`/api/chat?message=${encodeURIComponent(msg)}`, 'post'); if (res) setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]) } catch (err) {}
  }

  const fetchStatus = () => fetchWithAuth('/api/subscription/status').then(res => { if (res) { setSubscription(res.data); setProfileEmail(res.data.email); setProfileTelegram(res.data.telegram_id || '') } })
  const fetchHistory = () => fetchWithAuth('/api/portfolio/history').then(res => { if (res) setHistory(res.data) })

  useEffect(() => {
    if (!token) return navigate('/login')
    fetchWithAuth('/api/portfolio/summarize').then(res => { if (res?.data?.sync_required) handleSync(); else setSummary(res?.data) })
    fetchStatus(); fetchHistory()
  }, [activeTab])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const calculateCharges = (val: number) => {
    const total = (val * 0.0015) + 15.93; return { total }
  }

  const filteredHoldings = summary?.holdings?.filter((h: any) => h.tradingsymbol.toLowerCase().includes(searchTerm.toLowerCase())).sort((a: any, b: any) => {
    if (sortBy === 'symbol') return a.tradingsymbol.localeCompare(b.tradingsymbol)
    if (sortBy === 'pnl') return b.pnl - a.pnl
    if (sortBy === 'value') return b.current_value - a.current_value
    return 0
  })

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 flex flex-col md:flex-row overflow-hidden font-sans">
      <aside className={`fixed md:relative inset-0 z-40 w-full md:w-80 bg-slate-950 border-r border-slate-800 p-8 flex flex-col transition-transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        <div className="flex items-center gap-3 mb-16"><Zap className="w-8 h-8 text-blue-600" /><span className="text-xl font-black uppercase tracking-widest text-white">Alpha Engine</span></div>
        <nav className="flex-1 space-y-2">
          <button onClick={() => {setActiveTab('portfolio'); setSidebarOpen(false)}} className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl transition-all ${activeTab === 'portfolio' ? 'bg-blue-600 text-white shadow-xl' : 'text-slate-500 hover:bg-slate-900'}`}><PieChart size={18}/> Portfolio</button>
          <button onClick={() => {setActiveTab('report'); setSidebarOpen(false)}} className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl transition-all ${activeTab === 'report' ? 'bg-blue-600 text-white shadow-xl' : 'text-slate-500 hover:bg-slate-900'}`}><FileText size={18}/> AI Report</button>
          <button onClick={() => {setActiveTab('history'); setSidebarOpen(false)}} className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl transition-all ${activeTab === 'history' ? 'bg-blue-600 text-white shadow-xl' : 'text-slate-500 hover:bg-slate-900'}`}><HistoryIcon size={18}/> Trade Logs</button>
          <button onClick={() => {setActiveTab('chat'); setSidebarOpen(false)}} className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl transition-all ${activeTab === 'chat' ? 'bg-blue-600 text-white shadow-xl' : 'text-slate-500 hover:bg-slate-900'}`}><MessageSquare size={18}/> Chat</button>
          <button onClick={() => {setActiveTab('profile'); setSidebarOpen(false)}} className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl transition-all ${activeTab === 'profile' ? 'bg-blue-600 text-white shadow-xl' : 'text-slate-500 hover:bg-slate-900'}`}><User size={18}/> Profile</button>
          <button onClick={() => {setActiveTab('settings'); setSidebarOpen(false)}} className={`w-full flex items-center gap-4 px-6 py-4 rounded-xl transition-all ${activeTab === 'settings' ? 'bg-blue-600 text-white shadow-xl' : 'text-slate-500 hover:bg-slate-900'}`}><Settings size={18}/> Connection</button>
        </nav>
        <button onClick={() => { localStorage.clear(); navigate('/') }} className="mt-auto py-4 text-xs font-black text-slate-600 hover:text-red-400 flex items-center justify-center gap-2"><LogOut size={14} /> LOGOUT</button>
      </aside>

      <main className="flex-1 h-screen flex flex-col relative overflow-hidden">
        <header className="h-20 px-8 border-b border-slate-800 bg-slate-950/50 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-6">
             <div className="font-black text-slate-500 uppercase tracking-widest text-[9px] flex items-center gap-3"><div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"/> Live Session</div>
             <div className="hidden lg:flex items-center gap-2 text-slate-600 font-bold text-[10px] uppercase border-l border-slate-800 pl-6"><Clock size={12}/> {new Date().toLocaleTimeString()}</div>
          </div>
          <button onClick={() => setSidebarOpen(true)} className="md:hidden p-3 bg-slate-900 rounded-xl"><Menu/></button>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-12 scrollbar-hide pb-32">
          <AnimatePresence mode="wait">
            {activeTab === 'portfolio' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-10 max-w-7xl mx-auto">
                {summary?.connected ? (
                  <div className="space-y-10">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                       <div className="space-y-4">
                          <h2 className="text-4xl md:text-5xl font-black uppercase text-white tracking-tighter">Holdings</h2>
                          <div className="flex flex-wrap gap-4 uppercase text-[10px] font-black tracking-widest">
                             <div className="bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">Invested: <span className="text-blue-400 ml-1">₹{summary.invested_value?.toLocaleString()}</span></div>
                             <div className="bg-slate-900 px-4 py-2 rounded-xl border border-slate-800">Total P&L: <span className={`${summary.total_value >= summary.invested_value ? 'text-green-500' : 'text-red-500'} ml-1`}>{summary.total_value >= summary.invested_value ? '+' : ''}₹{(summary.total_value - summary.invested_value).toLocaleString()}</span></div>
                          </div>
                       </div>
                       <button onClick={handleSync} disabled={loading} className="bg-blue-600 px-10 py-4 rounded-3xl font-black text-[10px] tracking-widest uppercase flex items-center gap-3 active:scale-95 shadow-2xl transition-all"><RefreshCw size={14} className={loading ? 'animate-spin' : ''}/> Sync</button>
                    </div>

                    <div className="bg-slate-900/30 p-4 rounded-3xl border border-slate-800 flex flex-col md:flex-row gap-4 items-center justify-between">
                       <div className="relative w-full md:w-96">
                          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={16}/>
                          <input type="text" value={searchTerm} onChange={(e) => setSearchBar(e.target.value)} placeholder="Search identifier..." className="w-full bg-[#020617] border border-slate-800 rounded-2xl py-3 pl-12 pr-4 outline-none text-white font-bold text-sm" />
                       </div>
                       <div className="flex gap-2 w-full md:w-auto">
                          <button onClick={() => setSortBy('pnl')} className={`flex-1 md:flex-none px-4 py-3 rounded-2xl font-black text-[9px] uppercase border transition-all ${sortBy === 'pnl' ? 'bg-blue-600 border-blue-600 text-white' : 'bg-slate-950 border-slate-800 text-slate-500'}`}>Sort by Profit</button>
                          <button onClick={() => setSortBy('value')} className={`flex-1 md:flex-none px-4 py-3 rounded-2xl font-black text-[9px] uppercase border transition-all ${sortBy === 'value' ? 'bg-blue-600 border-blue-600 text-white' : 'bg-slate-950 border-slate-800 text-slate-500'}`}>Sort by Value</button>
                       </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
                       {filteredHoldings?.map((h: any) => (
                         <div key={h.tradingsymbol} className="bg-slate-900/50 border border-slate-800 p-6 md:p-10 rounded-[3rem] transition-all hover:border-blue-600 shadow-xl group relative overflow-hidden">
                            <div className="flex justify-between items-start mb-8 border-b border-slate-800 pb-8 relative z-10">
                               <div className="flex items-start gap-4">
                                  <div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center font-black text-white text-xl">{h.tradingsymbol.charAt(0)}</div>
                                  <div><div className="text-2xl font-black text-white">{h.tradingsymbol}</div><div className="text-xl font-bold text-white mt-1 uppercase tracking-tighter">₹{h.ltp}</div></div>
                               </div>
                               <div className="text-right">
                                  <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Live Profit/Loss</div>
                                  <div className={`text-3xl font-black tracking-tighter ${h.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>{h.pnl >= 0 ? '+' : ''}₹{h.pnl.toLocaleString()}</div>
                                  <div className={`text-[10px] font-bold mt-1 ${h.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>{h.pnlpercentage}% Growth</div>
                               </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 md:gap-6 mb-10 relative z-10">
                               <div className="bg-[#020617] p-6 rounded-[2rem] border border-slate-800/50"><div className="text-[9px] text-slate-500 font-black uppercase mb-2">Buy Average</div><div className="text-xl font-black text-blue-400 font-mono tracking-tighter">₹{h.averageprice?.toLocaleString()}</div><div className="text-[10px] text-slate-600 font-bold mt-1">{h.quantity} Shares</div></div>
                               <div className="bg-[#020617] p-6 rounded-[2rem] border border-slate-800/50"><div className="text-[9px] text-slate-500 font-black uppercase mb-2">Current Val</div><div className={`text-xl font-black font-mono tracking-tighter ${h.ltp >= h.averageprice ? 'text-green-500' : 'text-red-500'}`}>₹{h.current_value?.toLocaleString()}</div><div className="text-[10px] text-slate-600 font-bold mt-1 uppercase tracking-tighter">Live Status</div></div>
                            </div>
                            <div className="grid grid-cols-2 gap-4 mb-10 border-t border-slate-800 pt-8 relative z-10 text-center">
                               <div><div className="text-[9px] font-black text-green-500 uppercase tracking-widest mb-1">AI Target</div><div className="text-2xl font-black text-green-400 uppercase tracking-tighter font-mono">₹{h.target}</div></div>
                               <div><div className="text-[9px] font-black text-red-500 uppercase tracking-widest mb-1">Stop Loss</div><div className="text-2xl font-black text-red-400 uppercase tracking-tighter font-mono">₹{h.sl}</div></div>
                            </div>
                            <div className="flex gap-4 relative z-10"><button onClick={() => {setTradingShare(h); setTradeQty(1)}} className="flex-1 bg-blue-600 hover:bg-blue-500 py-6 rounded-3xl font-black text-[11px] uppercase shadow-lg active:scale-95 transition-all">Robo Trade</button><button onClick={() => {handleAnalyzeShare(h.tradingsymbol); setActiveTab('report')}} className="flex-1 bg-slate-800 hover:bg-slate-700 py-6 rounded-3xl font-black text-[11px] uppercase active:scale-95 transition-all text-slate-400">Research</button></div>
                         </div>
                       ))}
                    </div>
                  </div>
                ) : (
                  <div className="h-[60vh] border-4 border-dashed border-slate-800 rounded-[3rem] flex flex-col items-center justify-center text-center p-10 bg-slate-900/20 shadow-3xl"><ShieldAlert className="w-24 h-24 text-red-900/10 mb-8" /><h2 className="text-4xl font-black text-slate-400 mb-12 uppercase tracking-tighter">Engine Restricted</h2><button onClick={() => setActiveTab('settings')} className="bg-white text-black px-16 py-6 rounded-3xl font-black uppercase text-lg hover:bg-blue-600 hover:text-white active:scale-95 transition-all">Establish Link</button></div>
                )}
              </motion.div>
            )}

            {activeTab === 'profile' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto w-full pb-20">
                 <div className="bg-slate-900/50 border border-slate-800 rounded-[4rem] p-10 md:p-16 shadow-3xl">
                    <div className="flex items-center gap-6 mb-16"><div className="w-20 h-20 bg-blue-600 rounded-3xl flex items-center justify-center shadow-2xl"><Bell className="w-10 h-10 text-white" /></div><div><h2 className="text-5xl font-black uppercase text-white tracking-tighter">Alert Protocol</h2><p className="text-slate-500 text-[10px] font-black uppercase tracking-[0.4em] mt-2 italic">Automated Trade & AI Monitoring</p></div></div>
                    <form onSubmit={handleUpdateProfile} className="space-y-12 text-left">
                       <div className="space-y-4"><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-4 flex items-center gap-3">Notification Email {subscription?.is_email_verified && <CheckCircle size={14} className="text-green-500 shadow-lg"/>}</label><input type="email" value={profileEmail} onChange={(e) => setProfileEmail(e.target.value)} className="w-full bg-[#020617] border border-slate-800 rounded-[2.5rem] px-10 py-8 outline-none text-white font-mono shadow-inner focus:border-blue-600 transition-all text-xl" required /></div>
                       <div className="space-y-4"><label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-4 flex items-center gap-3">Telegram ID {subscription?.is_telegram_verified && <CheckCircle size={14} className="text-green-500 shadow-lg"/>}</label><input type="text" value={profileTelegram} onChange={(e) => setProfileTelegram(e.target.value)} className="w-full bg-[#020617] border border-slate-800 rounded-[2.5rem] px-10 py-8 outline-none text-white font-mono shadow-inner focus:border-blue-600 transition-all text-xl" required /></div>
                       <div className="bg-blue-600/5 border border-blue-600/20 p-10 rounded-[3rem] shadow-xl"><p className="text-[11px] font-black text-blue-400 uppercase tracking-[0.2em] leading-relaxed">System linked to Bot @VJInsightbot. All trade logs and daily AI portfolio health reports (Market Open/Close) will be routed through these verified channels.</p></div>
                       <button type="submit" disabled={savingProfile} className="w-full bg-white text-black hover:bg-blue-600 hover:text-white py-10 rounded-[3rem] font-black text-2xl shadow-3xl active:scale-95 transition-all uppercase tracking-[0.3em]">{savingProfile ? 'CONFIGURING...' : 'Authorize Notifications'}</button>
                    </form>
                 </div>
              </motion.div>
            )}

            {/* Other tabs follow same premium design pattern... */}
            {activeTab === 'report' && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-12 max-w-7xl mx-auto pb-20">
                 <div className="flex justify-between items-end gap-6 mb-12 border-b border-slate-800 pb-8"><h2 className="text-4xl font-black uppercase text-white tracking-tighter">Research deck</h2><button onClick={() => setActiveTab('portfolio')} className="bg-slate-800 px-8 py-3 rounded-2xl font-black text-[10px] uppercase tracking-widest flex items-center gap-2 active:scale-95 transition-all"><ChevronLeft size={14}/> Dashboard</button></div>
                 {summary?.holdings.map((h: any) => (
                   <div key={h.tradingsymbol} className="bg-slate-900/50 border border-slate-800 rounded-[3rem] p-8 md:p-12 mb-10 shadow-3xl relative overflow-hidden">
                      <div className="flex flex-col lg:flex-row gap-12">
                         <div className="lg:w-1/3 space-y-8 shrink-0">
                            <div className="flex items-center gap-4"><div className="w-14 h-14 bg-blue-600 rounded-2xl flex items-center justify-center font-black text-2xl text-white shadow-2xl">{h.tradingsymbol.charAt(0)}</div><div><h3 className="text-3xl font-black text-white tracking-tighter uppercase">{h.tradingsymbol}</h3><p className="text-slate-500 font-black text-[9px] uppercase tracking-widest">{h.exchange} • Equity</p></div></div>
                            <div className="space-y-4 bg-[#020617] p-8 rounded-[2rem] border border-slate-800 shadow-inner">
                               <div className="flex justify-between border-b border-slate-800 pb-4 text-[10px] font-black"><span className="text-slate-500 uppercase">Avg cost</span><span className="text-white font-mono">₹{h.averageprice}</span></div>
                               <div className="flex justify-between border-b border-slate-800 pb-4 text-[10px] font-black"><span className="text-slate-500 uppercase">Current</span><span className="text-white font-mono">₹{h.ltp}</span></div>
                               <div className="flex justify-between pt-2 text-[10px] font-black"><span className="text-slate-500 uppercase">Growth</span><span className={`px-2 py-1 rounded-lg ${h.pnl >= 0 ? 'bg-green-900/20 text-green-500' : 'bg-red-900/20 text-red-500'}`}>{h.pnlpercentage}%</span></div>
                            </div>
                         </div>
                         <div className="flex-1 space-y-8">
                            <div className="bg-blue-600/5 border border-blue-600/20 p-10 rounded-[2.5rem] relative shadow-lg">
                               <div className="flex justify-between items-center mb-6"><h4 className="text-xl font-black uppercase tracking-tighter flex items-center gap-3 text-blue-500"><LayoutGrid size={20}/> AI Core Research Report</h4><button onClick={() => handleAnalyzeShare(h.tradingsymbol)} disabled={analyzing === h.tradingsymbol} className="bg-blue-600 text-white px-8 py-3 rounded-full text-[10px] font-black uppercase tracking-widest flex items-center gap-3 shadow-lg active:scale-95 transition-all">{analyzing === h.tradingsymbol ? <RefreshCw size={14} className="animate-spin"/> : <RefreshCw size={14}/>} Refresh AI</button></div>
                               <div className="text-base text-slate-300 leading-relaxed font-semibold whitespace-pre-wrap">{shareAnalysis?.symbol === h.tradingsymbol ? shareAnalysis.analysis : (h.ai_analysis || "Activate AI core for latest technical outlook.")}</div>
                            </div>
                            <div className="grid grid-cols-2 gap-8">
                               <div className="bg-[#020617] border border-slate-800 p-8 rounded-[2rem] shadow-inner text-center"><h5 className="text-[10px] font-black text-green-500 uppercase tracking-widest mb-2 font-bold">Target</h5><div className="text-3xl font-black text-green-400 font-mono">₹{h.target}</div></div>
                               <div className="bg-[#020617] border border-slate-800 p-8 rounded-[2rem] shadow-inner text-center"><h5 className="text-[10px] font-black text-red-500 uppercase tracking-widest mb-2 font-bold">Stop Loss</h5><div className="text-3xl font-black text-red-400 font-mono">₹{h.sl}</div></div>
                            </div>
                         </div>
                      </div>
                   </div>
                 ))}
              </motion.div>
            )}

            {/* History tab design... */}
            {activeTab === 'history' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-10 max-w-7xl mx-auto pb-20">
                 <h2 className="text-5xl font-black tracking-tighter uppercase text-white">System logs</h2>
                 <div className="bg-slate-900 border border-slate-800 rounded-[3rem] overflow-hidden shadow-3xl">
                    <div className="overflow-x-auto"><table className="w-full text-left font-bold"><thead className="bg-[#020617] border-b border-slate-800 uppercase tracking-widest text-[9px] text-slate-500"><tr><th className="px-10 py-10">Timestamp</th><th className="px-10 py-10">Asset</th><th className="px-10 py-10">Protocol</th><th className="px-10 py-10">Price Point</th><th className="px-10 py-10">Reference</th></tr></thead><tbody>{history.map((t: any) => (<tr key={t.id} className="border-b border-slate-800/50 hover:bg-blue-600/5 transition-all"><td className="px-10 py-8 text-slate-400 font-mono text-xs font-medium">{new Date(t.timestamp).toLocaleString()}</td><td className="px-10 py-8 text-white uppercase text-xl tracking-tighter">{t.symbol}</td><td className="px-10 py-8"><span className={`px-4 py-2 rounded-xl text-[9px] font-black border ${t.transaction_type.includes('BUY') ? 'bg-green-900/10 text-green-500 border-green-500/20' : 'bg-red-900/10 text-red-500 border-red-500/20'}`}>{t.transaction_type}</span></td><td className="px-10 py-8 text-blue-400 font-mono text-lg tracking-tighter">₹{t.price || 'Market'}</td><td className="px-10 py-8 text-[9px] text-slate-600 font-mono uppercase tracking-widest">{t.order_id}</td></tr>))}{history.length === 0 && (<tr><td colSpan={5} className="px-10 py-32 text-center text-slate-700 font-black uppercase text-xs tracking-[0.5em] italic">Archive sequence null.</td></tr>)}</tbody></table></div>
                 </div>
              </motion.div>
            )}

            {/* Connection settings tab design... */}
            {activeTab === 'settings' && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="max-w-5xl mx-auto w-full pb-20">
                 {!selectedBroker ? (
                   <div className="space-y-12 text-center"><h2 className="text-6xl font-black uppercase text-white tracking-tighter">Demat Gate Link</h2><div className="grid md:grid-cols-2 gap-10"><button onClick={() => setSelectedBroker('angelone')} className="bg-slate-900 border-2 border-slate-800 p-12 rounded-[4rem] text-left hover:border-blue-600 transition-all group flex flex-col justify-between h-80 shadow-3xl relative overflow-hidden active:scale-95"><div className="z-10"><div className="text-4xl font-black mb-3 text-white uppercase tracking-tighter font-mono">Angel One</div><p className="text-slate-500 font-black text-[10px] tracking-[0.3em] uppercase opacity-70 italic">SmartAPI v2.0 Protocol</p></div><div className="z-10 flex items-center text-blue-500 font-black uppercase text-sm tracking-[0.2em] gap-3 group-hover:gap-5 transition-all">Establish Live Link <ArrowRight size={20} className="group-hover:translate-x-3 transition-transform" /></div><div className="absolute -right-20 -bottom-20 w-80 h-80 bg-blue-600/10 rounded-full blur-[120px]"/></button></div></div>
                 ) : (
                   <div className="bg-slate-900 border border-slate-800 rounded-[4rem] p-16 shadow-3xl relative overflow-hidden text-left"><button onClick={() => setSelectedBroker(null)} className="mb-12 text-slate-500 font-black flex items-center gap-3 hover:text-white transition-all uppercase text-[10px] tracking-[0.4em] active:scale-95 shadow-lg"><ChevronLeft size={16}/> Back</button><h2 className="text-6xl font-black tracking-tighter mb-4 uppercase text-white text-center">Authorization</h2><form onSubmit={handleConnect} className="space-y-12"><div className="grid md:grid-cols-2 gap-12"><div className="space-y-5"><label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] px-4">SmartAPI Key</label><input type="text" value={apiKey} onChange={(e) => setApiKey(e.target.value)} className="w-full bg-[#020617] border border-slate-800 rounded-[2rem] px-10 py-8 outline-none text-white font-mono text-base focus:border-blue-600 transition-all shadow-inner shadow-black" placeholder="Key" required /></div><div className="space-y-5"><label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] px-4">UserID</label><input type="text" value={clientCode} onChange={(e) => setClientCode(e.target.value)} className="w-full bg-[#020617] border border-slate-800 rounded-[2rem] px-10 py-8 outline-none text-white font-mono text-base focus:border-blue-600 transition-all shadow-inner shadow-black" placeholder="ID" required /></div></div><div className="grid md:grid-cols-2 gap-12"><div className="space-y-5"><label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] px-4">Trading Security PIN</label><input type="password" value={pin} onChange={(e) => setPin(e.target.value)} className="w-full bg-[#020617] border border-slate-800 rounded-[2rem] px-10 py-8 outline-none text-white font-mono text-base focus:border-blue-600 transition-all shadow-inner shadow-black" placeholder="••••" required /></div><div className="space-y-5"><label className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] px-4">TOTP Key</label><input type="text" value={totpSecret} onChange={(e) => setTotpSecret(e.target.value)} className="w-full bg-[#020617] border border-slate-800 rounded-[2rem] px-10 py-8 outline-none text-white font-mono text-base focus:border-blue-600 transition-all shadow-inner shadow-black" placeholder="Auth" required /></div></div><button type="submit" disabled={connecting} className="w-full bg-white text-black hover:bg-blue-600 hover:text-white py-10 rounded-[3rem] font-black text-2xl shadow-3xl transition-all uppercase transform active:scale-95 flex items-center justify-center gap-6">{connecting ? <RefreshCw className="w-10 h-10 animate-spin" /> : 'Confirm Live Auth'}</button></form></div>
                 )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* Robo Trade Modal */}
      <AnimatePresence>
        {tradingShare && (
          <div className="fixed inset-0 z-[100] flex items-end md:items-center justify-center p-2 md:p-6 backdrop-blur-[40px] bg-black/80 font-sans">
            <motion.div initial={{ y: "100%", opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: "100%", opacity: 0 }} className="bg-slate-950 border border-slate-800 p-6 md:p-12 rounded-t-[4rem] md:rounded-[5rem] max-w-2xl w-full shadow-[0_0_150px_rgba(37,99,235,0.2)] relative overflow-hidden max-h-[95vh] flex flex-col">
               <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-blue-600/5 blur-[120px] -z-10"/>
               
               <div className="overflow-y-auto pr-2 scrollbar-hide flex-1 pb-10">
                  <div className="flex items-center gap-6 mb-10"><div className="w-16 h-16 bg-blue-600 rounded-[1.5rem] flex items-center justify-center shadow-2xl shadow-blue-600/40"><Zap className="w-10 h-10 text-white"/></div><div><h3 className="text-4xl md:text-5xl font-black uppercase tracking-tighter text-white uppercase">Robo Alpha</h3><p className="text-slate-500 font-black uppercase text-[10px] tracking-[0.5em] mt-2 italic">Execution Engine Active</p></div></div>
                  
                  <div className="bg-slate-900/50 p-8 md:p-12 rounded-[3rem] md:rounded-[4rem] border border-slate-800 mb-10 shadow-inner">
                     <div className="flex justify-between items-center mb-12 border-b border-slate-800 pb-8"><div><span className="text-4xl md:text-5xl font-black tracking-tighter text-white uppercase">{tradingShare.tradingsymbol}</span><div className="text-slate-500 font-black uppercase text-[10px] tracking-widest mt-2">Listing: NSE Protocol</div></div><span className="text-3xl md:text-4xl font-black text-blue-500 tracking-tighter font-mono uppercase">₹{tradingShare.ltp}</span></div>
                     
                     <div className="space-y-12">
                        <div className="space-y-6"><div className="flex justify-between items-end px-2"><label className="text-[11px] font-black text-slate-500 uppercase tracking-widest px-4">Execute Units</label><span className="text-white font-black text-3xl font-mono">{tradeQty}</span></div><input type="range" min="1" max={tradingShare.quantity} value={tradeQty} onChange={(e) => setTradeQty(parseInt(e.target.value))} className="w-full h-4 bg-slate-800 rounded-2xl appearance-none cursor-pointer accent-blue-600 shadow-inner" /></div>
                        
                        <div className="grid grid-cols-2 gap-8 text-center pt-4"><div className="space-y-4"><label className="text-[10px] font-black text-green-500 uppercase tracking-[0.4em]">Target Price</label><div className="text-3xl md:text-4xl font-black text-green-400 bg-green-400/5 py-8 rounded-[2.5rem] border border-green-400/10 shadow-lg font-mono">₹{tradingShare.target}</div></div><div className="space-y-4"><label className="text-[10px] font-black text-red-500 uppercase tracking-[0.4em]">Stop Loss</label><div className="text-3xl md:text-4xl font-black text-red-400 bg-red-400/5 py-8 rounded-[2.5rem] border border-red-400/10 shadow-lg font-mono">₹{tradingShare.sl}</div></div></div>
                     </div>
                  </div>

                  <div className="bg-[#020617] border border-slate-800 rounded-[3rem] p-10 mb-10 shadow-inner shadow-black"><h4 className="text-[11px] font-black text-slate-500 uppercase tracking-[0.3em] mb-8 flex items-center gap-3 font-bold uppercase"><Receipt size={18} className="text-blue-500"/> Settlement Analysis</h4><div className="space-y-6 font-black uppercase text-[10px]"><div className="flex justify-between items-center"><span className="text-slate-500">Gross Sale Value</span><span className="text-white font-mono text-base tracking-tighter">₹{(tradeQty * tradingShare.ltp).toLocaleString()}</span></div><div className="flex justify-between items-center"><span className="text-slate-500">Tax & Charges (Est)</span><span className="text-red-500 font-mono text-base tracking-tighter">- ₹{calculateCharges(tradeQty * tradingShare.ltp).total.toFixed(2)}</span></div><div className="flex justify-between items-center border-t border-slate-800 pt-6"><span className="text-blue-500 font-black tracking-widest text-sm">Net Receivable</span><span className="text-blue-400 font-black text-3xl tracking-tighter font-mono">₹{(tradeQty * tradingShare.ltp - calculateCharges(tradeQty * tradingShare.ltp).total).toLocaleString()}</span></div></div></div>
               </div>

               <div className="flex gap-6 md:gap-10 pt-6 border-t border-slate-800 shrink-0"><button onClick={() => setTradingShare(null)} className="flex-1 py-8 bg-slate-900 border border-slate-800 rounded-[2.5rem] font-black uppercase text-xs tracking-[0.4em] text-slate-500 transition-all hover:text-white active:scale-95 shadow-xl">Abort</button><button onClick={() => handleExecuteTrade(tradingShare.tradingsymbol, tradingShare.target, tradingShare.sl)} disabled={executing} className="flex-1 py-8 bg-blue-600 shadow-[0_20px_60px_rgba(37,99,235,0.4)] rounded-[2.5rem] font-black uppercase text-xs tracking-[0.4em] text-white transition-all hover:bg-blue-500 active:scale-95 transform hover:-translate-y-1 flex items-center justify-center gap-4"><Shield size={20}/> {executing ? 'DEPLOYING...' : 'Confirm Order'}</button></div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<LandingPage />} /><Route path="/login" element={<AuthPage type="login" />} /><Route path="/register" element={<AuthPage type="register" />} /><Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} /><Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  </Router>
)

export default App
