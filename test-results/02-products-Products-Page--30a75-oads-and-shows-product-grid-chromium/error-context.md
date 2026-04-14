# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 02-products.spec.ts >> Products Page >> products page loads and shows product grid
- Location: e2e\02-products.spec.ts:14:7

# Error details

```
Error: page.goto: net::ERR_INSUFFICIENT_RESOURCES at http://localhost:5173/products
Call log:
  - navigating to "http://localhost:5173/products", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | // Set localStorage directly — faster and avoids full-page-reload auth timing issues
  4  | async function loginAndGoTo(page, path: string) {
  5  |   await page.goto('/login');
  6  |   // Inject auth into localStorage before React re-reads it
  7  |   await page.evaluate(() => localStorage.setItem('isLoggedIn', 'true'));
> 8  |   await page.goto(path);
     |              ^ Error: page.goto: net::ERR_INSUFFICIENT_RESOURCES at http://localhost:5173/products
  9  |   // Wait for React to mount
  10 |   await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  11 | }
  12 | 
  13 | test.describe('Products Page', () => {
  14 |   test('products page loads and shows product grid', async ({ page }) => {
  15 |     await loginAndGoTo(page, '/products');
  16 |     await expect(page.locator('h1')).toContainText('Products');
  17 |     // Wait for loading to finish — either products show or an error message
  18 |     await expect(page.locator('.product-grid')).toBeVisible({ timeout: 10000 });
  19 |   });
  20 | 
  21 |   test('products are fetched from the e-commerce API', async ({ page }) => {
  22 |     await loginAndGoTo(page, '/products');
  23 |     // Wait for products to appear in the grid (not just "Loading...")
  24 |     await expect(page.locator('.product-grid .product-card').first()).toBeVisible({ timeout: 10000 });
  25 |   });
  26 | 
  27 |   test('navbar is visible on products page', async ({ page }) => {
  28 |     await loginAndGoTo(page, '/products');
  29 |     await expect(page.locator('nav, .navbar, header')).toBeVisible();
  30 |   });
  31 | });
  32 | 
```