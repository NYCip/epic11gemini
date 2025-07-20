"""
Health check endpoint for MCP server
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

def add_health_routes(app: FastAPI):
    """Add health check routes to FastAPI app"""
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            # Add any specific health checks here
            # e.g., database connectivity, external service checks
            return JSONResponse(
                status_code=200,
                content={
                    "status": "healthy",
                    "service": "mcp_server",
                    "version": "11.0.0"
                }
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy", 
                    "service": "mcp_server",
                    "error": str(e)
                }
            )
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "EPIC V11 MCP Server",
            "status": "operational",
            "version": "11.0.0"
        }