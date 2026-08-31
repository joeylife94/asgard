import { useCallback, useEffect, useMemo, useState } from 'react'

const API_BASE = (import.meta.env.VITE_HEIMDALL_API_URL || 'http://localhost:8080').replace(/\/$/, '')
const RECOVERY_ENABLED = import.meta.env.VITE_ENABLE_RECOVERY === 'true'

function formatTimestamp(value) {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString()
}

function statusClass(status) {
  return `status-pill status-${String(status || 'unknown').toLowerCase()}`
}

async function request(path, options = {}, token = null) {
  const headers = new Headers(options.headers || {})
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })

  let body = null
  const text = await response.text()
  if (text) {
    try {
      body = JSON.parse(text)
    } catch {
      body = text
    }
  }

  if (!response.ok) {
    const message = typeof body === 'object' && body?.error
      ? body.error
      : response.status === 429
        ? 'Redrive rate limit exceeded. Try again later.'
        : `Request failed (${response.status})`
    throw new Error(message)
  }

  return body
}

function Login({ onLogin, busy, error }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  async function submit(event) {
    event.preventDefault()
    await onLogin(username, password)
  }

  return (
    <main className="login-shell">
      <section className="login-card" aria-labelledby="asgard-title" data-testid="login-card">
        <p className="eyebrow">Local AI Operations Tool</p>
        <h1 id="asgard-title">Asgard</h1>
        <p className="status-copy">
          Sign in with the configured Heimdall operator account to inspect persisted analysis jobs.
        </p>

        <form className="login-form" onSubmit={submit}>
          <label>
            Username
            <input
              data-testid="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label>
            Password
            <input
              data-testid="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <p className="error-banner" role="alert">{error}</p> : null}
          <button data-testid="login-button" type="submit" disabled={busy}>
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </section>
    </main>
  )
}

