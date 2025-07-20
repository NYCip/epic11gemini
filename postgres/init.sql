-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create databases
CREATE DATABASE langfuse;
CREATE DATABASE n8n;

-- MCP Tools Registry
CREATE TABLE IF NOT EXISTS mcp_tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    version VARCHAR(50) NOT NULL,
    description TEXT,
    capabilities JSONB NOT NULL,
    verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(255),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- MCP Tool Logs
CREATE TABLE IF NOT EXISTS mcp_tool_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id UUID REFERENCES mcp_tools(id),
    action VARCHAR(255) NOT NULL,
    agent_name VARCHAR(255),
    parameters JSONB,
    result JSONB,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Users table with RBAC
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'operator', 'viewer')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    mfa_secret VARCHAR(255),
    mfa_enabled BOOLEAN DEFAULT false
);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- System Override Log
CREATE TABLE IF NOT EXISTS system_override (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status VARCHAR(50) NOT NULL,
    initiated_by UUID REFERENCES users(id),
    reason TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Board Decision Log
CREATE TABLE IF NOT EXISTS board_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task JSONB NOT NULL,
    risk_assessments JSONB NOT NULL,
    approved BOOLEAN NOT NULL,
    reason TEXT,
    execution_result JSONB,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_mcp_tool_logs_timestamp ON mcp_tool_logs(timestamp);
CREATE INDEX idx_board_decisions_timestamp ON board_decisions(timestamp);

-- Create Edward as first admin (password must be updated via script)
INSERT INTO users (email, password_hash, full_name, role)
VALUES ('eip @iug.net', 'REPLACE_WITH_BCRYPT_HASH', 'Edward Ip', 'admin')
ON CONFLICT (email) DO NOTHING;
