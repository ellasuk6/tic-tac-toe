"""Application entry point. uvicorn runs `app.main:app`."""

from fastapi import FastAPI

from app.api.v1.router import api_router

app = FastAPI(title="Ultimate Tic-Tac-Toe API", version="0.1.0")
app.include_router(api_router)
