import client from './client';
import type { Product, CreateProductPayload } from '../types';

export const fetchProducts = (): Promise<Product[]> =>
  client.get<Product[]>('/products').then((r) => r.data);

export const searchProducts = (q: string): Promise<Product[]> =>
  client.get<Product[]>('/products/search', { params: { q } }).then((r) => r.data);

export const fetchProduct = (id: number): Promise<Product> =>
  client.get<Product>(`/products/${id}`).then((r) => r.data);

export const createProduct = (payload: CreateProductPayload): Promise<Product> =>
  client.post<Product>('/products', payload).then((r) => r.data);
