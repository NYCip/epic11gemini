from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from phi.playground import Playground
from phi.agent import Agent
from phi.team import Team
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
import os
import logging
import asyncio
from typing import Dict, List, Optional
import json

from .agent_factory import AgentFactory
from .risk_management import RiskAssessment, RiskLevel
from .tools.mcp_tools import MCPToolkit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global board instance
board_of_directors: Optional[Dict] = None
epic_team: Optional[Team] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize board on startup"""
    global board_of_directors, epic_team
    
    # Initialize Redis
    app.state.redis = await aioredis.from_url(
        os.getenv("REDIS_URL", "redis://redis:6379"),
        encoding="utf-8", 
        decode_responses=True
    )
    
    # Check for system override
    override_status = await app.state.redis.get("EDWARD_OVERRIDE_STATUS")
    if override_status == "HALT":
        logger.error("SYSTEM HALTED by EDWARD OVERRIDE - Refusing to start")
        raise RuntimeError("System halted by Edward Override")
    
    # Initialize agent factory
    factory = AgentFactory()
    
    # Create all board members
    logger.info("Initializing EPIC Board of Directors...")
    board_of_directors = factory.create_board_of_directors()
    
    # Create collaborative team
    epic_team = Team(
        name="EPIC Board of Directors",
        agents=list(board_of_directors.values()),
        instructions=[
            "You are the EPIC Board of Directors serving Edward Ip",
            "Major decisions require 7/11 board member consensus",
            "CSO, CRO, and CQO have veto power for high-risk actions",
            "Every action must prioritize Edward and his family's interests"
        ]
    )
    
    # Subscribe to override channel
    pubsub = app.state.redis.pubsub()
    await pubsub.subscribe("edward_override_channel")
    
    # Start override listener
    asyncio.create_task(override_listener(pubsub, app))
    
    # Report health
    await app.state.redis.set("agno_service_health", "healthy")
    
    logger.info("EPIC Board of Directors initialized successfully")
    
    yield
    
    # Cleanup
    await pubsub.unsubscribe("edward_override_channel")
    await app.state.redis.close()

async def override_listener(pubsub, app):
    """Listen for Edward Override commands"""
    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                if data['action'] == 'HALT':
                    logger.critical("EDWARD OVERRIDE RECEIVED - HALTING ALL OPERATIONS")
                    # Implement graceful shutdown
                    app.state.halted = True
                elif data['action'] == 'RESUME':
                    logger.info("System resume command received")
                    app.state.halted = False
            except Exception as e:
                logger.error(f"Error processing override: {e}")

app = FastAPI(
    title="EPIC V11 AGNO Service",
    description="AI Board of Directors for Edward Ip",
    version="11.0.0",
    lifespan=lifespan
)

# Create Playground interface
playground = Playground(agents=list(board_of_directors.values()) if board_of_directors else [])
app.mount("/", playground.get_app())

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agno_service",
        "board_members": len(board_of_directors) if board_of_directors else 0
    }

@app.post("/board/decision")
async def board_decision(
    task: dict,
    background_tasks: BackgroundTasks,
    redis = Depends(lambda: app.state.redis)
):
    """Submit a task for board decision with risk assessment"""
    
    # Check if system is halted
    if hasattr(app.state, 'halted') and app.state.halted:
        raise HTTPException(status_code=503, detail="System halted by Edward Override")
    
    # Collect risk assessments from relevant board members
    assessments: List[RiskAssessment] = []
    
    # Key members must assess
    key_members = ["CEO", "CQO", "CSO", "CRO"]
    
    for member_key in key_members:
        member = board_of_directors[member_key]
        assessment = await member.assess_risk(task)
        if assessment:
            assessments.append(assessment)
    
    # Get board consensus
    risk_framework = board_of_directors["CEO"].risk_framework
    approved, reason = await risk_framework.get_board_consensus(assessments)
    
    # Log decision
    decision_log = {
        "task": task,
        "assessments": [a.model_dump() for a in assessments],
        "approved": approved,
        "reason": reason
    }
    
    background_tasks.add_task(
        redis.lpush,
        "board_decisions",
        json.dumps(decision_log)
    )
    
    if not approved:
        raise HTTPException(status_code=403, detail=f"Board rejected: {reason}")
    
    # Execute through team if approved
    response = await epic_team.run(task.get("query", ""))
    
    return {
        "approved": approved,
        "reason": reason,
        "response": response,
        "risk_assessments": [a.model_dump() for a in assessments]
    }
