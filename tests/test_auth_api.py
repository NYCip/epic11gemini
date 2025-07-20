import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
import asyncio
from control_panel_backend.app.main import app
from control_panel_backend.app.auth import auth_service

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class TestAuthentication:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_login_success(self, client):
        # First create a test user
        test_password = "TestPassword123!"
        hashed = auth_service.get_password_hash(test_password)
        
        # Login
        response = client.post(
            "/control/auth/token",
            data={
                "username": "test @epic.pos.com",
                "password": test_password
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_invalid_credentials(self, client):
        response = client.post(
            "/control/auth/token",
            data={
                "username": "invalid @epic.pos.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_protected_endpoint(self, async_client):
        # Get token first
        login_response = await async_client.post(
            "/control/auth/token",
            data={
                "username": "eip @iug.net",
                "password": "correct_password"
            }
        )
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = await async_client.get(
            "/control/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "eip @iug.net"

class TestRBAC:
    @pytest.mark.asyncio
    async def test_admin_only_endpoint(self, async_client):
        # Test with operator token - should fail
        operator_token = "..."  # Get operator token
        
        response = await async_client.post(
            "/control/system/override/halt",
            headers={"Authorization": f"Bearer {operator_token}"},
            json={
                "action": "HALT",
                "reason": "Test",
                "confirmation_code": "EDWARD-ALPHA-OVERRIDE"
            }
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio  
    async def test_edward_override(self, async_client):
        # Get admin token
        admin_token = "..."  # Get Edward's token
        
        response = await async_client.post(
            "/control/system/override/halt",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "action": "HALT", 
                "reason": "Emergency test",
                "confirmation_code": "EDWARD-ALPHA-OVERRIDE"
            }
        )
        assert response.status_code == 200
        assert "HALTED" in response.json()["message"]
