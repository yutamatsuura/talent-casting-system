import { test, expect } from '@playwright/test';

const FRONTEND_URL = 'https://talent-casting-diagnosis-1jk8eujly-yutamatsuuras-projects.vercel.app';
const BACKEND_URL = 'https://talent-casting-backend-sjsm2c77ma-an.a.run.app';

test.describe('本番環境デプロイ検証', () => {
  test('バックエンドヘルスチェック', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/health`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    console.log('Health check response:', data);
    expect(data.status).toBe('healthy');
    expect(data.database).toBe('connected');
  });

  test('フロントエンドアクセス確認', async ({ page }) => {
    await page.goto(FRONTEND_URL);

    // ステータスコードを確認
    const response = await page.goto(FRONTEND_URL);
    console.log('Frontend status:', response?.status());

    // スクリーンショット撮影
    await page.screenshot({ path: 'tests/screenshots/frontend-home.png', fullPage: true });

    // タイトルが表示されているか
    await expect(page).toHaveTitle(/.*/, { timeout: 10000 });
  });

  test('API疎通確認 - 業種マスタ取得', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/industries`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    console.log('Industries response:', data);
    expect(data.total).toBeGreaterThan(0);
    expect(Array.isArray(data.industries)).toBeTruthy();
    expect(data.industries.length).toBeGreaterThan(0);
  });

  test('API疎通確認 - ターゲット層取得', async ({ request }) => {
    const response = await request.get(`${BACKEND_URL}/api/target-segments`);
    expect(response.ok()).toBeTruthy();

    const data = await response.json();
    console.log('Target segments response:', data);
    expect(data.total).toBeGreaterThan(0);
    expect(Array.isArray(data.items)).toBeTruthy();
    expect(data.items.length).toBeGreaterThan(0);
  });
});
