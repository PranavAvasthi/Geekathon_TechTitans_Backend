from fastapi import APIRouter, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from app.services.git_service import GitService
from app.services.github_service import GithubService

router = APIRouter()

class RepoRequest(BaseModel):
    url: str

@router.post("/commits")
async def analyze_repository(request: RepoRequest):
    try:
        git_service = GitService()
        stats = git_service.analyze_repository(request.url)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pull-requests")
async def get_pull_requests(request: RepoRequest):
    try:
        github_service = GithubService()
        stats = github_service.get_pull_requests(request.url)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/commits/{username}")
async def get_user_activity(username: str, request: RepoRequest):
    try:
        github_service = GithubService()
        stats = github_service.get_user_activity(request.url, username)
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))