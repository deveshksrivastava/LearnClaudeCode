export interface TableRow {
  field: string;
  description: string;
  type: string;
  source: string;
  unit: string;
  referenceFlag: string;
  referenceValue: string;
  dataFlag: string;
  attribute: string;
}

export interface Category {
  id: string;
  name: string;
  icon: string;
  description: string;
  itemCount: number;
  status: 'Active' | 'Inactive';
  color: string;
  tags: string[];
  productSummary: TableRow[];
  salesSummary: TableRow[];
}

const PRODUCT_ROWS: TableRow[] = [
  { field: 'ID',         description: 'Unique category identifier',  type: 'String',  source: 'Internal',  unit: '',    referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Category ID'    },
  { field: 'Name',       description: 'Category display name',       type: 'String',  source: 'Internal',  unit: '',    referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Category Name'  },
  { field: 'Item Count', description: 'Total number of listed items', type: 'Numeric', source: 'Inventory', unit: 'pcs', referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Total Items'    },
  { field: 'Status',     description: 'Current availability status', type: 'Boolean', source: 'Internal',  unit: '',    referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Active Flag'    },
  { field: 'Tags',       description: 'Associated search keywords',  type: 'Array',   source: 'Internal',  unit: '',    referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Tag List'       },
  { field: 'Colour',     description: 'Brand display colour code',   type: 'String',  source: 'Internal',  unit: 'HEX', referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Brand Colour'   },
];

const SALES_ROWS: TableRow[] = [
  { field: 'Revenue',    description: 'Total monthly revenue',          type: 'Numeric', source: 'Finance', unit: 'USD', referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Monthly Revenue' },
  { field: 'Units Sold', description: 'Number of units sold this month', type: 'Int4',    source: 'Sales',   unit: 'pcs', referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Units Sold'     },
  { field: 'Avg Price',  description: 'Average selling price per unit',  type: 'Numeric', source: 'Finance', unit: 'USD', referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Average Price'  },
  { field: 'Top Seller', description: 'Best performing product name',    type: 'String',  source: 'Sales',   unit: '',    referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'Top Product'    },
  { field: 'Growth',     description: 'Month-over-month growth rate',    type: 'Numeric', source: 'Finance', unit: '%',   referenceFlag: 'N/A', referenceValue: 'N/A', dataFlag: 'N/A', attribute: 'MoM Growth'     },
];

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
    productSummary: PRODUCT_ROWS,
    salesSummary: SALES_ROWS,
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
    productSummary: PRODUCT_ROWS,
    salesSummary: SALES_ROWS,
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
    productSummary: PRODUCT_ROWS,
    salesSummary: SALES_ROWS,
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
    productSummary: PRODUCT_ROWS,
    salesSummary: SALES_ROWS,
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
    productSummary: PRODUCT_ROWS,
    salesSummary: SALES_ROWS,
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
    productSummary: PRODUCT_ROWS,
    salesSummary: SALES_ROWS,
  },
];
