export interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
  itemCount: number;
  status: 'Active' | 'Inactive';
  color: string;
  tags: string[];
}

export const CATEGORIES: Category[] = [
  {
    id: 'electronics',
    name: 'Electronics',
    icon: '📦',
    description: 'Smartphones, laptops, tablets, accessories and all consumer electronics. From cutting-edge gadgets to everyday tech essentials.',
    itemCount: 24,
    status: 'Active',
    color: '#6366f1',
    tags: ['tech', 'gadgets', 'devices'],
  },
  {
    id: 'fashion',
    name: 'Fashion',
    icon: '👗',
    description: 'Clothing, footwear, and accessories for all styles and seasons. Curated collections from top brands and emerging designers.',
    itemCount: 18,
    status: 'Active',
    color: '#ec4899',
    tags: ['clothing', 'style', 'apparel'],
  },
  {
    id: 'home',
    name: 'Home & Living',
    icon: '🏠',
    description: 'Furniture, décor, kitchen essentials, and everything you need to make your home a comfortable and stylish space.',
    itemCount: 31,
    status: 'Active',
    color: '#f59e0b',
    tags: ['furniture', 'decor', 'kitchen'],
  },
  {
    id: 'sports',
    name: 'Sports',
    icon: '⚽',
    description: 'Fitness equipment, outdoor gear, sportswear, and accessories for athletes and active lifestyle enthusiasts.',
    itemCount: 12,
    status: 'Active',
    color: '#10b981',
    tags: ['fitness', 'outdoor', 'gear'],
  },
  {
    id: 'books',
    name: 'Books',
    icon: '📚',
    description: 'Fiction, non-fiction, educational, and self-help titles across every genre. Discover your next favourite read.',
    itemCount: 45,
    status: 'Active',
    color: '#8b5cf6',
    tags: ['education', 'fiction', 'reading'],
  },
  {
    id: 'beauty',
    name: 'Beauty',
    icon: '💄',
    description: 'Skincare, makeup, fragrances and personal care products. Premium beauty essentials for every routine.',
    itemCount: 9,
    status: 'Inactive',
    color: '#f43f5e',
    tags: ['skincare', 'makeup', 'wellness'],
  },
];
