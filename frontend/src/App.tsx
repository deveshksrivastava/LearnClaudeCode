import { useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import NavBar from './components/NavBar';
import ProductsPage from './pages/ProductsPage';
import CartPage from './pages/CartPage';
import ChatbotPage from './pages/ChatbotPage';
import LLMChatPage from './pages/LLMChatPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UsersPage from './pages/UsersPage';
import DashboardPage from './pages/DashboardPage';
import { fetchCart } from './api/cart';

function ProtectedRoute({ isLoggedIn, children }: { isLoggedIn: boolean; children: React.ReactNode }) {
  if (!isLoggedIn) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const [cartCount, setCartCount] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!localStorage.getItem('isLoggedIn'));

  const refreshCartCount = useCallback(() => {
    fetchCart().then((cart) => setCartCount(cart.items.length));
  }, []);

  const handleLogin = () => {
    localStorage.setItem('isLoggedIn', 'true');
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('isLoggedIn');
    setIsLoggedIn(false);
  };

  return (
    <BrowserRouter>
      <NavBar cartCount={cartCount} isLoggedIn={isLoggedIn} onLogout={handleLogout} />
      <div className="flex flex-col flex-1 min-h-0">
      <Routes>
        <Route path="/login" element={isLoggedIn ? <Navigate to="/dashboard" replace /> : <LoginPage onLogin={handleLogin} />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={isLoggedIn ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} />
        <Route path="/dashboard" element={<ProtectedRoute isLoggedIn={isLoggedIn}><DashboardPage /></ProtectedRoute>} />
        <Route path="/products" element={<ProtectedRoute isLoggedIn={isLoggedIn}><ProductsPage onCartChange={refreshCartCount} /></ProtectedRoute>} />
        <Route path="/cart" element={<ProtectedRoute isLoggedIn={isLoggedIn}><CartPage /></ProtectedRoute>} />
        <Route path="/users" element={<ProtectedRoute isLoggedIn={isLoggedIn}><UsersPage /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute isLoggedIn={isLoggedIn}><ChatbotPage /></ProtectedRoute>} />
        <Route path="/llm-chat" element={<ProtectedRoute isLoggedIn={isLoggedIn}><LLMChatPage /></ProtectedRoute>} />
      </Routes>
      </div>
    </BrowserRouter>
  );
}
