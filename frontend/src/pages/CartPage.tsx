import CartItem from '../components/CartItem';
import { useCart } from '../hooks/useCart';

export default function CartPage() {
  const { cart, loading, error, removeItem } = useCart();

  return (
    <main className="page">
      <h1 className="page-title">Your Cart</h1>
      {loading && <p className="status-msg">Loading...</p>}
      {error && <p className="status-msg error">{error}</p>}
      {!loading && !error && cart.items.length === 0 && (
        <p className="status-msg">Your cart is empty.</p>
      )}
      <div className="cart-list">
        {cart.items.map((item) => (
          <CartItem key={item.product.id} item={item} onRemove={removeItem} />
        ))}
      </div>
      {cart.items.length > 0 && (
        <div className="cart-total">
          <strong>Total: ${cart.total.toFixed(2)}</strong>
        </div>
      )}
    </main>
  );
}
