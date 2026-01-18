"""
Relay Gateway - Main FastAPI application.

The Gateway is the Policy Decision Point (PDP) that:
1. Validates agent action manifests
2. Evaluates policies via OPA
3. Issues cryptographic seals
4. Maintains audit trail
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from gateway.config import get_settings
from gateway.db.session import DatabaseManager, DatabaseConfig
from gateway.api.v1 import manifest, seal, audit, orgs, agents

# Global database manager
db_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Initializes and cleans up resources.
    """
    global db_manager

    settings = get_settings()

    # Initialize database
    db_config = DatabaseConfig(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        username=settings.db_user,
        password=settings.db_password,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )

    db_manager = DatabaseManager(db_config)
    db_manager.initialize()

    # Make db_manager available to session.py
    import gateway.db.session as session_module
    session_module.db_manager = db_manager

    print(f"✅ {settings.app_name} v{settings.app_version} started")
    print(f"📊 Database: {settings.db_host}:{settings.db_port}/{settings.db_name}")
    print(f"🛡️  OPA: {settings.opa_url}")

    yield

    # Cleanup
    if db_manager:
        db_manager.close()
    print("👋 Relay Gateway shutdown")


# Create FastAPI app
app = FastAPI(
    title="Relay Gateway",
    description="Agent governance system with cryptographic proofs and audit trails",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(manifest.router)
app.include_router(seal.router)
app.include_router(audit.router)
app.include_router(orgs.router)
app.include_router(agents.router)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Relay Gateway",
        "version": "1.0.0",
        "description": "Agent governance with cryptographic proofs",
        "endpoints": {
            "validate": "POST /v1/manifest/validate",
            "verify": "GET /v1/seal/verify",
            "audit": "GET /v1/audit/query",
            "health": "GET /v1/manifest/health",
            "register_org": "POST /v1/orgs/register",
            "get_org": "GET /v1/orgs/{org_id}",
            "register_agent": "POST /v1/agents/register",
            "list_agents": "GET /v1/agents",
        },
    }


@app.get("/health")
async def health():
    """Overall health check."""
    from gateway.core.policy_engine import PolicyEngine
    from sqlalchemy import text

    policy_engine = PolicyEngine(opa_url=settings.opa_url)
    opa_healthy = policy_engine.health_check()

    # Check database
    db_healthy = False
    if db_manager:
        try:
            with db_manager.get_session() as session:
                session.execute(text("SELECT 1"))
                db_healthy = True
        except Exception:
            pass

    overall_healthy = opa_healthy and db_healthy

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "components": {
            "database": "healthy" if db_healthy else "unhealthy",
            "opa": "healthy" if opa_healthy else "unhealthy",
        },
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Ensures we fail closed on unexpected errors.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.api_workers,
    )
