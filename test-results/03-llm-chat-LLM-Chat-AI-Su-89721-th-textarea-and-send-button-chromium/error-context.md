# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: 03-llm-chat.spec.ts >> LLM Chat (AI Support) >> LLM chat page loads with textarea and send button
- Location: e2e\03-llm-chat.spec.ts:11:7

# Error details

```
Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
Call log:
  - navigating to "http://localhost:5173/llm-chat", waiting until "load"

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | async function loginAndGoTo(page, path: string) {
  4  |   await page.goto('/login');
  5  |   await page.evaluate(() => localStorage.setItem('isLoggedIn', 'true'));
> 6  |   await page.goto(path);
     |              ^ Error: page.goto: net::ERR_ABORTED; maybe frame was detached?
  7  |   await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  8  | }
  9  | 
  10 | test.describe('LLM Chat (AI Support)', () => {
  11 |   test('LLM chat page loads with textarea and send button', async ({ page }) => {
  12 |     await loginAndGoTo(page, '/llm-chat');
  13 |     await expect(page.locator('textarea.chat-textarea')).toBeVisible();
  14 |     await expect(page.locator('button.chat-send-btn')).toBeVisible();
  15 |   });
  16 | 
  17 |   test('send button is disabled when input is empty', async ({ page }) => {
  18 |     await loginAndGoTo(page, '/llm-chat');
  19 |     const sendBtn = page.locator('button.chat-send-btn');
  20 |     await expect(sendBtn).toBeDisabled();
  21 |   });
  22 | 
  23 |   test('send button enables when text is typed', async ({ page }) => {
  24 |     await loginAndGoTo(page, '/llm-chat');
  25 |     await page.locator('textarea.chat-textarea').fill('Hello');
  26 |     await expect(page.locator('button.chat-send-btn')).toBeEnabled();
  27 |   });
  28 | 
  29 |   test('TOOL CALLING: asking about products triggers real product data', async ({ page }) => {
  30 |     await loginAndGoTo(page, '/llm-chat');
  31 | 
  32 |     // Type a product query
  33 |     await page.locator('textarea.chat-textarea').fill('What products do you sell?');
  34 |     await page.locator('button.chat-send-btn').click();
  35 | 
  36 |     // Wait for the AI to respond (tool call + second LLM pass can take ~10s)
  37 |     const aiResponse = page.locator('.chat-bubble--assistant .chat-content').last();
  38 |     await expect(aiResponse).not.toContainText('...', { timeout: 30000 });
  39 |     await expect(aiResponse).toBeVisible({ timeout: 30000 });
  40 | 
  41 |     // The response should contain actual product names (not "I cannot answer")
  42 |     const responseText = await aiResponse.textContent();
  43 |     console.log('AI Product Response:', responseText?.substring(0, 200));
  44 | 
  45 |     // Should NOT say it can't answer from context
  46 |     expect(responseText).not.toMatch(/retrieved context does not|cannot provide|I don't have/i);
  47 |   });
  48 | 
  49 |   test('TOOL CALLING: asking to add to cart works', async ({ page }) => {
  50 |     await loginAndGoTo(page, '/llm-chat');
  51 | 
  52 |     await page.locator('textarea.chat-textarea').fill('Add product 1 to my cart');
  53 |     await page.locator('button.chat-send-btn').click();
  54 | 
  55 |     const aiResponse = page.locator('.chat-bubble--assistant .chat-content').last();
  56 |     await expect(aiResponse).not.toContainText('...', { timeout: 30000 });
  57 |     await expect(aiResponse).toBeVisible({ timeout: 30000 });
  58 | 
  59 |     const responseText = await aiResponse.textContent();
  60 |     console.log('AI Cart Response:', responseText?.substring(0, 200));
  61 | 
  62 |     // Should NOT say it can't add to cart
  63 |     expect(responseText).not.toMatch(/don't have the capability|cannot add|not able to/i);
  64 |   });
  65 | 
  66 |   test('new conversation button clears the chat', async ({ page }) => {
  67 |     await loginAndGoTo(page, '/llm-chat');
  68 |     // Click "New Conversation" button
  69 |     const clearBtn = page.locator('button.chat-clear-btn');
  70 |     if (await clearBtn.isVisible()) {
  71 |       await clearBtn.click();
  72 |       // Chat window should be empty (show empty state)
  73 |       await expect(page.locator('.chat-empty')).toBeVisible();
  74 |     }
  75 |   });
  76 | });
  77 | 
```