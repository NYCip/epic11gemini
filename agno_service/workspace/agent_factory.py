from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.llm.anthropic import Anthropic
from phi.llm.google import Gemini
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.pgvector import PgVector
from phi.embedder.openai import OpenAIEmbedder
from typing import List, Dict, Optional
import os
import logging

from .epic_doctrine import EPIC_DOCTRINE, BOARD_ROLES
from .risk_management import RiskManagementFramework
from .tools.mcp_tools import MCPToolkit
from .tools.donna_tools import DonnaProtectionTools

logger = logging.getLogger(__name__)

class DoctrineCompliantAssistant(Assistant):
    """Extended Assistant class with EPIC doctrine compliance"""
    
    def __init__(self, *args, **kwargs):
        # Extract risk framework if provided
        self.risk_framework = kwargs.pop('risk_framework', None)
        super().__init__(*args, **kwargs)
    
    async def assess_risk(self, task: dict):
        """Risk assessment method for doctrine compliance"""
        if self.risk_framework:
            return await self.risk_framework.assess_risk(task)
        else:
            logger.warning(f"No risk framework available for {self.name}")
            return None

class AgentFactory:
    """
    Factory for creating doctrine-compliant PhiData assistants
    Each agent is embedded with EPIC V8 doctrine and risk management
    """
    
    def __init__(self, db_url: str = None):
        self.db_url = db_url or os.getenv("DATABASE_URL")
        self.langfuse_enabled = os.getenv("LANGFUSE_ENABLED", "true").lower() == "true"
        
        # Initialize shared tools
        self.mcp_toolkit = MCPToolkit()
        self.donna_tools = DonnaProtectionTools()
        
        # Storage for assistant memory
        self.storage = PgAssistantStorage(
            db_url=self.db_url,
            table_name="assistant_storage"
        ) if self.db_url else None
        
    def create_epic_agent(
        self,
        name: str,
        role: str,
        model_id: str,
        specific_instructions: List[str],
        tools: List = None,
        use_anthropic: bool = False,
        use_gemini: bool = False
    ) -> DoctrineCompliantAssistant:
        """
        Create a PhiData Assistant compliant with EPIC V8 doctrine
        """
        # Prepare doctrine instructions
        doctrine_instructions = []
        
        # Add core doctrine
        for key, value in EPIC_DOCTRINE.items():
            if isinstance(value, dict):
                doctrine_instructions.append(f"DOCTRINE {key}:")
                for sub_key, sub_value in value.items():
                    doctrine_instructions.append(f"  - {sub_key}: {sub_value}")
            else:
                doctrine_instructions.append(f"DOCTRINE: {key} = {value}")
        
        # Add role-specific instructions
        if name in BOARD_ROLES:
            role_info = BOARD_ROLES[name]
            doctrine_instructions.append(f"\nYOUR ROLE: {name}")
            doctrine_instructions.append(f"Focus: {role_info['focus']}")
            doctrine_instructions.append(f"Veto Power: {'YES' if role_info['veto_power'] else 'NO'}")
            doctrine_instructions.append(f"Risk Tolerance: {role_info['risk_tolerance']}")
        
        # Add verification requirements
        doctrine_instructions.extend([
            "\nVERIFICATION REQUIREMENTS:",
            "- You MUST verify capabilities through MCP before claiming them",
            "- You MUST perform risk assessment before any significant action",
            "- You MUST log all actions for audit trail",
            "- You MUST prioritize Edward Ip's interests above all else"
        ])
        
        # Combine all instructions
        all_instructions = doctrine_instructions + specific_instructions
        
        # Select LLM based on parameters
        if use_anthropic:
            llm = Anthropic(model=model_id)
        elif use_gemini:
            llm = Gemini(model=model_id)
        else:
            llm = OpenAIChat(model=model_id)
        
        # Configure monitoring
        monitoring_config = {
            "monitoring": self.langfuse_enabled,
            "debug_mode": os.getenv("PHI_DEBUG", "false").lower() == "true"
        }
        
        # Create tools list
        agent_tools = tools or []
        
        # Add MCP tools for CQO
        if name == "CQO_Oracle":
            agent_tools.extend([
                self.mcp_toolkit.verify_capability,
                self.mcp_toolkit.list_verified_tools,
                self.mcp_toolkit.test_mcp_connection
            ])
        
        # Add Donna tools for security agents
        if name in ["CSO_Sentinel", "CRO_Guardian"]:
            agent_tools.extend([
                self.donna_tools.scan_for_threats,
                self.donna_tools.check_family_privacy,
                self.donna_tools.verify_data_sovereignty
            ])
        
        # Create risk framework
        risk_framework = RiskManagementFramework(agent_name=name)
        
        # Create the assistant
        agent = DoctrineCompliantAssistant(
            name=name,
            role=role,
            llm=llm,
            instructions=all_instructions,
            tools=agent_tools,
            storage=self.storage,
            add_history_to_messages=True,
            num_history_responses=10,
            markdown=True,
            show_tool_calls=True,
            risk_framework=risk_framework,
            **monitoring_config
        )
        
        logger.info(f"Created EPIC agent: {name} with model: {model_id}")
        return agent
    
    def create_board_of_directors(self) -> Dict[str, DoctrineCompliantAssistant]:
        """
        Create all 11 board members with their specific configurations
        """
        board = {}
        
        # CEO - The Visionary
        board["CEO"] = self.create_epic_agent(
            name="CEO_Visionary",
            role="Strategic Leader & Edward's Primary Representative",
            model_id="gpt-4o",
            specific_instructions=[
                "You are the leader of the board and Edward's primary AI representative",
                "Make strategic decisions that advance Edward's long-term interests",
                "You have veto power over major decisions",
                "Balance innovation with family security"
            ]
        )
        
        # CQO - The Oracle  
        board["CQO"] = self.create_epic_agent(
            name="CQO_Oracle",
            role="Quality Assurance & MCP Verification Specialist",
            model_id="gpt-4o",
            specific_instructions=[
                "You are responsible for verifying ALL capability claims through MCP",
                "Never allow unverified capabilities to be claimed",
                "You have veto power over any unverified actions",
                "Maintain the highest standards of accuracy and truth"
            ]
        )
        
        # CTO - The Architect
        board["CTO"] = self.create_epic_agent(
            name="CTO_Architect", 
            role="Technical Architecture & Implementation Lead",
            model_id="claude-3-5-sonnet-20241022",
            use_anthropic=True,
            specific_instructions=[
                "Design and oversee technical implementations",
                "Ensure all systems are secure, scalable, and maintainable",
                "Focus on open-source solutions and proven technologies",
                "Coordinate with CSO on security architecture"
            ]
        )
        
        # CSO - The Sentinel
        board["CSO"] = self.create_epic_agent(
            name="CSO_Sentinel",
            role="Security Guardian & Threat Analyst",
            model_id="gpt-4o",
            specific_instructions=[
                "You are the primary security guardian with veto power",
                "Assess all actions for security implications",
                "Protect Edward and family's digital assets and privacy",
                "Immediately flag and block any suspicious activities"
            ]
        )
        
        # CDO - The Alchemist
        board["CDO"] = self.create_epic_agent(
            name="CDO_Alchemist",
            role="Data Transformation & Insights Specialist",
            model_id="gemini-2.0-flash-exp",
            use_gemini=True,
            specific_instructions=[
                "Transform raw data into actionable insights",
                "Ensure data privacy and sovereignty",
                "Create valuable analysis for Edward's decision-making",
                "Maintain strict data governance standards"
            ]
        )
        
        # CRO - The Guardian
        board["CRO"] = self.create_epic_agent(
            name="CRO_Guardian",
            role="Risk Assessment & Mitigation Expert",
            model_id="gpt-4o",
            specific_instructions=[
                "You have veto power over high-risk actions",
                "Assess all proposals for potential risks",
                "Develop and enforce risk mitigation strategies",
                "Prioritize family safety and asset protection"
            ]
        )
        
        # COO - The Orchestrator
        board["COO"] = self.create_epic_agent(
            name="COO_Orchestrator",
            role="Operational Excellence & Workflow Optimization",
            model_id="gpt-4o-mini",
            specific_instructions=[
                "Optimize operational workflows and efficiency",
                "Coordinate between board members",
                "Ensure smooth execution of approved plans",
                "Monitor system performance and resource usage"
            ]
        )
        
        # CINO - The Pioneer
        board["CINO"] = self.create_epic_agent(
            name="CINO_Pioneer",
            role="Innovation Scout & Emerging Tech Analyst",
            model_id="claude-3-5-haiku-20241022",
            use_anthropic=True,
            specific_instructions=[
                "Scout emerging technologies and innovations",
                "Propose innovative solutions to challenges",
                "Balance innovation with security and practicality",
                "Research new opportunities for Edward's benefit"
            ]
        )
        
        # CCDO - The Diplomat
        board["CCDO"] = self.create_epic_agent(
            name="CCDO_Diplomat",
            role="External Relations & Partnership Manager",
            model_id="gemini-1.5-flash",
            use_gemini=True,
            specific_instructions=[
                "Manage external communications and partnerships",
                "Protect Edward's reputation and interests",
                "Negotiate favorable terms in all dealings",
                "Maintain professional relationships"
            ]
        )
        
        # CPHO - The Sage
        board["CPHO"] = self.create_epic_agent(
            name="CPHO_Sage",
            role="Ethical Guidance & Philosophical Advisor",
            model_id="gpt-4o",
            specific_instructions=[
                "Provide ethical guidance on all decisions",
                "Ensure actions align with Edward's values",
                "Consider long-term philosophical implications",
                "Guide the board toward wise decisions"
            ]
        )
        
        # CXO - The Catalyst
        board["CXO"] = self.create_epic_agent(
            name="CXO_Catalyst",
            role="Cross-functional Innovation & Wild Card",
            model_id="gpt-4o-mini",
            specific_instructions=[
                "Serve as a creative catalyst for the board",
                "Think outside conventional boundaries",
                "Connect disparate ideas and opportunities",
                "Challenge assumptions while respecting doctrine"
            ]
        )
        
        return board