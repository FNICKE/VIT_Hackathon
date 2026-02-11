import React from 'react';

const Home = () => {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* Hero Section */}
      <header className="relative overflow-hidden bg-white pt-16 pb-32">
        <div className="container mx-auto px-6 relative z-10">
          <div className="flex flex-col items-center text-center">
            <span className="px-4 py-1.5 rounded-full text-sm font-medium bg-indigo-100 text-indigo-600 mb-6">
              New Version 2.0 is live
            </span>
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-slate-900 mb-6">
              Build your next idea <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">
                faster than ever.
              </span>
            </h1>
            <p className="max-w-2xl text-lg text-slate-600 mb-10">
              Stop wasting time on boilerplate. Use our pre-built components to 
              launch your SaaS, portfolio, or blog in record time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-bold transition-all shadow-lg hover:shadow-indigo-200">
                Get Started Free
              </button>
              <button className="px-8 py-4 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl font-bold transition-all">
                View Documentation
              </button>
            </div>
          </div>
        </div>
        
        {/* Subtle Background Decoration */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-0 opacity-20 pointer-events-none">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-400 blur-[120px]"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-violet-400 blur-[120px]"></div>
        </div>
      </header>

      {/* Features Section */}
      <section className="py-24 bg-slate-50">
        <div className="container mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              { title: "Lightning Fast", desc: "Built with React and Tailwind for maximum performance.", icon: "⚡" },
              { title: "Responsive Design", desc: "Looks great on mobile, tablet, and desktop screens.", icon: "📱" },
              { title: "Easy Scaling", desc: "Modular code that grows alongside your business.", icon: "🚀" }
            ].map((feature, i) => (
              <div key={i} className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-slate-600 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="bg-indigo-600 rounded-3xl p-12 text-center text-white relative overflow-hidden">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 relative z-10">Ready to transform your workflow?</h2>
          <p className="text-indigo-100 mb-8 max-w-xl mx-auto relative z-10">
            Join over 10,000+ developers building the future of the web.
          </p>
          <button className="bg-white text-indigo-600 px-10 py-4 rounded-xl font-bold hover:bg-slate-100 transition-colors relative z-10">
            Join the Waitlist
          </button>
        </div>
      </section>
    </div>
  );
}

export default Home;