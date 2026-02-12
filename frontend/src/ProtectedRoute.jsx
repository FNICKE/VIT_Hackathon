import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { isAuthenticated } from './config/api';

export const ProtectedRoute = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login', { state: { from: location } });
    }
  }, [navigate, location]);

  if (!isAuthenticated()) {
    return null;
  }

  return children;
};

export default ProtectedRoute;
