import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Navbar from './componant/Navbar'; 
import Footer from './componant/Footer';
import ProtectedRoute from './ProtectedRoute';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Group from './pages/Group';

const LayoutWrapper = ({ children }) => {
  const location = useLocation();
  
  const excludedRoutes = ['/login', '/register', '/dashboard', '/groups'];
  const isExcluded = excludedRoutes.includes(location.pathname);

  return (
    <div className="flex flex-col min-h-screen">
      {!isExcluded && <Navbar />}
      
      <main className={`flex-grow ${!isExcluded ? 'pt-20' : ''}`}>
        {children}
      </main>

      {!isExcluded && <Footer />}
    </div>
  );
};

const App = () => {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || "YOUR_CLIENT_ID_HERE.apps.googleusercontent.com"}>
      <Router>
        <LayoutWrapper>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/groups" 
              element={
                <ProtectedRoute>
                  <Group />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </LayoutWrapper>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;