import React from 'react';
import { Link } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google'; // Import Google Login

const Login = () => {
  
  const handleGoogleSuccess = (credentialResponse) => {
    console.log("Google Login Success:", credentialResponse);
    // Here you would send credentialResponse.credential to your backend
  };

  const handleGoogleError = () => {
    console.log("Google Login Failed");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 md:bg-white">
      <div className="flex w-full max-w-[1200px] min-h-[700px] shadow-2xl overflow-hidden md:rounded-3xl bg-white m-0 md:m-4">
        
        {/* Left Side: Login Form */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 md:px-16 lg:px-20 py-12">
          <div className="mb-10 text-center lg:text-left">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-2">Welcome back!</h2>
            <p className="text-slate-500">Please enter your details to sign in.</p>
          </div>

          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Email Address</label>
              <input 
                type="email" 
                placeholder="name@company.com" 
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <div>
              <div className="flex justify-between mb-2">
                <label className="text-sm font-semibold text-slate-700">Password</label>
                <Link to="/forgot-password" size="sm" className="text-sm font-semibold text-indigo-600 hover:text-indigo-500 transition-colors">
                  Forgot?
                </Link>
              </div>
              <input 
                type="password" 
                placeholder="••••••••" 
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all"
              />
            </div>

            <button className="w-full bg-indigo-600 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all active:scale-[0.98]">
              Sign In
            </button>

            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-100"></div></div>
              <div className="relative flex justify-center text-xs uppercase"><span className="bg-white px-2 text-slate-400 font-medium">Or continue with</span></div>
            </div>

            {/* REAL GOOGLE LOGIN BUTTON */}
            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={handleGoogleError}
                useOneTap
                theme="outline"
                shape="pill"
                width="100%"
              />
            </div>
          </form>

          <p className="mt-8 text-center text-slate-500">
            Don't have an account?{" "}
            <Link to="/register" className="font-bold text-indigo-600 hover:text-indigo-700 hover:underline transition-all">
              Sign up for free
            </Link>
          </p>
        </div>

        {/* Right Side: Visual Content */}
        <div className="hidden lg:flex w-1/2 bg-indigo-600 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-white/10 rounded-full -mr-40 -mt-40 blur-3xl animate-pulse"></div>
          <div className="relative z-10 w-full flex flex-col justify-center items-center p-16 text-center text-white">
             <div className="mb-8 p-4 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-xl group hover:scale-110 transition-transform">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
             </div>
             <h3 className="text-4xl font-bold mb-6">Experience the fastest way to build.</h3>
             <p className="text-indigo-100 text-lg max-w-sm leading-relaxed mb-8">
               "This platform has completely transformed how our team manages projects."
             </p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Login;