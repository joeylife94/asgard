# Rate Limit Policy (Heimdall)

This document defines the **default rate limits** for Heimdall endpoints and how to apply them.

## Principles

- Rate limiting is enforced by `RateLimitInterceptor` on controller methods annotated with `@RateLimit`.
- Limits should be defined per endpoint based on risk and cost.
- Authentication endpoints must avoid self-denial (e.g., login should not be rate-limited by the same rule set).

## Default Limits (proposed)

| Endpoint | Method | Key | Limit | Window | Notes |
|---|---:|---|---:|---|---|
| `/api/v1/auth/login` | POST | IP | 20 | 1 minute | Prevent brute force |
| `/api/v1/auth/me` | GET | USER | 120 | 1 minute | Lightweight |
| `/api/v1/logs` | POST | API_KEY | 300 | 1 minute | Ingestion |
| `/api/v1/logs/search` | GET | USER | 120 | 1 minute | Read-heavy |
| `/api/bifrost/analyze` | POST | USER | 100 | 1 hour | Expensive (AI) |
| `/api/bifrost/analyze/async` | POST | USER | 100 | 1 hour | Expensive (AI) |
| `/api/bifrost/history` | GET | USER | 200 | 1 hour | Read |

## Implementation Notes

- Use `@RateLimit(maxRequests=..., duration=..., timeUnit=..., keyType=...)` on controller methods.
- Recommended `keyType`:
  - Auth/login: `IP`
  - User endpoints: `USER`
  - Service-to-service ingestion: `API_KEY`

## Verification

```powershell
.\gradlew.bat :heimdall:test --no-daemon
```
