from fastapi import FastAPI # type: ignore
from app.routers import git
from dotenv import load_dotenv # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

load_dotenv()

app = FastAPI(title="Git Repository Analyzer")

app.include_router(git.router, prefix="/api/v1", tags=["git"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],  
)

if __name__ == "__main__":
    import uvicorn # type: ignore
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)