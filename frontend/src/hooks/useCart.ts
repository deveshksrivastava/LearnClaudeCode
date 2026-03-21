import { useState, useEffect, useCallback } from 'react';
import { fetchCart, addToCart, removeFromCart } from '../api/cart';
import type { CartResponse } from '../types';

export function useCart() {
  const [cart, setCart] = useState<CartResponse>({ items: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    return fetchCart()
      .then(setCart)
      .catch(() => setError('Failed to load cart'));
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  const addItem = useCallback(async (productId: number, quantity: number) => {
    await addToCart({ product_id: productId, quantity });
    await refresh();
  }, [refresh]);

  const removeItem = useCallback(async (productId: number) => {
    await removeFromCart(productId);
    await refresh();
  }, [refresh]);

  return { cart, loading, error, addItem, removeItem, refresh };
}
