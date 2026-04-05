import React, { useEffect, useState } from 'react';
import { Users, LogOut, LayoutDashboard, ShieldAlert, UserX, UserCheck, Search, Bell } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface User {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  last_login?: string;
}

const AdminDashboard: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users');
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleSuspend = async (userId: string) => {
    try {
      await api.post(`/admin/users/${userId}/suspend`);
      fetchUsers();
    } catch (err) {
      console.error('Failed to suspend user', err);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 flex items-center gap-3">
          <div className="p-2 bg-indigo-600 rounded">
            <ShieldAlert className="h-6 w-6 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">Admin Ops</span>
        </div>
        
        <nav className="flex-1 mt-6 px-4 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-2.5 bg-slate-800 text-indigo-400 rounded-lg transition-colors">
            <LayoutDashboard className="h-5 w-5" />
            <span className="font-medium">Dashboard</span>
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2.5 text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition-colors">
            <Users className="h-5 w-5" />
            <span className="font-medium">Users</span>
          </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button 
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-2 text-slate-400 hover:text-red-400 transition-colors"
          >
            <LogOut className="h-5 w-5" />
            <span>Terminate Session</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-slate-900 border-b border-slate-800 flex items-center justify-between px-8">
          <div className="relative w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search quant registry..." 
              className="w-full bg-slate-950 border border-slate-700 rounded-full pl-10 pr-4 py-2 text-sm focus:ring-1 focus:ring-indigo-500 transition-all"
            />
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-white transition-colors relative">
              <Bell className="h-5 w-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-indigo-500 rounded-full border-2 border-slate-900"></span>
            </button>
            <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-xs">
              AD
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <section className="flex-1 overflow-auto p-8">
          <div className="mb-8">
            <h1 className="text-2xl font-bold">Access Management</h1>
            <p className="text-slate-400 text-sm mt-1">Control system access and user status</p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-800/50">
                  <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-400 tracking-wider">User Identity</th>
                  <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-400 tracking-wider">Security Group</th>
                  <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-400 tracking-wider">Status</th>
                  <th className="px-6 py-4 text-xs font-semibold uppercase text-slate-400 tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {loading ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-slate-500 italic">
                      Synchronizing registry...
                    </td>
                  </tr>
                ) : users.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                      No active quant profiles found.
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex flex-col">
                          <span className="font-medium">{user.email}</span>
                          <span className="text-xs text-slate-500">ID: {user.id.substring(0, 8)}...</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs font-mono ${user.role === 'ADMIN' ? 'bg-indigo-900/40 text-indigo-300 border border-indigo-500/30' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                          {user.role}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className={`w-2 h-2 rounded-full ${user.is_active ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                          <span className="text-sm">{user.is_active ? 'Active' : 'Suspended'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleSuspend(user.id)}
                          disabled={user.role === 'ADMIN'}
                          className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${user.role === 'ADMIN' ? 'opacity-30 cursor-not-allowed text-slate-500' : 'hover:bg-red-900/20 text-red-400 hover:text-red-300'}`}
                          title={user.is_active ? "Suspend User" : "Activate User"}
                        >
                          {user.is_active ? <UserX className="h-4 w-4" /> : <UserCheck className="h-4 w-4" />}
                          {user.is_active ? 'Suspend' : 'Unsuspend'}
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>
    </div>
  );
};

export default AdminDashboard;
