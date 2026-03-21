import { useState, useEffect } from 'react';
import { fetchProducts, searchProducts } from '../api/products';
import type { Product } from '../types';

export function useProducts(query: string) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    const timer = setTimeout(() => {
      const request = query.trim() ? searchProducts(query.trim()) : fetchProducts();
      request
        .then(setProducts)
        .catch(() => setError('Failed to load products'))
        .finally(() => setLoading(false));
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return { products, loading, error };
}
