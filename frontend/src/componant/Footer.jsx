import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-100">
      <div className="max-w-7xl mx-auto px-6 pt-16 pb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
          
          {/* Brand Column */}
          <div className="col-span-1 lg:col-span-1">
            <div className="flex items-center gap-2 mb-6">
              <div className="h-8 w-8 bg-indigo-600 rounded-lg flex items-center justify-center shadow-md">
                <span className="text-white font-bold">F</span>
              </div>
              <span className="text-xl font-bold tracking-tight text-slate-800">
                Fast<span className="text-indigo-600">UI</span>
              </span>
            </div>
            <p className="text-slate-500 leading-relaxed mb-6">
              Making web development faster and more beautiful for everyone. Build your next big idea with our components.
            </p>
            <div className="flex gap-4">
              {/* Social Icons placeholder */}
              {['twitter', 'github', 'discord'].map((social) => (
                <div key={social} className="w-9 h-9 bg-slate-50 rounded-full flex items-center justify-center text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 cursor-pointer transition-all">
                  <span className="sr-only">{social}</span>
                  <div className="w-5 h-5 bg-current rounded-sm"></div> {/* Replace with actual icons */}
                </div>
              ))}
            </div>
          </div>

          {/* Links Columns */}
          <div>
            <h4 className="font-bold text-slate-900 mb-6">Product</h4>
            <ul className="space-y-4">
              {['Features', 'Integrations', 'Pricing', 'Changelog'].map((item) => (
                <li key={item}>
                  <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">{item}</a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-slate-900 mb-6">Company</h4>
            <ul className="space-y-4">
              {['About Us', 'Careers', 'Privacy Policy', 'Terms of Service'].map((item) => (
                <li key={item}>
                  <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">{item}</a>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter Column */}
          <div className="col-span-1">
            <h4 className="font-bold text-slate-900 mb-6">Stay Updated</h4>
            <p className="text-sm text-slate-500 mb-4">Subscribe to our newsletter for the latest updates.</p>
            <form className="flex flex-col gap-2">
              <input 
                type="email" 
                placeholder="Enter your email" 
                className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
              />
              <button className="bg-indigo-600 text-white font-bold py-3 rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100">
                Subscribe
              </button>
            </form>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-50 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-slate-400">
            © 2026 FastUI Inc. All rights reserved.
          </p>
          <div className="flex gap-8">
            <a href="#" className="text-xs text-slate-400 hover:text-slate-600">Status</a>
            <a href="#" className="text-xs text-slate-400 hover:text-slate-600">Cookies</a>
            <a href="#" className="text-xs text-slate-400 hover:text-slate-600">Security</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;