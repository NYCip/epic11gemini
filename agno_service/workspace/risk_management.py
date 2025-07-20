from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXTREME = 5

class RiskCategory(Enum):
    FINANCIAL = "financial"
    SECURITY = "security"
    OPERATIONAL = "operational"
    REPUTATIONAL = "reputational"
    LEGAL = "legal"
    TECHNICAL = "technical"
    PRIVACY = "privacy"

class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=10.0)
    categories: List[RiskCategory]
    pros: List[str]
    cons: List[str]
    mitigation_strategies: List[str]
    requires_human_approval: bool
    confidence_level: float = Field(ge=0.0, le=1.0)
    assessed_by: str
    assessment_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
class RiskManagementFramework:
    """
    V8 Risk Management Framework - Core risk assessment logic
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.risk_history: List[RiskAssessment] = []
        
    async def assess_risk(self, task: Dict) -> RiskAssessment:
        """
        Comprehensive risk assessment for any proposed action
        """
        # Extract task details
        action = task.get("action", "")
        context = task.get("context", {})
        target = task.get("target", "")
        
        # Initialize assessment components
        risk_score = 0.0
        categories = []
        pros = []
        cons = []
        mitigation_strategies = []
        
        # 1. SECURITY RISK ASSESSMENT
        security_score = self._assess_security_risk(action, context)
        if security_score > 0:
            risk_score += security_score
            categories.append(RiskCategory.SECURITY)
            if security_score > 5:
                cons.append(f"High security risk detected (score: {security_score})")
                mitigation_strategies.append("Require additional authentication")
                mitigation_strategies.append("Enable comprehensive audit logging")
        
        # 2. FINANCIAL RISK ASSESSMENT  
        if any(keyword in action.lower() for keyword in ["payment", "transfer", "purchase", "invest"]):
            financial_score = self._assess_financial_risk(action, context)
            risk_score += financial_score
            categories.append(RiskCategory.FINANCIAL)
            if financial_score > 3:
                cons.append("Financial transaction detected")
                mitigation_strategies.append("Require transaction approval")
                mitigation_strategies.append("Set transaction limits")
        
        # 3. PRIVACY RISK ASSESSMENT
        if any(keyword in action.lower() for keyword in ["personal", "private", "family", "edward"]):
            privacy_score = 8.0  # High sensitivity for family data
            risk_score += privacy_score
            categories.append(RiskCategory.PRIVACY)
            cons.append("Potential privacy impact on Edward or family")
            mitigation_strategies.append("Ensure data remains within approved systems")
            mitigation_strategies.append("Apply maximum encryption standards")
        
        # 4. OPERATIONAL RISK ASSESSMENT
        operational_score = self._assess_operational_risk(action, context)
        if operational_score > 0:
            risk_score += operational_score
            categories.append(RiskCategory.OPERATIONAL)
        
        # 5. REPUTATIONAL RISK ASSESSMENT
        if any(keyword in action.lower() for keyword in ["public", "publish", "share", "external"]):
            reputational_score = 4.0
            risk_score += reputational_score
            categories.append(RiskCategory.REPUTATIONAL)
            cons.append("Potential public exposure")
            mitigation_strategies.append("Review content before publication")
        
        # Calculate final risk level
        risk_level = self._calculate_risk_level(risk_score)
        
        # Determine if human approval needed
        requires_human_approval = (
            risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.EXTREME] or
            RiskCategory.PRIVACY in categories or
            risk_score > 15.0
        )
        
        # Add pros if risk is acceptable
        if risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            pros.append("Risk level within acceptable parameters")
            pros.append("Action aligns with EPIC doctrine")
        
        # Create assessment
        assessment = RiskAssessment(
            risk_level=risk_level,
            risk_score=min(risk_score, 10.0),  # Cap at 10
            categories=categories,
            pros=pros,
            cons=cons,
            mitigation_strategies=mitigation_strategies,
            requires_human_approval=requires_human_approval,
            confidence_level=0.85,  # Base confidence
            assessed_by=self.agent_name
        )
        
        # Log assessment
        self.risk_history.append(assessment)
        logger.info(f"Risk Assessment by {self.agent_name}: {assessment.model_dump_json()}")
        
        return assessment
    
    def _assess_security_risk(self, action: str, context: Dict) -> float:
        """Assess security-related risks"""
        score = 0.0
        
        # Check for dangerous keywords
        dangerous_keywords = ["sudo", "admin", "root", "password", "credential", "key", "token"]
        for keyword in dangerous_keywords:
            if keyword in action.lower():
                score += 3.0
        
        # Check for system modifications
        if any(word in action.lower() for word in ["delete", "remove", "modify", "override"]):
            score += 2.0
            
        # Check for external connections
        if any(word in action.lower() for word in ["connect", "api", "webhook", "external"]):
            score += 1.5
            
        return score
    
    def _assess_financial_risk(self, action: str, context: Dict) -> float:
        """Assess financial risks"""
        score = 0.0
        
        # Check amount if present
        amount = context.get("amount", 0)
        if amount > 10000:
            score += 5.0
        elif amount > 1000:
            score += 3.0
        elif amount > 100:
            score += 1.0
            
        # Check for high-risk financial actions
        if any(word in action.lower() for word in ["wire", "crypto", "investment"]):
            score += 2.0
            
        return score
    
    def _assess_operational_risk(self, action: str, context: Dict) -> float:
        """Assess operational risks"""
        score = 0.0
        
        # Check for service disruption potential
        if any(word in action.lower() for word in ["stop", "halt", "restart", "shutdown"]):
            score += 3.0
            
        # Check for batch operations
        if any(word in action.lower() for word in ["bulk", "mass", "all", "batch"]):
            score += 1.5
            
        return score
    
    def _calculate_risk_level(self, score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if score <= 2:
            return RiskLevel.LOW
        elif score <= 5:
            return RiskLevel.MEDIUM
        elif score <= 8:
            return RiskLevel.HIGH
        elif score <= 12:
            return RiskLevel.CRITICAL
        else:
            return RiskLevel.EXTREME
    
    async def get_board_consensus(self, assessments: List[RiskAssessment]) -> Tuple[bool, str]:
        """
        Determine board consensus based on multiple risk assessments
        Requires 7/11 approval for proceed, with veto power for security agents
        """
        total_members = len(assessments)
        high_risk_votes = sum(1 for a in assessments if a.risk_level.value >= RiskLevel.HIGH.value)
        approval_votes = sum(1 for a in assessments if a.risk_level.value <= RiskLevel.MEDIUM.value)
        
        # Check for veto from CSO or CRO
        veto_agents = ["CSO_Sentinel", "CRO_Guardian", "CQO_Oracle"]
        for assessment in assessments:
            if assessment.assessed_by in veto_agents and assessment.risk_level.value >= RiskLevel.HIGH.value:
                return False, f"VETO by {assessment.assessed_by}: {assessment.cons[0] if assessment.cons else 'High risk detected'}"
        
        # Require 7/11 approval
        if approval_votes >= 7:
            return True, f"Board approval granted ({approval_votes}/{total_members} votes)"
        else:
            return False, f"Insufficient board approval ({approval_votes}/{total_members} votes required: 7/11)"
