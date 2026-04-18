import { test, expect } from '@playwright/test';

// Set localStorage directly — faster and avoids full-page-reload auth timing issues
async function loginAndGoTo(page, path: string) {
  await page.goto('/login');
  // Inject auth into localStorage before React re-reads it
  await page.evaluate(() => localStorage.setItem('isLoggedIn', 'true'));
  await page.goto(path);
  // Wait for React to mount
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
}

test.describe('Products Page', () => {
  test('products page loads and shows product grid', async ({ page }) => {
    await loginAndGoTo(page, '/products');
    await expect(page.locator('h1')).toContainText('Products');
    // Wait for loading to finish — either products show or an error message
    await expect(page.locator('.product-grid')).toBeVisible({ timeout: 10000 });
  });

  test('products are fetched from the e-commerce API', async ({ page }) => {
    await loginAndGoTo(page, '/products');
    // Wait for products to appear in the grid (not just "Loading...")
    await expect(page.locator('.product-grid .product-card').first()).toBeVisible({ timeout: 10000 });
  });

  test('navbar is visible on products page', async ({ page }) => {
    await loginAndGoTo(page, '/products');
    await expect(page.locator('nav, .navbar, header')).toBeVisible();
  });
});
