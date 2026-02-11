"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.dependencies import get_engine
from api.routes import export, instruments, simulate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load the engine on startup."""
    get_engine()
    yield


app = FastAPI(
    title="ML2 Belgian Economy Simulator",
    description="Macroeconomic simulation engine for Belgian fiscal policy experiments",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulate.router, tags=["simulation"])
app.include_router(instruments.router, tags=["instruments"])
app.include_router(export.router, tags=["export"])


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
