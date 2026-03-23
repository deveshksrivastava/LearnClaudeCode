import { useState, useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import ProductsPage from './pages/ProductsPage';
import CartPage from './pages/CartPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UsersPage from './pages/UsersPage';
import DashboardPage from './pages/DashboardPage';
import { fetchCart } from './api/cart';

export default function App() {
  const [cartCount, setCartCount] = useState(0);

  const refreshCartCount = useCallback(() => {
    fetchCart().then((cart) => setCartCount(cart.items.length));
  }, []);

  return (
    <BrowserRouter>
      <NavBar cartCount={cartCount} />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={<ProductsPage onCartChange={refreshCartCount} />} />
        <Route path="/cart" element={<CartPage />} />
        <Route path="/users" element={<UsersPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}
