from fastapi import FastAPI # type: ignore
from app.routers import git
from dotenv import load_dotenv # type: ignore
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Git Repository Analyzer")

app.include_router(git.router, prefix="/api/v1", tags=["git"])

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)