import pytest
import docker
import time
import requests
from typing import Dict

class TestSystemIntegration:
    @pytest.fixture(scope="class")
    def docker_client(self):
        return docker.from_env()
    
    @pytest.fixture(scope="class") 
    def running_system(self, docker_client):
        """Start the entire system"""
        # Run docker-compose up
        project = docker_client.api.create_project(
            "epic_v11",
            "./docker-compose.yml"
        )
        project.up()
        
        # Wait for services to be healthy
        time.sleep(60)
        
        yield project
        
        # Teardown
        project.down()
    
    def test_all_services_healthy(self, running_system):
        """Verify all services are running and healthy"""
        services = [
            ("https://epic.pos.com/health", "control_panel"),
            ("https://epic.pos.com/agno/health", "agno_service"),
            ("http://localhost:9000/health", "mcp_server"),
            ("https://langfuse.epic.pos.com", "langfuse")
        ]
        
        for url, service in services:
            response = requests.get(url, verify=False)
            assert response.status_code == 200, f"{service} is not healthy"
    
    def test_end_to_end_board_decision(self, running_system):
        """Test complete flow from login to board decision"""
        
        # 1. Login as Edward
        login_response = requests.post(
            "https://epic.pos.com/control/auth/token",
            data={
                "username": "eip @iug.net",
                "password": "test_password"
            },
            verify=False
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 2. Submit task to board
        headers = {"Authorization": f"Bearer {token}"}
        task_response = requests.post(
            "https://epic.pos.com/board/decision",
            headers=headers,
            json={
                "query": "Analyze the security of our current setup",
                "context": {"priority": "high"}
            },
            verify=False
        )
        assert task_response.status_code == 200
        
        result = task_response.json()
        assert result["approved"] == True
        assert len(result["risk_assessments"]) >= 4  # At least key members
    
    def test_edward_override_integration(self, running_system):
        """Test Edward Override affects all services"""
        
        # Login and get admin token
        token = self._get_admin_token()
        
        # Activate override
        override_response = requests.post(
            "https://epic.pos.com/control/system/override/halt",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action": "HALT",
                "reason": "Integration test",
                "confirmation_code": "EDWARD-ALPHA-OVERRIDE"
            },
            verify=False
        )
        assert override_response.status_code == 200
        
        # Verify AGNO service is halted
        time.sleep(2)  # Allow propagation
        
        board_response = requests.post(
            "https://epic.pos.com/board/decision",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": "test"},
            verify=False
        )
        assert board_response.status_code == 503  # Service unavailable
        
        # Resume system
        resume_response = requests.post(
            "https://epic.pos.com/control/system/override/resume",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "action": "RESUME",
                "reason": "Test complete"
            },
            verify=False
        )
        assert resume_response.status_code == 200
