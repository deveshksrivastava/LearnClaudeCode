import { useState } from 'react';
import type { Product } from '../types';

interface Props {
  product: Product;
  onAddToCart: (productId: number, quantity: number) => void;
}

export default function ProductCard({ product, onAddToCart }: Props) {
  const [qty, setQty] = useState(1);

  return (
    <div className="product-card">
      <h3 className="product-name">{product.name}</h3>
      <p className="product-price">${product.price.toFixed(2)}</p>
      <p className={`product-stock ${product.stock === 0 ? 'out-of-stock' : ''}`}>
        {product.stock === 0 ? 'Out of stock' : `${product.stock} in stock`}
      </p>
      <div className="product-actions">
        <input
          type="number"
          className="qty-input"
          min={1}
          max={product.stock}
          value={qty}
          disabled={product.stock === 0}
          onChange={(e) => setQty(Math.max(1, Math.min(product.stock, Number(e.target.value))))}
        />
        <button
          className="add-btn"
          disabled={product.stock === 0}
          onClick={() => onAddToCart(product.id, qty)}
        >
          Add to Cart
        </button>
      </div>
    </div>
  );
}
