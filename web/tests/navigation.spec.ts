import { expect, test } from '@playwright/test';

test('primary routes and focused surfaces are available', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveURL(/\/atlas$/);
  await expect(page.getByRole('heading', { name: 'Atlas' })).toBeVisible();
  await page.getByRole('link', { name: 'Library' }).click();
  await expect(page.getByRole('heading', { name: 'Library' })).toBeVisible();
  await page.getByRole('link', { name: 'Runs' }).click();
  await expect(page.getByRole('heading', { name: 'Runs' })).toBeVisible();
  await page.getByRole('link', { name: 'Analysis' }).click();
  await expect(page.getByRole('heading', { name: 'Analysis' })).toBeVisible();
});

test('command palette opens from keyboard', async ({ page }) => {
  await page.goto('/atlas');
  await expect(page.locator('.app-shell')).toHaveAttribute('data-ready', 'true');
  await page.keyboard.press('Control+K');
  await expect(page.getByRole('dialog', { name: 'Command palette' })).toBeVisible();
});
