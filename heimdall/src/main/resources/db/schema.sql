-- PostgreSQL Schema for Heimdall

-- Log Entries Table
CREATE TABLE IF NOT EXISTS log_entries (
    id BIGSERIAL PRIMARY KEY,
    event_id VARCHAR(36) UNIQUE NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source VARCHAR(100) NOT NULL,
    service_name VARCHAR(100),
    environment VARCHAR(50),
    severity VARCHAR(20) NOT NULL,
    log_content TEXT NOT NULL,
    log_hash VARCHAR(64) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for log_entries
CREATE INDEX IF NOT EXISTS idx_log_entries_timestamp ON log_entries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_log_entries_service_env ON log_entries(service_name, environment);
CREATE INDEX IF NOT EXISTS idx_log_entries_severity ON log_entries(severity);
CREATE INDEX IF NOT EXISTS idx_log_entries_log_hash ON log_entries(log_hash);

-- Analysis Results Table
CREATE TABLE IF NOT EXISTS analysis_results (
    id BIGSERIAL PRIMARY KEY,
    log_id BIGINT NOT NULL REFERENCES log_entries(id) ON DELETE CASCADE,
    bifrost_analysis_id BIGINT,
    request_id VARCHAR(36) UNIQUE NOT NULL,
    correlation_id VARCHAR(36),
    summary TEXT,
    root_cause TEXT,
    recommendation TEXT,
    severity VARCHAR(20),
    confidence DECIMAL(3,2),
    model VARCHAR(100),
    duration_seconds DECIMAL(10,2),
    analyzed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Jobs Table (Kafka control plane orchestration)
CREATE TABLE IF NOT EXISTS analysis_jobs (
    job_id UUID PRIMARY KEY,
    idempotency_key VARCHAR(200) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    finished_at TIMESTAMP,
    trace_id VARCHAR(128),
    model_policy JSONB,
    log_id BIGINT,
    input_ref VARCHAR(200),
    result_ref BIGINT,
    result_summary TEXT,
    result_payload JSONB,
    error_code VARCHAR(100),
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_analysis_jobs_status_created ON analysis_jobs(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_jobs_log_id ON analysis_jobs(log_id);

-- Indexes for analysis_results
CREATE INDEX IF NOT EXISTS idx_analysis_results_log_id ON analysis_results(log_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_analyzed_at ON analysis_results(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_severity ON analysis_results(severity);

-- Log Statistics Table
CREATE TABLE IF NOT EXISTS log_statistics (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    hour SMALLINT NOT NULL,
    service_name VARCHAR(100),
    environment VARCHAR(50),
    severity VARCHAR(20),
    count INTEGER NOT NULL DEFAULT 0,
    avg_size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, hour, service_name, environment, severity)
);

-- Indexes for log_statistics
CREATE INDEX IF NOT EXISTS idx_log_statistics_date_hour ON log_statistics(date, hour);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGSERIAL PRIMARY KEY,
    log_id BIGINT REFERENCES log_entries(id) ON DELETE SET NULL,
    analysis_id BIGINT REFERENCES analysis_results(id) ON DELETE SET NULL,
    type VARCHAR(50) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    recipient VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for notifications
CREATE INDEX IF NOT EXISTS idx_notifications_sent_at ON notifications(sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);

-- Redrive Audit Logs Table (for DLQ operation auditing)
CREATE TABLE IF NOT EXISTS redrive_audit_logs (
    id BIGSERIAL PRIMARY KEY,
    job_id UUID NOT NULL,
    idempotency_key VARCHAR(200),
    previous_status VARCHAR(20),
    previous_attempt_count INTEGER,
    performed_by VARCHAR(200) NOT NULL,
    performed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(50),
    user_agent VARCHAR(500),
    trace_id VARCHAR(128),
    reason VARCHAR(500),
    outcome VARCHAR(20) NOT NULL,
    error_message TEXT
);

-- Indexes for redrive_audit_logs
CREATE INDEX IF NOT EXISTS idx_redrive_audit_job_id ON redrive_audit_logs(job_id);
CREATE INDEX IF NOT EXISTS idx_redrive_audit_performed_at ON redrive_audit_logs(performed_at DESC);
CREATE INDEX IF NOT EXISTS idx_redrive_audit_performed_by ON redrive_audit_logs(performed_by);
