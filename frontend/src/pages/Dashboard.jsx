import React from 'react';
import { NavLink, Link } from 'react-router-dom'; // Added Link and NavLink
import { 
  Wallet, 
  Users, 
  TrendingUp, 
  ArrowUpRight, 
  Plus, 
  Award,
  RefreshCw,
  LayoutDashboard,
  History,
  ArrowRight
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const Dashboard = () => {
  // Mock Data
  const balances = { algo: "1,240.50", inr: "85,400.00" };
  const categories = [
    { name: 'Food', value: 400, color: '#6366f1' },
    { name: 'Travel', value: 300, color: '#818cf8' },
    { name: 'Shopping', value: 300, color: '#a5b4fc' },
    { name: 'Utility', value: 200, color: '#c7d2fe' },
  ];

  const recentExpenses = [
    { id: 1, title: 'Dinner with Team', group: 'Office Crew', amount: '- ₹1,200', date: 'Today' },
    { id: 2, title: 'Gas Bill', group: 'Flatmates', amount: '- ₹450', date: 'Yesterday' },
  ];

  const achievements = [
    { id: 1, title: 'Early Bird', icon: '🌅', desc: 'First expense before 8 AM', unlocked: true },
    { id: 2, title: 'Crypto King', icon: '💎', desc: '10 ALGO transactions', unlocked: true },
    { id: 3, title: 'Saver', icon: '💰', desc: 'Spend 20% less than last month', unlocked: false },
  ];

  // NavLink Style Helper
  const navClass = ({ isActive }) => 
    `w-full flex items-center gap-3 px-3 py-2 rounded-xl transition-all font-semibold ${
      isActive ? 'bg-indigo-50 text-indigo-600 shadow-sm' : 'text-slate-500 hover:bg-slate-50'
    }`;

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="hidden lg:flex w-64 bg-white border-r border-slate-200 flex-col p-6 space-y-8 sticky top-0 h-screen">
        <div className="flex items-center gap-2 px-2">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white">
            <TrendingUp size={20} />
          </div>
          <span className="font-bold text-xl text-slate-900 tracking-tight">SplitAlgo</span>
        </div>
        
        <nav className="space-y-1">
          <NavLink to="/dashboard" className={navClass}>
            <LayoutDashboard size={20} /> Dashboard
          </NavLink>
          <NavLink to="/groups" className={navClass}>
            <Users size={20} /> Groups
          </NavLink>
          <NavLink to="/wallet" className={navClass}>
            <Wallet size={20} /> Wallet
          </NavLink>
          <NavLink to="/activity" className={navClass}>
            <History size={20} /> Activity
          </NavLink>
        </nav>

        <div className="mt-auto p-4 bg-slate-900 rounded-2xl text-white">
          <p className="text-xs font-bold text-slate-400 uppercase mb-2">Pro Plan</p>
          <p className="text-sm font-medium mb-3">Get unlimited groups and advanced AI analytics.</p>
          <button className="w-full py-2 bg-indigo-600 rounded-lg text-xs font-bold hover:bg-indigo-700 transition-all">Upgrade Now</button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8 lg:p-12 overflow-y-auto">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Welcome Back, Alex</h1>
            <p className="text-slate-500">Here's what's happening with your finances today.</p>
          </div>
          <div className="flex gap-3 w-full md:w-auto">
            <Link to="/groups" className="flex-1 md:flex-none">
              <button className="w-full bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-xl flex items-center justify-center gap-2 font-semibold hover:bg-slate-50 transition-all">
                <Users size={18} /> View Groups
              </button>
            </Link>
            <button className="flex-1 md:flex-none bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-indigo-200 transition-all font-semibold">
              <Plus size={20} /> New Expense
            </button>
          </div>
        </header>

        {/* Top Cards: Wallet & Analytics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-white rounded-3xl p-8 border border-slate-100 shadow-sm relative overflow-hidden">
            <div className="relative z-10">
              <h3 className="text-slate-500 font-medium mb-4 flex items-center gap-2">
                <Wallet size={18} /> Total Balance
              </h3>
              <div className="flex flex-col md:flex-row md:items-end gap-6">
                <div>
                  <p className="text-5xl font-black text-slate-900 tracking-tight">₹{balances.inr}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-lg text-sm font-bold">{balances.algo} ALGO</span>
                    <span className="text-slate-400 text-sm font-medium">≈ $154.20 USD</span>
                  </div>
                </div>
                <div className="flex gap-2 mt-4 md:mt-0">
                  <button className="px-4 py-2 bg-slate-50 hover:bg-slate-100 rounded-xl text-slate-700 transition-colors flex items-center gap-2 text-sm font-bold border border-slate-100">
                    <RefreshCw size={14} /> Bridge
                  </button>
                  <button className="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all text-sm font-bold shadow-md">
                    Sync GPay
                  </button>
                </div>
              </div>
            </div>
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-50/50 rounded-full -mr-32 -mt-32 blur-3xl"></div>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm flex flex-col items-center">
            <div className="w-full flex justify-between items-center mb-4">
               <h3 className="font-bold text-slate-800">Spend Analysis</h3>
               <ArrowRight size={16} className="text-slate-300" />
            </div>
            <div className="w-full h-40">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={categories} innerRadius={45} outerRadius={60} paddingAngle={8} dataKey="value">
                    {categories.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 mt-4">
              {categories.map(c => (
                <div key={c.name} className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{backgroundColor: c.color}}></div>
                  <span className="text-xs font-bold text-slate-500 uppercase tracking-wide">{c.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Activity */}
          <section>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-slate-800">Recent Activity</h3>
              <button className="text-indigo-600 text-sm font-bold hover:bg-indigo-50 px-3 py-1 rounded-lg transition-all">View All</button>
            </div>
            <div className="space-y-4">
              {recentExpenses.map(exp => (
                <div key={exp.id} className="bg-white p-5 rounded-2xl border border-slate-100 flex justify-between items-center hover:shadow-lg hover:border-indigo-100 transition-all cursor-pointer group">
                  <div className="flex items-center gap-4">
                    <div className="p-3 bg-rose-50 text-rose-500 rounded-xl group-hover:scale-110 transition-transform">
                      <ArrowUpRight size={20} />
                    </div>
                    <div>
                      <p className="font-bold text-slate-900">{exp.title}</p>
                      <p className="text-sm text-slate-400 font-medium">{exp.group} • {exp.date}</p>
                    </div>
                  </div>
                  <p className="font-bold text-slate-900 text-lg">{exp.amount}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Achievements Grid */}
          <section>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                <Award className="text-amber-500" /> My Badges
              </h3>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {achievements.map(ach => (
                <div 
                  key={ach.id} 
                  className={`p-5 rounded-3xl border transition-all cursor-pointer group relative overflow-hidden
                    ${ach.unlocked ? 'bg-white border-slate-100 hover:shadow-xl hover:-translate-y-1' : 'bg-slate-100/50 border-transparent opacity-60'}`}
                >
                  <div className="relative z-10">
                    <span className="text-3xl mb-3 block">{ach.icon}</span>
                    <p className="font-bold text-slate-900 text-sm">{ach.title}</p>
                    <p className="text-[10px] text-slate-400 font-bold uppercase mt-1 tracking-wider">{ach.unlocked ? 'Unlocked' : 'Locked'}</p>
                  </div>
                  
                  {/* Hover Overlay */}
                  <div className="absolute inset-0 bg-indigo-600 text-white p-5 rounded-3xl opacity-0 group-hover:opacity-100 transition-all flex flex-col justify-center transform translate-y-2 group-hover:translate-y-0">
                    <p className="font-bold text-sm mb-1">{ach.title}</p>
                    <p className="text-xs text-indigo-100 leading-snug">{ach.desc}</p>
                  </div>
                </div>
              ))}
              <div className="p-5 rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center text-slate-400 group hover:border-indigo-300 transition-colors">
                <p className="text-[10px] font-black uppercase tracking-widest mb-1 group-hover:text-indigo-400">Next Unlock</p>
                <Plus size={20} className="group-hover:rotate-90 transition-transform" />
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;