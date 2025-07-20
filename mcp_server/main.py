from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
from datetime import datetime

from database import get_db, MCPTool, MCPToolLog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EPIC MCP Server", version="1.0.0")

class ToolRegistration(BaseModel):
    name: str
    version: str
    description: str
    capabilities: Dict

class VerificationRequest(BaseModel):
    tool_name: str
    capability: str
    agent_name: str

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp_server"}

@app.post("/tools/register")
async def register_tool(
    tool: ToolRegistration,
    db: Session = Depends(get_db)
):
    """Register a new tool in the MCP registry"""
    db_tool = MCPTool(
        name=tool.name,
        version=tool.version,
        description=tool.description,
        capabilities=tool.capabilities
    )
    db.add(db_tool)
    db.commit()
    return {"message": f"Tool {tool.name} registered successfully"}

@app.post("/tools/verify")
async def verify_capability(
    request: VerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify if a tool has a specific capability"""
    tool = db.query(MCPTool).filter(MCPTool.name == request.tool_name).first()
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    has_capability = request.capability in tool.capabilities.get("actions", [])
    
    # Log the verification
    log_entry = MCPToolLog(
        tool_id=tool.id,
        action="verify_capability",
        agent_name=request.agent_name,
        parameters={"capability": request.capability},
        result={"has_capability": has_capability},
        success=True
    )
    db.add(log_entry)
    db.commit()
    
    return {
        "tool_name": request.tool_name,
        "capability": request.capability,
        "verified": has_capability,
        "verified_at": datetime.utcnow().isoformat()
    }

@app.get("/tools/list")
async def list_tools(
    verified_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all registered tools"""
    query = db.query(MCPTool)
    if verified_only:
        query = query.filter(MCPTool.verified == True)
    
    tools = query.all()
    return [
        {
            "name": tool.name,
            "version": tool.version,
            "description": tool.description,
            "verified": tool.verified,
            "capabilities": tool.capabilities
        }
        for tool in tools
    ]
