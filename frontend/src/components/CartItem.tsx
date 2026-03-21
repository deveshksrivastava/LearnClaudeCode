import type { CartItemData } from '../types';

interface Props {
  item: CartItemData;
  onRemove: (productId: number) => void;
}

export default function CartItem({ item, onRemove }: Props) {
  const lineTotal = item.product.price * item.quantity;
  return (
    <div className="cart-item">
      <div className="cart-item-info">
        <span className="cart-item-name">{item.product.name}</span>
        <span className="cart-item-meta">
          ${item.product.price.toFixed(2)} × {item.quantity} = ${lineTotal.toFixed(2)}
        </span>
      </div>
      <button className="remove-btn" onClick={() => onRemove(item.product.id)}>
        Remove
      </button>
    </div>
  );
}
