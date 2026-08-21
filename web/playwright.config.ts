import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  use: { baseURL: process.env.ALPS_E2E_URL || 'http://127.0.0.1:8787', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: process.env.ALPS_E2E_URL ? undefined : { command: 'echo "Set ALPS_E2E_URL to a running Runtime" && exit 1', port: 8787, reuseExistingServer: true }
});
