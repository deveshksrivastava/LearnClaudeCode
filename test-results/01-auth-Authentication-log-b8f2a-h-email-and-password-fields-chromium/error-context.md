# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 01-auth.spec.ts >> Authentication >> login page loads with email and password fields
- Location: e2e\01-auth.spec.ts:4:7

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: expect(locator).toBeVisible() failed

Locator:  locator('input[type="email"]')
Expected: visible
Received: undefined

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('input[type="email"]')

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test.describe('Authentication', () => {
  4  |   test('login page loads with email and password fields', async ({ page }) => {
  5  |     await page.goto('/login');
> 6  |     await expect(page.locator('input[type="email"]')).toBeVisible();
     |                                                       ^ Error: expect(locator).toBeVisible() failed
  7  |     await expect(page.locator('input[type="password"]')).toBeVisible();
  8  |     await expect(page.locator('button[type="submit"]')).toBeVisible();
  9  |   });
  10 | 
  11 |   test('root redirects to login when not authenticated', async ({ page }) => {
  12 |     await page.goto('/');
  13 |     await expect(page).toHaveURL(/login/);
  14 |   });
  15 | 
  16 |   test('login with valid credentials redirects to dashboard', async ({ page }) => {
  17 |     await page.goto('/login');
  18 |     await page.locator('input[type="email"]').fill('test@example.com');
  19 |     await page.locator('input[type="password"]').fill('password123');
  20 |     await page.locator('button[type="submit"]').click();
  21 |     // After login, should land on dashboard
  22 |     await expect(page).toHaveURL(/dashboard/, { timeout: 5000 });
  23 |   });
  24 | 
  25 |   test('register page is accessible', async ({ page }) => {
  26 |     await page.goto('/register');
  27 |     await expect(page.locator('input[type="email"]')).toBeVisible();
  28 |   });
  29 | });
  30 | 
```