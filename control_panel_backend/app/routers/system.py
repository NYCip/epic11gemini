from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import redis.asyncio as aioredis
from typing import List
import json
from datetime import datetime

from ..database import get_db
from .. import models, schemas
from ..auth import auth_service
from ..dependencies import get_redis

router = APIRouter()

async def log_audit(
    db: Session,
    user_id: str,
    action: str,
    resource: str = None,
    details: dict = None
):
    """Log an audit entry"""
    audit_entry = models.AuditLog(
        user_id=user_id,
        action=action,
        resource=resource,
        details=details
    )
    db.add(audit_entry)
    db.commit()

@router.post("/override/halt", response_model=dict)
async def halt_system(
    request: schemas.SystemOverrideRequest,
    background_tasks: BackgroundTasks,
    current_user: models.Users = Depends(auth_service.require_role([models.UserRole.ADMIN])),
    db: Session = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    """
    EDWARD OVERRIDE ALPHA - Emergency system halt
    Only accessible by admin users
    """
    # Verify confirmation code for extra security
    if request.confirmation_code != "EDWARD-ALPHA-OVERRIDE":
        raise HTTPException(status_code=403, detail="Invalid confirmation code")
    
    # Set system halt status in Redis
    await redis.set("EDWARD_OVERRIDE_STATUS", "HALT")
    await redis.publish("edward_override_channel", json.dumps({
        "action": "HALT",
        "initiated_by": str(current_user.id),
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    # Log the override
    override_entry = models.SystemOverride(
        status="HALT",
        initiated_by=current_user.id,
        reason=request.reason
    )
    db.add(override_entry)
    db.commit()
    
    # Audit log
    background_tasks.add_task(
        log_audit,
        db,
        current_user.id,
        "SYSTEM_HALT",
        "system_override",
        {"reason": request.reason}
    )
    
    return {
        "message": "EDWARD OVERRIDE ALPHA activated. System HALTED.",
        "status": "HALT",
        "initiated_by": current_user.email,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/override/resume", response_model=dict)
async def resume_system(
    request: schemas.SystemOverrideRequest,
    background_tasks: BackgroundTasks,
    current_user: models.Users = Depends(auth_service.require_role([models.UserRole.ADMIN])),
    db: Session = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis)
):
    """Resume system operations after halt"""
    # Clear halt status
    await redis.set("EDWARD_OVERRIDE_STATUS", "ACTIVE")
    await redis.publish("edward_override_channel", json.dumps({
        "action": "RESUME",
        "initiated_by": str(current_user.id),
        "timestamp": datetime.utcnow().isoformat()
    }))
    
    # Log the resume
    override_entry = models.SystemOverride(
        status="RESUME",
        initiated_by=current_user.id,
        reason=request.reason
    )
    db.add(override_entry)
    db.commit()
    
    # Audit log
    background_tasks.add_task(
        log_audit,
        db,
        current_user.id,
        "SYSTEM_RESUME",
        "system_override",
        {"reason": request.reason}
    )
    
    return {
        "message": "System operations resumed.",
        "status": "ACTIVE",
        "initiated_by": current_user.email,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/status", response_model=schemas.SystemStatus)
async def get_system_status(
    current_user: models.Users = Depends(auth_service.get_current_active_user),
    redis: aioredis.Redis = Depends(get_redis),
    app_state = Depends(lambda: app.state)
):
    """Get current system status"""
    override_status = await redis.get("EDWARD_OVERRIDE_STATUS") or "ACTIVE"
    
    # Check service health
    services = {
        "control_panel": "healthy",
        "redis": "healthy" if await redis.ping() else "unhealthy",
        "database": "healthy",  # Add actual health check
        "agno_service": await redis.get("agno_service_health") or "unknown",
        "mcp_server": await redis.get("mcp_server_health") or "unknown"
    }
    
    uptime = time.time() - app_state.start_time
    
    return schemas.SystemStatus(
        status=override_status,
        services=services,
        uptime=uptime
    )

@router.get("/audit/logs", response_model=List[schemas.AuditLogEntry])
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    current_user: models.Users = Depends(
        auth_service.require_role([models.UserRole.ADMIN, models.UserRole.OPERATOR])
    ),
    db: Session = Depends(get_db)
):
    """Retrieve audit logs (admin and operator only)"""
    logs = db.query(models.AuditLog)\
        .order_by(models.AuditLog.timestamp.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    return logs
