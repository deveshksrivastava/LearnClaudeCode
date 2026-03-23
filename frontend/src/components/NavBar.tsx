import { Link } from 'react-router-dom';

interface Props {
  cartCount: number;
}

export default function NavBar({ cartCount }: Props) {
  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">ShopFast</Link>
      <div className="nav-links">
        <Link to="/users" className="nav-link">Users</Link>
        <Link to="/cart" className="nav-cart">
          Cart{cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </Link>
      </div>
    </nav>
  );
}
