import React, { useState } from 'react';
import { 
  Users, Plus, Link as LinkIcon, Shield, 
  Copy, ExternalLink, UserPlus, Info, 
  Wallet, BadgeCheck, TrendingDown
} from 'lucide-react';

const Group = () => {
  const [activeTab, setActiveTab] = useState('list'); // 'list', 'create', 'members'

  // Mock Data
  const groups = [
    { id: 1, name: "Office Crew", desc: "Daily lunch & coffee splits", vault: "ALGO...4BGT24", currency: "INR", members: 8 },
    { id: 2, name: "Flatmates", desc: "Rent, Electricity & Groceries", vault: "ALGO...X7GUTU", currency: "INR", members: 4 }
  ];

  const members = [
    { id: 1, name: "Alex Rivera", email: "alex@example.com", risk: 12, badges: ["👑 Admin", "💎 Crypto King"], avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Alex" },
    { id: 2, name: "Priya Sharma", email: "priya@example.com", risk: 45, badges: ["⚡ Fast Payer"], avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Priya" },
    { id: 3, name: "John Doe", email: "john@example.com", risk: 88, badges: ["🐌 Late Payer"], avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=John" }
  ];

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-black text-slate-900 flex items-center gap-3">
              <Users className="text-indigo-600" size={32} /> Group Management
            </h1>
            <p className="text-slate-500 mt-1">Manage your split-expense circles and on-chain vaults.</p>
          </div>
          <div className="flex bg-white p-1 rounded-2xl border border-slate-200 shadow-sm">
            <button 
              onClick={() => setActiveTab('list')}
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'list' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'}`}
            >
              My Groups
            </button>
            <button 
              onClick={() => setActiveTab('create')}
              className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${activeTab === 'create' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50'}`}
            >
              + Create New
            </button>
          </div>
        </div>

        {/* --- View: Group Listing --- */}
        {activeTab === 'list' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map(group => (
              <div key={group.id} className="bg-white rounded-3xl p-6 border border-slate-100 shadow-sm hover:shadow-xl transition-all group">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600">
                    <Users size={24} />
                  </div>
                  <span className="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wider">
                    {group.currency}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-1">{group.name}</h3>
                <p className="text-slate-500 text-sm mb-6 line-clamp-2">{group.desc}</p>
                
                <div className="space-y-3 mb-6">
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>Vault Address</span>
                    <button className="text-indigo-600 hover:underline flex items-center gap-1">
                      <Copy size={12} /> Copy
                    </button>
                  </div>
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-100 font-mono text-xs text-slate-600 truncate">
                    {group.vault}
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex -space-x-2">
                    {[...Array(3)].map((_, i) => (
                      <div key={i} className="w-8 h-8 rounded-full border-2 border-white bg-slate-200"></div>
                    ))}
                    <div className="w-8 h-8 rounded-full border-2 border-white bg-indigo-100 flex items-center justify-center text-[10px] font-bold text-indigo-600">
                      +{group.members - 3}
                    </div>
                  </div>
                  <button 
                    onClick={() => setActiveTab('members')}
                    className="text-sm font-bold text-indigo-600 flex items-center gap-1 group-hover:gap-2 transition-all"
                  >
                    View Members <ExternalLink size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* --- View: Create Group Form --- */}
        {activeTab === 'create' && (
          <div className="max-w-2xl mx-auto bg-white rounded-3xl p-8 border border-slate-100 shadow-sm">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Create New Group</h2>
            <form className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Group Name</label>
                  <input type="text" placeholder="e.g. Goa Trip 2024" className="w-full px-4 py-3 rounded-xl bg-slate-50 border-transparent focus:bg-white focus:border-indigo-600 transition-all outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-slate-700 mb-2">Base Currency</label>
                  <select className="w-full px-4 py-3 rounded-xl bg-slate-50 border-transparent focus:bg-white focus:border-indigo-600 transition-all outline-none">
                    <option>INR (Fiat)</option>
                    <option>ALGO (Web3)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Description</label>
                <textarea rows="3" placeholder="What's this group for?" className="w-full px-4 py-3 rounded-xl bg-slate-50 border-transparent focus:bg-white focus:border-indigo-600 transition-all outline-none resize-none"></textarea>
              </div>
              <div className="p-4 bg-indigo-50 rounded-2xl border border-indigo-100 flex gap-4">
                <div className="text-indigo-600"><Shield size={24} /></div>
                <p className="text-xs text-indigo-700 leading-relaxed">
                  <strong>On-Chain Vault:</strong> Creating a group will deploy a new Algorand smart-contract vault to secure the pooled funds.
                </p>
              </div>
              <button className="w-full bg-indigo-600 py-4 rounded-xl text-white font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all">
                Create Group & Deploy Vault
              </button>
            </form>
          </div>
        )}

        {/* --- View: Member Management --- */}
        {activeTab === 'members' && (
          <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
              <h3 className="text-xl font-bold text-slate-900">Group Members</h3>
              <button className="text-indigo-600 font-bold text-sm flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-xl">
                <LinkIcon size={16} /> Invite Link
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/50 text-slate-400 text-[10px] uppercase tracking-widest font-bold">
                    <th className="px-6 py-4">Member</th>
                    <th className="px-6 py-4">Risk Score</th>
                    <th className="px-6 py-4">Badges</th>
                    <th className="px-6 py-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {members.map(member => (
                    <tr key={member.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <img src={member.avatar} alt="" className="w-10 h-10 rounded-full bg-slate-100" />
                          <div>
                            <p className="font-bold text-slate-900">{member.name}</p>
                            <p className="text-xs text-slate-400">{member.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-24 h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${member.risk < 30 ? 'bg-emerald-500' : member.risk < 60 ? 'bg-amber-500' : 'bg-rose-500'}`} 
                              style={{ width: `${member.risk}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-bold text-slate-600">{member.risk}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-2">
                          {member.badges.map(badge => (
                            <span key={badge} className="text-[10px] bg-slate-100 text-slate-600 px-2 py-1 rounded-lg font-bold">
                              {badge}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-slate-400 hover:text-rose-600 transition-colors">
                          <Info size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Group;