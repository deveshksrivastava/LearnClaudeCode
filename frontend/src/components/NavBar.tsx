import { Link, useNavigate } from 'react-router-dom';

interface Props {
  cartCount: number;
  isLoggedIn: boolean;
  onLogout: () => void;
}

export default function NavBar({ cartCount, isLoggedIn, onLogout }: Props) {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">ShopFast</Link>
      <div className="nav-links">
        <Link to="/chat" className="nav-link">Chat</Link>
        <Link to="/llm-chat" className="nav-link">AI Support</Link>
        <Link to="/users" className="nav-link">Users</Link>
        <Link to="/cart" className="nav-cart">
          Cart{cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </Link>
        {isLoggedIn ? (
          <button className="nav-link nav-logout" onClick={handleLogout}>Logout</button>
        ) : (
          <Link to="/login" className="nav-link nav-login">Login</Link>
        )}
      </div>
    </nav>
  );
}
