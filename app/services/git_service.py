import os
import shutil
from git import Repo # type: ignore
from datetime import datetime
from collections import Counter

class GitService:
    def __init__(self):
        self.temp_dir = "temp_repos"
        
    def _create_temp_dir(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
            
    def _clean_temp_dir(self, repo_path):
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            
    def analyze_repository(self, repo_url):
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_path = os.path.join(self.temp_dir, repo_name)
        
        try:
            self._create_temp_dir()
            self._clean_temp_dir(repo_path)
            
            repo = Repo.clone_from(repo_url, repo_path)
            
            author_commits = Counter()
            author_details = {}
            
            for commit in repo.iter_commits():
                author_name = commit.author.name
                author_email = commit.author.email
                
                author_commits[author_name] += 1
                author_details[author_name] = {
                    "name": author_name,
                    "email": author_email
                }
            
            authors_data = [
                {
                    "name": author_name,
                    "email": author_details[author_name]["email"],
                    "commit_count": commit_count
                }
                for author_name, commit_count in sorted(
                    author_commits.items(),
                    key=lambda x: (-x[1], x[0].lower()) 
                )
            ]
            
            # Get all commits
            commits_data = []
            for commit in list(repo.iter_commits()):
                commits_data.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "author_email": commit.author.email,
                    "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    "message": commit.message.strip(),
                    "lines_changed": commit.stats.total["lines"]
                })
            
            total_commits = sum(1 for _ in repo.iter_commits())
            
            stats = {
                "repository_url": repo_url,
                "total_commits": total_commits,
                "total_authors": len(authors_data),
                "authors": authors_data, 
                "commits": commits_data
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error analyzing repository: {str(e)}")
            
        finally:
            self._clean_temp_dir(repo_path)