import { useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import ProductsPage from './pages/ProductsPage';
import CartPage from './pages/CartPage';
import ChatbotPage from './pages/ChatbotPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UsersPage from './pages/UsersPage';
import DashboardPage from './pages/DashboardPage';
import FixLayout from './pages/FixLayout';
import { fetchCart } from './api/cart';

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
        <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
        <Route path="/register" element={<RegisterPage />} />
        {/* <Route path="/" element={<FixLayout />} /> */}

        
        <Route path="/" element={<DashboardPage />} />
        <Route path="/products" element={<ProductsPage onCartChange={refreshCartCount} />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/chat" element={<ChatbotPage />} />
      </Routes>
      </div>
    </BrowserRouter>
  );
}
