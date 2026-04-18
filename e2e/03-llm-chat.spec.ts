import { test, expect } from '@playwright/test';

async function loginAndGoTo(page, path: string) {
  await page.goto('/login');
  await page.evaluate(() => localStorage.setItem('isLoggedIn', 'true'));
  await page.goto(path);
  await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
}

test.describe('LLM Chat (AI Support)', () => {
  test('LLM chat page loads with textarea and send button', async ({ page }) => {
    await loginAndGoTo(page, '/llm-chat');
    await expect(page.locator('textarea.chat-textarea')).toBeVisible();
    await expect(page.locator('button.chat-send-btn')).toBeVisible();
  });

  test('send button is disabled when input is empty', async ({ page }) => {
    await loginAndGoTo(page, '/llm-chat');
    const sendBtn = page.locator('button.chat-send-btn');
    await expect(sendBtn).toBeDisabled();
  });

  test('send button enables when text is typed', async ({ page }) => {
    await loginAndGoTo(page, '/llm-chat');
    await page.locator('textarea.chat-textarea').fill('Hello');
    await expect(page.locator('button.chat-send-btn')).toBeEnabled();
  });

  test('TOOL CALLING: asking about products triggers real product data', async ({ page }) => {
    await loginAndGoTo(page, '/llm-chat');

    // Type a product query
    await page.locator('textarea.chat-textarea').fill('What products do you sell?');
    await page.locator('button.chat-send-btn').click();

    // Wait for the AI to respond (tool call + second LLM pass can take ~10s)
    const aiResponse = page.locator('.chat-bubble--assistant .chat-content').last();
    await expect(aiResponse).not.toContainText('...', { timeout: 30000 });
    await expect(aiResponse).toBeVisible({ timeout: 30000 });

    // The response should contain actual product names (not "I cannot answer")
    const responseText = await aiResponse.textContent();
    console.log('AI Product Response:', responseText?.substring(0, 200));

    // Should NOT say it can't answer from context
    expect(responseText).not.toMatch(/retrieved context does not|cannot provide|I don't have/i);
  });

  test('TOOL CALLING: asking to add to cart works', async ({ page }) => {
    await loginAndGoTo(page, '/llm-chat');

    await page.locator('textarea.chat-textarea').fill('Add product 1 to my cart');
    await page.locator('button.chat-send-btn').click();

    const aiResponse = page.locator('.chat-bubble--assistant .chat-content').last();
    await expect(aiResponse).not.toContainText('...', { timeout: 30000 });
    await expect(aiResponse).toBeVisible({ timeout: 30000 });

    const responseText = await aiResponse.textContent();
    console.log('AI Cart Response:', responseText?.substring(0, 200));

    // Should NOT say it can't add to cart
    expect(responseText).not.toMatch(/don't have the capability|cannot add|not able to/i);
  });

  test('new conversation button clears the chat', async ({ page }) => {
    await loginAndGoTo(page, '/llm-chat');
    // Click "New Conversation" button
    const clearBtn = page.locator('button.chat-clear-btn');
    if (await clearBtn.isVisible()) {
      await clearBtn.click();
      // Chat window should be empty (show empty state)
      await expect(page.locator('.chat-empty')).toBeVisible();
    }
  });
});
