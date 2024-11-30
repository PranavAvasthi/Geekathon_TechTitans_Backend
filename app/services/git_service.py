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
            all_authors = set()
            
            for commit in repo.iter_commits():
                author_info = {
                    "name": commit.author.name,
                    "email": commit.author.email
                }
                all_authors.add(str(author_info))
                author_commits[commit.author.name] += 1
            
            top_authors = []
            for author_name, commit_count in author_commits.most_common(10):
                author_email = None
                for author_str in all_authors:
                    author_dict = eval(author_str)
                    if author_dict["name"] == author_name:
                        author_email = author_dict["email"]
                        break
                
                top_authors.append({
                    "name": author_name,
                    "email": author_email,
                    "commit_count": commit_count
                })
            
            commits_data = []
            for commit in list(repo.iter_commits())[:10]:
                commits_data.append({
                    "hash": commit.hexsha,
                    "author": commit.author.name,
                    "date": datetime.fromtimestamp(commit.committed_date).isoformat(),
                    "message": commit.message.strip(),
                    "lines_changed": commit.stats.total["lines"]
                })
            
            total_commits = sum(1 for _ in repo.iter_commits())
            
            stats = {
                "repository_url": repo_url,
                "total_commits": total_commits,
                "total_authors": len(all_authors),
                "top_authors": top_authors,
                "latest_commits": commits_data
            }
            
            return stats
            
        except Exception as e:
            raise Exception(f"Error analyzing repository: {str(e)}")
            
        finally:
            self._clean_temp_dir(repo_path)