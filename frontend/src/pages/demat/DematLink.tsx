import React, { useState, useEffect } from 'react';
import { Wallet, Check, Trash2, Plus, X, ArrowLeft, Link2, RefreshCw, ExternalLink } from 'lucide-react';

interface DematAccount {
  id: string;
  broker_name: string;
  client_id: string;
  is_active: boolean;
  connected_at: string;
}

interface Broker {
  name: string;
  fields: string[];
  guide: string;
}

const BROKERS: Broker[] = [
  { name: 'Angel One', fields: ['SmartAPI Key', 'Client ID', 'Password', 'TOTP Secret'], guide: 'Visit smartapi.angelbroking.com to generate API keys.' },
  { name: 'Zerodha', fields: ['API Key', 'API Secret', 'Client ID', 'TOTP Secret'], guide: 'Go to kite.trade to create an app.' },
  { name: 'Groww', fields: ['API Key', 'API Secret'], guide: 'Check Settings > Trading APIs on Groww web.' },
  { name: 'Dhan', fields: ['Client ID', 'Access Token'], guide: 'Generate token at hq.dhan.co.' },
  { name: 'Upstox', fields: ['API Key', 'API Secret', 'Redirect URI'], guide: 'Create app at developer.upstox.com.' },
];

const DematLink: React.FC = () => {
  const [dematAccounts, setDematAccounts] = useState<DematAccount[]>([]);
  const [showBrokerSelect, setShowBrokerSelect] = useState(false);
  const [selectedBroker, setSelectedBroker] = useState<Broker | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchDematAccounts();
  }, []);

  const fetchDematAccounts = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/brokers/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      // Map brokers to demat account format
      const mappedAccounts = Array.isArray(data) ? data.map(broker => ({
        id: broker.id.toString(),
        broker_name: broker.broker_name,
        client_id: broker.credentials?.['Client ID'] || 'Unknown',
        is_active: broker.is_active,
        connected_at: new Date().toISOString() // Backend doesn't store this, using current date
      })) : [];
      setDematAccounts(mappedAccounts);
    } catch (err) {
      console.error('Failed to fetch demat accounts:', err);
    }
  };

  // handleAddDemat removed - broker linking is done via handleLinkBroker

  const handleLinkBroker = async () => {
    if (!selectedBroker || Object.keys(formData).length === 0) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/brokers/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          broker_name: selectedBroker.name,
          credentials: formData
        })
      });

      if (res.ok) {
        await fetchDematAccounts();
        setSelectedBroker(null);
        setFormData({});
        setShowBrokerSelect(false);
        setMessage({ type: 'success', text: `${selectedBroker.name} linked successfully!` });
      } else {
        setMessage({ type: 'error', text: `Failed to link ${selectedBroker.name}` });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Connection error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleActivateDemat = async (id: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/brokers/${id}/toggle`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        setDematAccounts(dematAccounts.map(a =>
          a.id === id ? { ...a, is_active: true } : a
        ));
        setMessage({ type: 'success', text: 'Demat account activated!' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to activate account' });
    }
  };

  const handleDeleteDemat = async (id: string) => {
    if (!confirm('Are you sure you want to unlink this demat account?')) return;

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`/api/brokers/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        setDematAccounts(dematAccounts.filter(a => a.id !== id));
        setMessage({ type: 'success', text: 'Demat account unlinked' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to unlink account' });
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => window.history.back()}
              className="p-2 hover:bg-slate-800 rounded-lg transition"
            >
              <ArrowLeft className="w-5 h-5 text-slate-400" />
            </button>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Link2 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Demat & Broker Linking</h1>
                <p className="text-xs text-slate-500">Connect your trading accounts</p>
              </div>
            </div>
          </div>
          <button
            onClick={() => setShowBrokerSelect(true)}
            className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg font-bold text-sm transition flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Link Broker
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-5xl mx-auto p-6">
        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-xl flex items-center gap-3 ${
            message.type === 'success'
              ? 'bg-green-900/30 border border-green-500/50 text-green-400'
              : 'bg-red-900/30 border border-red-500/50 text-red-400'
          }`}>
            {message.type === 'success' ? <Check className="w-5 h-5" /> : <X className="w-5 h-5" />}
            {message.text}
            <button onClick={() => setMessage(null)} className="ml-auto">
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-2">
              <Wallet className="w-5 h-5 text-blue-400" />
              <span className="text-slate-500 text-sm">Total Accounts</span>
            </div>
            <h3 className="text-3xl font-bold">{dematAccounts.length}</h3>
          </div>
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-2">
              <Check className="w-5 h-5 text-green-400" />
              <span className="text-slate-500 text-sm">Active</span>
            </div>
            <h3 className="text-3xl font-bold text-green-400">
              {dematAccounts.filter(a => a.is_active).length}
            </h3>
          </div>
          <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800">
            <div className="flex items-center gap-3 mb-2">
              <Link2 className="w-5 h-5 text-indigo-400" />
              <span className="text-slate-500 text-sm">Pending</span>
            </div>
            <h3 className="text-3xl font-bold text-indigo-400">
              {dematAccounts.filter(a => !a.is_active).length}
            </h3>
          </div>
        </div>

        {/* Broker Selection Panel */}
        {showBrokerSelect && (
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 mb-8">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Select Broker to Link</h2>
              <button onClick={() => { setShowBrokerSelect(false); setSelectedBroker(null); }} className="text-slate-500 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            {!selectedBroker ? (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {BROKERS.map(broker => (
                  <button
                    key={broker.name}
                    onClick={() => setSelectedBroker(broker)}
                    className="p-4 rounded-xl border border-slate-700 bg-slate-950 hover:border-blue-500 transition-all text-center"
                  >
                    <span className="font-bold text-white">{broker.name}</span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="bg-slate-950 p-6 rounded-xl border border-blue-500/30">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-blue-600 rounded-lg">
                    <Link2 className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-blue-400">{selectedBroker.name}</h3>
                    <p className="text-xs text-slate-500">Fill your credentials below</p>
                  </div>
                </div>

                <div className="space-y-4 mb-6">
                  {selectedBroker.fields.map(field => (
                    <div key={field}>
                      <label className="text-xs uppercase font-bold text-slate-500 mb-1 block">{field}</label>
                      <input
                        type="password"
                        value={formData[field] || ''}
                        onChange={(e) => setFormData({ ...formData, [field]: e.target.value })}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm focus:border-blue-500 outline-none text-white"
                        placeholder={`Enter ${field}`}
                      />
                    </div>
                  ))}
                </div>

                <div className="bg-blue-500/10 p-3 rounded-lg border border-blue-500/20 mb-6">
                  <p className="text-xs text-slate-400 flex items-start gap-2">
                    <ExternalLink className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    {selectedBroker.guide}
                  </p>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleLinkBroker}
                    disabled={loading}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 py-3 rounded-xl font-bold text-sm transition disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                    Link {selectedBroker.name}
                  </button>
                  <button
                    onClick={() => { setSelectedBroker(null); setFormData({}); }}
                    className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold text-sm transition"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Demat Accounts List */}
        <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
          <h2 className="text-xl font-bold text-white mb-6">Your Demat Accounts</h2>

          {dematAccounts.length === 0 ? (
            <div className="text-center py-12">
              <Wallet className="w-12 h-12 text-slate-700 mx-auto mb-4" />
              <p className="text-slate-500 mb-2">No demat accounts linked yet</p>
              <p className="text-xs text-slate-600">Click "Link Broker" to connect your trading account</p>
            </div>
          ) : (
            <div className="space-y-3">
              {dematAccounts.map(account => (
                <div
                  key={account.id}
                  className="flex items-center justify-between p-4 rounded-xl bg-slate-950 border border-slate-800"
                >
                  <div className="flex items-center gap-4">
                    <div className={`p-3 rounded-xl ${account.is_active ? 'bg-green-900/30' : 'bg-slate-800'}`}>
                      <Wallet className={`w-5 h-5 ${account.is_active ? 'text-green-400' : 'text-slate-500'}`} />
                    </div>
                    <div>
                      <p className="font-bold text-white">{account.broker_name}</p>
                      <p className="text-xs text-slate-500">Client ID: {account.client_id}</p>
                      <p className="text-xs text-slate-600">Added: {new Date(account.connected_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {account.is_active ? (
                      <span className="px-3 py-1 text-xs font-bold bg-green-500/20 text-green-400 rounded-full border border-green-500/30">
                        Active
                      </span>
                    ) : (
                      <button
                        onClick={() => handleActivateDemat(account.id)}
                        className="px-3 py-1 text-xs font-bold bg-blue-500/20 text-blue-400 rounded-full border border-blue-500/30 hover:bg-blue-500/40 transition"
                      >
                        Activate
                      </button>
                    )}
                    <button
                      onClick={() => handleDeleteDemat(account.id)}
                      className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DematLink;