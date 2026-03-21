import { useState } from 'react';
import SearchBar from '../components/SearchBar';
import ProductCard from '../components/ProductCard';
import { useProducts } from '../hooks/useProducts';
import { addToCart } from '../api/cart';

interface Props {
  onCartChange: () => void;
}

export default function ProductsPage({ onCartChange }: Props) {
  const [query, setQuery] = useState('');
  const { products, loading, error } = useProducts(query);

  const handleAddToCart = async (productId: number, quantity: number) => {
    try {
      await addToCart({ product_id: productId, quantity });
      onCartChange();
    } catch {
      alert('Failed to add item to cart.');
    }
  };

  return (
    <main className="page">
      <h1 className="page-title">Products</h1>
      <SearchBar value={query} onChange={setQuery} />
      {loading && <p className="status-msg">Loading...</p>}
      {error && <p className="status-msg error">{error}</p>}
      {!loading && !error && products.length === 0 && (
        <p className="status-msg">No products found.</p>
      )}
      <div className="product-grid">
        {products.map((p) => (
          <ProductCard key={p.id} product={p} onAddToCart={handleAddToCart} />
        ))}
      </div>
    </main>
  );
}
