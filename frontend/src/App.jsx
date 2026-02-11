import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google'; // 1. Import the Provider
import Navbar from './componant/Navbar'; 
import Footer from './componant/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';

const LayoutWrapper = ({ children }) => {
  const location = useLocation();
  const hideNavbarFooter = location.pathname === '/login' || location.pathname === '/register';

  return (
    <div className="flex flex-col min-h-screen">
      {!hideNavbarFooter && <Navbar />}
      <main className={`flex-grow ${!hideNavbarFooter ? 'pt-20' : ''}`}>
        {children}
      </main>
      {!hideNavbarFooter && <Footer />}
    </div>
  );
};

const App = () => {
  return (
    /* 2. Wrap everything here. Replace the text below with your real ID later */
    <GoogleOAuthProvider clientId="YOUR_CLIENT_ID_HERE.apps.googleusercontent.com">
      <Router>
        <LayoutWrapper>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </LayoutWrapper>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;