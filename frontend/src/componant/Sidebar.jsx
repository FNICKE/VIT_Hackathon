import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Users, 
  Wallet, 
  TrendingUp, 
  LayoutDashboard, 
  History 
} from 'lucide-react';

const Sidebar = () => {
  // Helper function for active styles
  const navLinkClass = ({ isActive }) => 
    `w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-semibold ${
      isActive 
        ? 'bg-indigo-50 text-indigo-600 shadow-sm' // Active Style (from your image)
        : 'text-slate-500 hover:bg-slate-50'      // Default Style
    }`;

  return (
    <aside className="hidden lg:flex w-64 bg-white border-r border-slate-200 flex-col p-6 space-y-8 sticky top-0 h-screen">
      {/* Logo Section */}
      <div className="flex items-center gap-3 px-2">
        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-200">
          <TrendingUp size={24} />
        </div>
        <span className="font-bold text-xl text-slate-900 tracking-tight">SplitAlgo</span>
      </div>
      
      {/* Navigation Links */}
      <nav className="space-y-2">
        <NavLink to="/dashboard" className={navLinkClass}>
          <LayoutDashboard size={22} /> 
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/groups" className={navLinkClass}>
          <Users size={22} /> 
          <span>Groups</span>
        </NavLink>

        <NavLink to="/wallet" className={navLinkClass}>
          <Wallet size={22} /> 
          <span>Wallet</span>
        </NavLink>

        <NavLink to="/activity" className={navLinkClass}>
          <History size={22} /> 
          <span>Activity</span>
        </NavLink>
      </nav>

      {/* Optional: Pro Plan Card or Logout */}
      <div className="mt-auto p-4 bg-slate-900 rounded-2xl text-white">
        <p className="text-xs font-bold text-slate-400 uppercase mb-2">Hackathon Mode</p>
        <p className="text-xs text-slate-300 leading-relaxed">
          Algorand Testnet Connected
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;