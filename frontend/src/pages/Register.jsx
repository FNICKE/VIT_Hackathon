import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { API, apiCall, saveToken } from '../config/api';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '', confirmPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!agreedToTerms) {
      setError('Please agree to the terms and conditions');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    try {
      const data = await apiCall(API.auth.register, {
        method: 'POST',
        body: JSON.stringify({ email: formData.email, password: formData.password }),
      });

      if (data.access_token) {
        saveToken(data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true);
    try {
      console.log("Register Success with Google:", credentialResponse);
      // TODO: Send Google token to backend
    } catch (err) {
      setError('Google registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 md:bg-white">
      <div className="flex w-full max-w-[1200px] min-h-[750px] shadow-2xl overflow-hidden md:rounded-3xl bg-white m-0 md:m-4">
        
        {/* Left Side: Visual/Testimonial */}
        <div className="hidden lg:flex w-1/2 bg-indigo-600 relative overflow-hidden">
          <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-white/10 rounded-full -ml-40 -mt-40 blur-3xl"></div>
          
          <div className="relative z-10 w-full flex flex-col justify-center p-16 text-white">
            <h3 className="text-4xl font-bold mb-6 leading-tight">
              Start your 14-day <br /> free trial today.
            </h3>
            <ul className="space-y-4 mb-10">
              {[
                "Full access to all premium components",
                "Unlimited projects and collaborators",
                "Advanced analytics dashboard",
                "24/7 Priority email support"
              ].map((benefit, i) => (
                <li key={i} className="flex items-center gap-3 text-indigo-100">
                  <svg className="w-5 h-5 text-indigo-300" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {benefit}
                </li>
              ))}
            </ul>
            
            <div className="p-6 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20">
              <p className="italic text-indigo-50 mb-4">"Joining this platform was the best decision for our startup. We launched 3 weeks ahead of schedule."</p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-indigo-400 overflow-hidden border border-white/20">
                   <img src="https://i.pravatar.cc/150?u=2" alt="Alex Rivera" />
                </div>
                <div>
                  <p className="font-bold text-sm text-white">Alex Rivera</p>
                  <p className="text-indigo-300 text-xs">Founder of NovaTech</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Register Form */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center px-8 md:px-16 lg:px-20 py-12">
          <div className="mb-8 text-center lg:text-left">
            <h2 className="text-3xl font-extrabold text-slate-900 mb-2">Create an account</h2>
            <p className="text-slate-500">Join thousands of developers worldwide.</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl text-sm">
              {error}
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Email Address</label>
              <input 
                type="email" 
                name="email"
                placeholder="john@example.com" 
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all" 
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Password</label>
              <input 
                type="password" 
                name="password"
                placeholder="••••••••" 
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all" 
                required
              />
              <p className="mt-2 text-xs text-slate-400 font-medium">Must be at least 8 characters.</p>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Confirm Password</label>
              <input 
                type="password" 
                name="confirmPassword"
                placeholder="••••••••" 
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none transition-all" 
                required
              />
            </div>

            <div className="flex items-start gap-2">
              <input 
                type="checkbox" 
                id="terms" 
                checked={agreedToTerms}
                onChange={(e) => setAgreedToTerms(e.target.checked)}
                className="mt-1 w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" 
              />
              <label htmlFor="terms" className="text-sm text-slate-500 leading-tight select-none cursor-pointer">
                I agree to the <Link to="/terms" className="text-indigo-600 font-semibold underline">Terms of Service</Link> and <Link to="/privacy" className="text-indigo-600 font-semibold underline">Privacy Policy</Link>.
              </label>
            </div>

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-indigo-100 hover:bg-indigo-700 transition-all active:scale-[0.98] mt-2 disabled:opacity-50">
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-100"></div></div>
              <div className="relative flex justify-center text-xs uppercase"><span className="bg-white px-2 text-slate-400 font-medium">Or join with</span></div>
            </div>

            <div className="flex justify-center">
              <GoogleLogin
                onSuccess={handleGoogleSuccess}
                onError={() => setError('Google registration failed')}
                useOneTap
                theme="outline"
                shape="pill"
                width="100%"
              />
            </div>
          </form>

          <p className="mt-6 text-center text-slate-500">
            Already have an account?{" "}
            <Link to="/login" className="font-bold text-indigo-600 hover:text-indigo-700 hover:underline transition-all">
              Log in
            </Link>
          </p>
        </div>

      </div>
    </div>
  );
};

export default Register;