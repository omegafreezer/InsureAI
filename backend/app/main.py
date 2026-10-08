from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import auth, claims, dashboard, audit
from .seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield


app = FastAPI(
    title="InsureAI Claims Risk & Fraud Platform",
    version="1.0.0",
    description="Enterprise-style P&C insurance claims risk, fraud detection and workflow API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(claims.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(audit.router, prefix="/api")


@app.get("/")
def root():
    return {"service": "InsureAI", "status": "healthy", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
