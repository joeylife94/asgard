import fs from 'node:fs'
import { expect, test } from '@playwright/test'

const username = process.env.M3_OPERATOR_USERNAME
const password = process.env.M3_OPERATOR_PASSWORD

if (!username || !password) {
  throw new Error('M3_OPERATOR_USERNAME and M3_OPERATOR_PASSWORD are required')
}

test('operator performs one controlled recovery and sees duplicate redrive as SKIPPED', async ({ page }) => {
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' })
  await page.getByTestId('username').fill(username)
  await page.getByTestId('password').fill(password)
  await page.getByTestId('login-button').click()

  await expect(page.getByTestId('operator-console')).toBeVisible()
  const failedRow = page.getByTestId('job-row-FAILED').first()
  await expect(failedRow).toBeVisible()
  await failedRow.click()

  await expect(page.getByTestId('job-status')).toHaveText('FAILED')
  await expect(page.getByTestId('job-attempt')).toHaveText('0')
  await expect(page.getByTestId('recovery-panel')).toBeVisible()
  await expect(page.getByTestId('redrive-button')).toBeDisabled()

  await page.getByTestId('redrive-reason').fill('M3 synthetic operator recovery proof')
  await expect(page.getByTestId('redrive-button')).toBeDisabled()
  await page.getByTestId('redrive-confirmation').check()
  await page.screenshot({ path: 'm3-before-redrive.png', fullPage: true })
  await page.getByTestId('redrive-button').click()

  await expect(page.getByTestId('job-status')).toHaveText('SUCCEEDED', { timeout: 360_000 })
  await expect(page.getByTestId('job-attempt')).toHaveText('1')
  await expect(page.getByTestId('audit-SUCCESS').first()).toContainText('Previous: FAILED / attempt 0')
  await expect(page.getByTestId('audit-SUCCESS').first()).toContainText('M3 synthetic operator recovery proof')
  await page.screenshot({ path: 'm3-after-recovery.png', fullPage: true })

  await expect(page.getByTestId('redrive-button')).toContainText('Verify duplicate redrive')
  await page.getByTestId('redrive-reason').fill('M3 duplicate redrive proof')
  await page.getByTestId('redrive-confirmation').check()
  await page.getByTestId('redrive-button').click()

  await expect(page.getByTestId('job-status')).toHaveText('SUCCEEDED', { timeout: 30_000 })
  await expect(page.getByTestId('job-attempt')).toHaveText('1')
  await expect(page.getByTestId('audit-SKIPPED').first()).toBeVisible()
  await expect(page.getByTestId('audit-SKIPPED').first()).toContainText('M3 duplicate redrive proof')
  await page.screenshot({ path: 'm3-duplicate-skipped.png', fullPage: true })

  fs.writeFileSync('m3-browser-evidence.json', `${JSON.stringify({
    status: 'PASS',
    surface: 'controlled-recovery-operator-workflow',
    initialStatus: 'FAILED',
    initialAttempt: 0,
    recoveredStatus: 'SUCCEEDED',
    recoveredAttempt: 1,
    successAuditVisible: true,
    duplicateOutcomeVisible: 'SKIPPED',
    duplicateAttemptUnchanged: true,
    synthetic: true,
    cloudExecution: false,
  }, null, 2)}\n`, 'utf8')
})
