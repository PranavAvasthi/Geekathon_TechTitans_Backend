from github import Github # type: ignore
from github.GithubException import GithubException # type: ignore
from datetime import datetime
import os

class GithubService:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        print(f"Token found: {'yes' if self.github_token else 'no'}")  # Debug print
        if not self.github_token:
            raise Exception("GITHUB_TOKEN environment variable is not set")
        self.github = Github(self.github_token)
    
    def get_pull_requests(self, repo_url):
        try:
            parts = repo_url.strip('/').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid repository URL format")
            
            owner = parts[-2]
            repo_name = parts[-1].replace('.git', '')
            
            try:
                # Get repository
                repo = self.github.get_repo(f"{owner}/{repo_name}")
            except GithubException as e:
                if e.status == 404:
                    raise Exception(f"Repository {owner}/{repo_name} not found")
                elif e.status == 403:
                    raise Exception("API rate limit exceeded. Please try again later")
                else:
                    raise Exception(f"GitHub API error: {str(e)}")
            
            pulls_data = []
            
            for pr in repo.get_pulls(state='open'):
                pulls_data.append({
                    "number": pr.number,
                    "title": pr.title,
                    "status": "open",
                    "created_at": pr.created_at.isoformat(),
                    "author": pr.user.login,
                    "url": pr.html_url
                })
            
            for pr in repo.get_pulls(state='closed'):
                pulls_data.append({
                    "number": pr.number,
                    "title": pr.title,
                    "status": "closed",
                    "created_at": pr.created_at.isoformat(),
                    "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                    "author": pr.user.login,
                    "url": pr.html_url
                })
            
            stats = {
                "repository": f"{owner}/{repo_name}",
                "total_pull_requests": len(pulls_data),
                "open_prs": sum(1 for pr in pulls_data if pr['status'] == 'open'),
                "closed_prs": sum(1 for pr in pulls_data if pr['status'] == 'closed'),
                "pull_requests": sorted(pulls_data, key=lambda x: x['number'], reverse=True)
            }
            
            return stats
            
        except Exception as e:
            raise Exception(str(e)) 

    def get_user_activity(self, repo_url: str, username: str):
        try:
            parts = repo_url.strip('/').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid repository URL format")
            
            owner = parts[-2]
            repo_name = parts[-1].replace('.git', '')
            
            try:
                repo = self.github.get_repo(f"{owner}/{repo_name}")
            except GithubException as e:
                if e.status == 404:
                    raise Exception(f"Repository {owner}/{repo_name} not found")
                elif e.status == 403:
                    raise Exception("API rate limit exceeded. Please try again later")
                else:
                    raise Exception(f"GitHub API error: {str(e)}")
            
            # Get user's commits
            commits_data = []
            try:
                commits = repo.get_commits(author=username)
                for commit in commits:
                    commits_data.append({
                        "hash": commit.sha,
                        "message": commit.commit.message,
                        "date": commit.commit.author.date.isoformat(),
                        "url": commit.html_url,
                        "changes": {
                            "additions": commit.stats.additions,
                            "deletions": commit.stats.deletions,
                            "total": commit.stats.total
                        }
                    })
            except GithubException as e:
                commits_data = []  # No commits found or error
            
            # Get user's pull requests
            prs_data = []
            for pr in repo.get_pulls(state='all'):
                if pr.user.login.lower() == username.lower():
                    prs_data.append({
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "created_at": pr.created_at.isoformat(),
                        "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
                        "merged": pr.merged,
                        "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                        "url": pr.html_url,
                        "changes": {
                            "additions": pr.additions,
                            "deletions": pr.deletions,
                            "changed_files": pr.changed_files
                        }
                    })
            
            # Prepare user statistics
            stats = {
                "repository": f"{owner}/{repo_name}",
                "username": username,
                "total_commits": len(commits_data),
                "total_pull_requests": len(prs_data),
                "contribution_summary": {
                    "total_additions": sum(c["changes"]["additions"] for c in commits_data),
                    "total_deletions": sum(c["changes"]["deletions"] for c in commits_data),
                    "total_changes": sum(c["changes"]["total"] for c in commits_data)
                },
                "commits": sorted(commits_data, key=lambda x: x["date"], reverse=True),
                "pull_requests": sorted(prs_data, key=lambda x: x["created_at"], reverse=True)
            }
            
            return stats
            
        except Exception as e:
            raise Exception(str(e))