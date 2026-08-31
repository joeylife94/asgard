import { useCallback, useEffect, useMemo, useState } from 'react'

const API_BASE = (import.meta.env.VITE_HEIMDALL_API_URL || 'http://localhost:8080').replace(/\/$/, '')

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

function JobDetail({ job, loading }) {
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
        <div><dt>Attempt</dt><dd>{job.attemptCount ?? 0}</dd></div>
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
    </section>
  )
}

export default function App() {
  const [token, setToken] = useState(null)
  const [username, setUsername] = useState(null)
  const [jobs, setJobs] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [selectedJob, setSelectedJob] = useState(null)
  const [busy, setBusy] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
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
    } catch (nextError) {
      setError(nextError.message)
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    if (!token || !selectedId) {
      setSelectedJob(null)
      return
    }

    let cancelled = false
    setDetailLoading(true)
    request(`/api/v1/analysis/jobs/${selectedId}`, {}, token)
      .then((job) => {
        if (!cancelled) setSelectedJob(job)
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
          <button className="secondary-button" type="button" onClick={refresh} disabled={busy}>
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
              <p className="section-label">Read-only</p>
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

        <JobDetail job={selectedJob || selectedListJob} loading={detailLoading} />
      </section>

      <footer className="read-only-note">
        M2 is intentionally read-only. Recovery/redrive controls remain outside this milestone.
      </footer>
    </main>
  )
}