function AuditHistory({ audits }) {
  if (!RECOVERY_ENABLED) return null

  return (
    <div className="audit-block" data-testid="redrive-audit">
      <h3>Redrive audit</h3>
      {audits.length === 0 ? (
        <p className="empty-audit">No redrive audit entries for this job.</p>
      ) : (
        <div className="audit-list">
          {audits.map((audit) => (
            <article className="audit-row" key={audit.id} data-testid={`audit-${audit.outcome}`}>
              <div className="audit-heading">
                <strong>{audit.outcome}</strong>
                <span>{formatTimestamp(audit.performedAt)}</span>
              </div>
              <p>Previous: {audit.previousStatus || '—'} / attempt {audit.previousAttemptCount ?? '—'}</p>
              <p>Reason: {audit.reason || '—'}</p>
              <p>Operator: {audit.performedBy || '—'}</p>
              {audit.errorMessage ? <p className="audit-error">{audit.errorMessage}</p> : null}
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

function RecoveryPanel({ job, audits, busy, onRedrive }) {
  const [reason, setReason] = useState('')
  const [confirmed, setConfirmed] = useState(false)

  useEffect(() => {
    setReason('')
    setConfirmed(false)
  }, [job?.jobId])

  if (!RECOVERY_ENABLED || !job) return null

  const hasRecoveryAudit = audits.some((audit) => audit.outcome === 'SUCCESS')
  const canRecover = job.status === 'FAILED'
  const canVerifyDuplicate = job.status === 'SUCCEEDED' && hasRecoveryAudit

  if (!canRecover && !canVerifyDuplicate) return null

  const actionLabel = canRecover ? 'Redrive failed job' : 'Verify duplicate redrive'
  const disabled = busy || !reason.trim() || !confirmed

  async function submit(event) {
    event.preventDefault()
    await onRedrive(reason.trim())
    setReason('')
    setConfirmed(false)
  }

  return (
    <form className="recovery-panel" onSubmit={submit} data-testid="recovery-panel">
      <div>
        <p className="section-label">Controlled recovery</p>
        <h3>{actionLabel}</h3>
        <p className="recovery-copy">
          {canRecover
            ? 'This sends one authorized retry through the existing recovery path.'
            : 'This intentionally calls redrive again to confirm the backend records SKIPPED without incrementing attempts.'}
        </p>
      </div>
      <label className="reason-field">
        Operator reason
        <textarea
          data-testid="redrive-reason"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          rows="3"
          placeholder="Why is this redrive being performed?"
          required
        />
      </label>
      <label className="confirmation-field">
        <input
          data-testid="redrive-confirmation"
          type="checkbox"
          checked={confirmed}
          onChange={(event) => setConfirmed(event.target.checked)}
        />
        <span>I confirm this is an explicit operator recovery action for this selected job.</span>
      </label>
      <button className="danger-button" data-testid="redrive-button" type="submit" disabled={disabled}>
        {busy ? 'Executing…' : actionLabel}
      </button>
    </form>
  )
}

function JobDetail({ job, loading, audits, recoveryBusy, onRedrive }) {
  if (loading) {
    return <section className="detail-panel" data-testid="job-detail">Loading job detail…</section>
  }

  if (!job) {
    return (
      <section className="detail-panel empty-detail" data-testid="job-detail">
        Select a job to inspect its persisted lifecycle state.
      </section>
    )
  }

  const payload = job.resultPayload && Object.keys(job.resultPayload).length > 0
    ? JSON.stringify(job.resultPayload, null, 2)
    : null

  return (
    <section className="detail-panel" data-testid="job-detail">
      <div className="detail-heading">
        <div>
          <p className="section-label">Job detail</p>
          <h2>{job.jobId}</h2>
        </div>
        <span className={statusClass(job.status)} data-testid="job-status">{job.status}</span>
      </div>

      <dl className="metadata-grid">
        <div><dt>Created</dt><dd>{formatTimestamp(job.createdAt)}</dd></div>
        <div><dt>Started</dt><dd>{formatTimestamp(job.startedAt)}</dd></div>
        <div><dt>Finished</dt><dd>{formatTimestamp(job.finishedAt)}</dd></div>
        <div><dt>Attempt</dt><dd data-testid="job-attempt">{job.attemptCount ?? 0}</dd></div>
        <div><dt>Log ID</dt><dd>{job.logId ?? '—'}</dd></div>
        <div><dt>Result ref</dt><dd>{job.resultRef ?? '—'}</dd></div>
        <div className="wide"><dt>Trace ID</dt><dd>{job.traceId || '—'}</dd></div>
        <div className="wide"><dt>Idempotency key</dt><dd>{job.idempotencyKey || '—'}</dd></div>
      </dl>

      {job.status === 'SUCCEEDED' ? (
        <div className="result-block" data-testid="job-result">
          <h3>Persisted result</h3>
          <p>{job.resultSummary || 'No result summary was persisted.'}</p>
          {payload ? <pre>{payload}</pre> : null}
        </div>
      ) : null}

      {job.status === 'FAILED' ? (
        <div className="error-block" data-testid="job-error">
          <h3>Persisted failure</h3>
          <p><strong>{job.errorCode || 'FAILED'}</strong></p>
          <p>{job.errorMessage || 'No error message was persisted.'}</p>
        </div>
      ) : null}

      <RecoveryPanel job={job} audits={audits} busy={recoveryBusy} onRedrive={onRedrive} />
      <AuditHistory audits={audits} />
    </section>
  )
}

export default function App() {
  const [token, setToken] = useState(null)
  const [username, setUsername] = useState(null)
  const [jobs, setJobs] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [selectedJob, setSelectedJob] = useState(null)
  const [audits, setAudits] = useState([])
  const [busy, setBusy] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [recoveryBusy, setRecoveryBusy] = useState(false)
  const [error, setError] = useState(null)

  const selectedListJob = useMemo(
    () => jobs.find((job) => job.jobId === selectedId) || null,
    [jobs, selectedId],
  )

  const loadJobs = useCallback(async (activeToken) => {
    const page = await request('/api/v1/analysis/jobs?page=0&size=20', {}, activeToken)
    const content = Array.isArray(page?.content) ? page.content : []
    setJobs(content)
    setSelectedId((current) => current && content.some((job) => job.jobId === current)
      ? current
      : content[0]?.jobId || null)
  }, [])

  const loadSelected = useCallback(async (activeToken, jobId) => {
    const job = await request(`/api/v1/analysis/jobs/${jobId}`, {}, activeToken)
    setSelectedJob(job)
    if (RECOVERY_ENABLED) {
      const history = await request(`/api/v1/analysis/jobs/${jobId}/redrive/audit`, {}, activeToken)
      setAudits(Array.isArray(history) ? history : [])
    } else {
      setAudits([])
    }
    return job
  }, [])

  async function login(nextUsername, password) {
    setBusy(true)
    setError(null)
    try {
      const response = await request('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: nextUsername, password }),
      })
      setToken(response.token)
      setUsername(response.username || nextUsername)
      await loadJobs(response.token)
    } catch (nextError) {
      setError(nextError.message)
      setToken(null)
      setUsername(null)
    } finally {
      setBusy(false)
    }
  }

  async function refresh() {
    if (!token) return
    setBusy(true)
    setError(null)
    try {
      await loadJobs(token)
      if (selectedId) await loadSelected(token, selectedId)
    } catch (nextError) {
      setError(nextError.message)
    } finally {
      setBusy(false)
    }
  }

  async function redrive(reason) {
    if (!token || !selectedId) return
    setRecoveryBusy(true)
    setError(null)
    try {
      const beforeAttempt = selectedJob?.attemptCount ?? selectedListJob?.attemptCount ?? 0
      await request(`/api/v1/analysis/jobs/${selectedId}/redrive`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      }, token)

      let latest = null
      for (let attempt = 0; attempt < 180; attempt += 1) {
        latest = await request(`/api/v1/analysis/jobs/${selectedId}`, {}, token)
        setSelectedJob(latest)
        if (latest.status === 'SUCCEEDED' || latest.status === 'FAILED') break
        await new Promise((resolve) => setTimeout(resolve, 2000))
      }

      await loadJobs(token)
      await loadSelected(token, selectedId)

      if (latest?.status === 'SUCCEEDED' && latest.attemptCount < beforeAttempt) {
        throw new Error('Persisted attempt count regressed after redrive.')
      }
    } catch (nextError) {
      setError(nextError.message)
      try {
        await loadSelected(token, selectedId)
      } catch {
        // Preserve the primary redrive failure for the operator.
      }
    } finally {
      setRecoveryBusy(false)
    }
  }

  useEffect(() => {
    if (!token || !selectedId) {
      setSelectedJob(null)
      setAudits([])
      return
    }

    let cancelled = false
    setDetailLoading(true)
    Promise.all([
      request(`/api/v1/analysis/jobs/${selectedId}`, {}, token),
      RECOVERY_ENABLED
        ? request(`/api/v1/analysis/jobs/${selectedId}/redrive/audit`, {}, token)
        : Promise.resolve([]),
    ])
      .then(([job, history]) => {
        if (!cancelled) {
          setSelectedJob(job)
          setAudits(Array.isArray(history) ? history : [])
        }
      })
      .catch((nextError) => {
        if (!cancelled) setError(nextError.message)
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false)
      })

    return () => { cancelled = true }
  }, [selectedId, token])

  if (!token) {
    return <Login onLogin={login} busy={busy} error={error} />
  }

  return (
    <main className="console-shell" data-testid="operator-console">
      <header className="topbar">
        <div>
          <p className="eyebrow">Local AI Operations Tool</p>
          <h1>Asgard</h1>
        </div>
        <div className="topbar-actions">
          <span className="operator-chip">Operator: {username}</span>
          <button className="secondary-button" type="button" onClick={refresh} disabled={busy || recoveryBusy}>
            {busy ? 'Refreshing…' : 'Refresh'}
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={() => {
              setToken(null)
              setUsername(null)
              setJobs([])
              setSelectedId(null)
              setSelectedJob(null)
              setAudits([])
              setError(null)
            }}
          >
            Sign out
          </button>
        </div>
      </header>

      {error ? <p className="error-banner console-error" role="alert">{error}</p> : null}

      <section className="console-grid">
        <aside className="jobs-panel" aria-label="Recent analysis jobs">
          <div className="panel-heading">
            <div>
              <p className="section-label">{RECOVERY_ENABLED ? 'Operator workflow' : 'Read-only'}</p>
              <h2>Recent jobs</h2>
            </div>
            <span className="count-badge">{jobs.length}</span>
          </div>

          <div className="job-list" data-testid="job-list">
            {jobs.length === 0 ? (
              <p className="empty-state">No persisted jobs found.</p>
            ) : jobs.map((job) => (
              <button
                type="button"
                key={job.jobId}
                className={`job-row ${job.jobId === selectedId ? 'selected' : ''}`}
                onClick={() => setSelectedId(job.jobId)}
                data-testid={`job-row-${job.status}`}
              >
                <span className={statusClass(job.status)}>{job.status}</span>
                <strong>{job.jobId}</strong>
                <span>{formatTimestamp(job.createdAt)}</span>
                <span>Attempt {job.attemptCount ?? 0}</span>
              </button>
            ))}
          </div>
        </aside>

        <JobDetail
          job={selectedJob || selectedListJob}
          loading={detailLoading}
          audits={audits}
          recoveryBusy={recoveryBusy}
          onRedrive={redrive}
        />
      </section>

      <footer className="read-only-note">
        {RECOVERY_ENABLED
          ? 'M3 enables only the bounded redrive/audit workflow for the selected job; arbitrary job mutation remains unavailable.'
          : 'M2 is intentionally read-only. Recovery/redrive controls remain outside this milestone.'}
      </footer>
    </main>
  )
}
