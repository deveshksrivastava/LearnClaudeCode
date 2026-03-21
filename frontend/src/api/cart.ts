import client from './client';
import type { CartResponse, AddToCartPayload } from '../types';

export const fetchCart = (): Promise<CartResponse> =>
  client.get<CartResponse>('/cart').then((r) => r.data);

export const addToCart = (payload: AddToCartPayload): Promise<void> =>
  client.post('/cart', payload).then(() => undefined);

export const removeFromCart = (productId: number): Promise<void> =>
  client.delete(`/cart/${productId}`).then(() => undefined);
