import { test, expect } from '@playwright/test';

test.describe('Backend API Health', () => {
  test('e-commerce API is reachable', async ({ request }) => {
    const res = await request.get('http://localhost:8000/products');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(Array.isArray(body)).toBeTruthy();
    console.log(`Products in DB: ${body.length}`);
    body.forEach((p: any) => console.log(`  - [${p.id}] ${p.name} $${p.price}`));
  });

  test('LLM chatbot health endpoint is OK', async ({ request }) => {
    const res = await request.get('http://localhost:8002/api/v1/health');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body.status).toBe('ok');
    console.log('Chatbot version:', body.version);
  });

  test('TOOL CALLING: chatbot calls list_all_products tool', async ({ request }) => {
    const res = await request.post('http://localhost:8002/api/v1/chat-llm', {
      data: {
        session_id: `playwright-${Date.now()}`,
        message: 'What products do you sell?',
      },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    console.log('Response:', body.response?.substring(0, 300));

    // Should NOT contain the "retrieved context" fallback message
    expect(body.response).not.toMatch(/retrieved context does not|cannot provide/i);
    // Should contain product-related info (prices, names)
    expect(body.response).toMatch(/\$|product|sell|available/i);
  });

  test('TOOL CALLING: chatbot searches products', async ({ request }) => {
    const res = await request.post('http://localhost:8002/api/v1/chat-llm', {
      data: {
        session_id: `playwright-search-${Date.now()}`,
        message: 'Search for keyboard',
      },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    console.log('Search Response:', body.response?.substring(0, 300));
    expect(body.response).not.toMatch(/cannot|don't have/i);
  });

  test('TOOL CALLING: chatbot can view cart', async ({ request }) => {
    const res = await request.post('http://localhost:8002/api/v1/chat-llm', {
      data: {
        session_id: `playwright-cart-${Date.now()}`,
        message: 'Show me my cart',
      },
    });
    expect(res.status()).toBe(200);
    const body = await res.json();
    console.log('Cart Response:', body.response?.substring(0, 300));
    expect(res.status()).toBe(200);
  });

  test('cart API returns valid structure', async ({ request }) => {
    const res = await request.get('http://localhost:8000/cart');
    expect(res.status()).toBe(200);
    const body = await res.json();
    expect(body).toHaveProperty('items');
    expect(body).toHaveProperty('total');
    console.log(`Cart: ${body.items.length} items, total $${body.total}`);
  });
});
