import fs from 'node:fs'
import { expect, test } from '@playwright/test'

const username = process.env.M2_OPERATOR_USERNAME
const password = process.env.M2_OPERATOR_PASSWORD

if (!username || !password) {
  throw new Error('M2_OPERATOR_USERNAME and M2_OPERATOR_PASSWORD are required')
}

test('operator can inspect persisted success and failure jobs without mutation controls', async ({ page }) => {
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' })

  await expect(page.getByTestId('login-card')).toBeVisible()
  await page.getByTestId('username').fill(username)
  await page.getByTestId('password').fill(password)
  await page.getByTestId('login-button').click()

  await expect(page.getByTestId('operator-console')).toBeVisible()
  await expect(page.getByTestId('job-list')).toBeVisible()

  const succeededRow = page.getByTestId('job-row-SUCCEEDED').first()
  const failedRow = page.getByTestId('job-row-FAILED').first()
  await expect(succeededRow).toBeVisible()
  await expect(failedRow).toBeVisible()

  await succeededRow.click()
  await expect(page.getByTestId('job-status')).toHaveText('SUCCEEDED')
  await expect(page.getByTestId('job-result')).toBeVisible()
  const successText = (await page.getByTestId('job-result').innerText()).trim()
  expect(successText.length).toBeGreaterThan(20)
  await page.screenshot({ path: 'm2-success-job.png', fullPage: true })

  await failedRow.click()
  await expect(page.getByTestId('job-status')).toHaveText('FAILED')
  await expect(page.getByTestId('job-error')).toContainText('M2_DETERMINISTIC_FAILURE')
  await page.screenshot({ path: 'm2-failed-job.png', fullPage: true })

  const mutationButtons = page.locator('button').filter({ hasText: /redrive|retry|recover/i })
  await expect(mutationButtons).toHaveCount(0)

  const evidence = {
    status: 'PASS',
    surface: 'read-only-operator-console',
    successVisible: true,
    failureVisible: true,
    mutationControlsVisible: false,
    synthetic: true,
  }
  fs.writeFileSync('m2-browser-evidence.json', `${JSON.stringify(evidence, null, 2)}\n`, 'utf8')
})
