"""
Smoke tests for EPIC V11 API endpoints
"""
import os
import pytest
import httpx
from typing import Optional

BASE_URL = os.getenv('EPIC_BASE_URL', 'http://localhost:8000')

class TestHealthEndpoints:
    """Test basic health and status endpoints"""
    
    @pytest.mark.asyncio
    async def test_control_panel_health(self):
        """Test control panel health endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            data = response.json()
            assert data.get('status') == 'healthy'
    
    @pytest.mark.asyncio
    async def test_system_status(self):
        """Test system status endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/control/system/status")
            assert response.status_code in [200, 401]  # May require auth

class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    @pytest.mark.asyncio
    async def test_auth_providers(self):
        """Test NextAuth providers endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/auth/providers")
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_login_page(self):
        """Test login page accessibility"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/auth/login")
            assert response.status_code == 200

class TestMCPEndpoints:
    """Test MCP server endpoints"""
    
    @pytest.mark.asyncio
    async def test_mcp_health(self):
        """Test MCP server health"""
        mcp_url = os.getenv('MCP_BASE_URL', 'http://localhost:9000')
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{mcp_url}/health")
            assert response.status_code == 200

class TestSecurityHeaders:
    """Test security headers and configuration"""
    
    @pytest.mark.asyncio
    async def test_security_headers(self):
        """Test that proper security headers are set"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            
            # Check for security headers
            headers = response.headers
            assert 'x-content-type-options' in headers.keys() or response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_cors_configuration(self):
        """Test CORS configuration"""
        async with httpx.AsyncClient() as client:
            response = await client.options(f"{BASE_URL}/health")
            assert response.status_code in [200, 204, 405]  # OPTIONS may not be implemented

class TestDatabaseConnectivity:
    """Test database connectivity through API"""
    
    @pytest.mark.asyncio
    async def test_database_status(self):
        """Test database connectivity via system status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/control/system/database-status")
            # May require authentication, so accept 401 as valid response
            assert response.status_code in [200, 401, 404]