import pytest
from agno_service.workspace.risk_management import (
    RiskManagementFramework, 
    RiskLevel,
    RiskCategory
)

class TestRiskAssessment:
    @pytest.fixture
    def risk_framework(self):
        return RiskManagementFramework("TEST_AGENT")
    
    @pytest.mark.asyncio
    async def test_low_risk_action(self, risk_framework):
        task = {
            "action": "read_file",
            "context": {"filename": "readme.txt"}
        }
        
        assessment = await risk_framework.assess_risk(task)
        assert assessment.risk_level == RiskLevel.LOW
        assert not assessment.requires_human_approval
    
    @pytest.mark.asyncio
    async def test_high_risk_financial(self, risk_framework):
        task = {
            "action": "transfer_funds",
            "context": {"amount": 50000, "recipient": "external"}
        }
        
        assessment = await risk_framework.assess_risk(task)
        assert assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert assessment.requires_human_approval
        assert RiskCategory.FINANCIAL in assessment.categories
    
    @pytest.mark.asyncio
    async def test_extreme_risk_family_data(self, risk_framework):
        task = {
            "action": "share_family_photos",
            "context": {"destination": "public_website"}
        }
        
        assessment = await risk_framework.assess_risk(task)
        assert assessment.risk_level == RiskLevel.EXTREME
        assert assessment.requires_human_approval
        assert RiskCategory.PRIVACY in assessment.categories
    
    @pytest.mark.asyncio
    async def test_board_consensus_approved(self, risk_framework):
        # Create mock assessments
        assessments = []
        for i in range(11):
            assessment = await risk_framework.assess_risk({
                "action": "routine_task",
                "context": {}
            })
            assessment.risk_level = RiskLevel.LOW if i < 8 else RiskLevel.MEDIUM
            assessments.append(assessment)
        
        approved, reason = await risk_framework.get_board_consensus(assessments)
        assert approved
        assert "approval granted" in reason
    
    @pytest.mark.asyncio
    async def test_board_consensus_veto(self, risk_framework):
        # Create assessments with CSO veto
        assessments = []
        for i in range(11):
            assessment = await risk_framework.assess_risk({
                "action": "risky_action",
                "context": {}
            })
            if i == 3:  # CSO
                assessment.assessed_by = "CSO_Sentinel"
                assessment.risk_level = RiskLevel.CRITICAL
            assessments.append(assessment)
        
        approved, reason = await risk_framework.get_board_consensus(assessments)
        assert not approved
        assert "VETO" in reason
