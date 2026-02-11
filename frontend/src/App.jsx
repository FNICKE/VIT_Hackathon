import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import Navbar from './componant/Navbar'; 
import Footer from './componant/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Group from './pages/Group'; // 1. Import your new Group component

const LayoutWrapper = ({ children }) => {
  const location = useLocation();
  
  // 2. Added '/groups' to the excluded list so it gets the full-screen dashboard feel
  const excludedRoutes = ['/login', '/register', '/dashboard', '/groups'];
  const isExcluded = excludedRoutes.includes(location.pathname);

  return (
    <div className="flex flex-col min-h-screen">
      {!isExcluded && <Navbar />}
      
      {/* 3. If excluded (Dashboard/Groups/Login), we remove the top padding entirely */}
      <main className={`flex-grow ${!isExcluded ? 'pt-20' : ''}`}>
        {children}
      </main>

      {!isExcluded && <Footer />}
    </div>
  );
};

const App = () => {
  return (
    /* Replace with your actual Google Client ID */
    <GoogleOAuthProvider clientId="YOUR_CLIENT_ID_HERE.apps.googleusercontent.com">
      <Router>
        <LayoutWrapper>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/groups" element={<Group />} /> {/* 4. Added Group Route */}
          </Routes>
        </LayoutWrapper>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;