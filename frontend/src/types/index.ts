export interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
}

export interface CartItemData {
  product: Product;
  quantity: number;
}

export interface CartResponse {
  items: CartItemData[];
  total: number;
}

export interface AddToCartPayload {
  product_id: number;
  quantity: number;
}

export interface CreateProductPayload {
  name: string;
  price: number;
  stock: number;
}
