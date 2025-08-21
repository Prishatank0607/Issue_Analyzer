import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import git
import requests
from config import Config

class GitHubParser:
    """Handles GitHub repository parsing and file extraction."""
    
    def __init__(self):
        self.config = Config()
        self.temp_dir = None
        
    def parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner and repo name."""
        try:
            # Handle different GitHub URL formats
            if url.endswith('.git'):
                url = url[:-4]
            
            if 'github.com' not in url:
                raise ValueError("Invalid GitHub URL")
                
            parts = url.replace('https://github.com/', '').replace('http://github.com/', '').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid GitHub URL format")
                
            return {
                'owner': parts[0],
                'repo': parts[1],
                'full_url': f"https://github.com/{parts[0]}/{parts[1]}.git"
            }
        except Exception as e:
            raise ValueError(f"Failed to parse GitHub URL: {str(e)}")
    
    def clone_repository(self, repo_url: str) -> str:
        """Clone GitHub repository to temporary directory."""
        try:
            self.temp_dir = tempfile.mkdtemp()
            print(f"Cloning repository to: {self.temp_dir}")
            
            git.Repo.clone_from(repo_url, self.temp_dir)
            return self.temp_dir
        except Exception as e:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def extract_code_files(self, repo_path: str) -> List[Dict[str, str]]:
        """Extract code files from the cloned repository."""
        code_files = []
        repo_path = Path(repo_path)
        
        try:
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    # Skip hidden files, directories, and non-code files
                    if any(part.startswith('.') for part in file_path.parts):
                        continue
                    
                    # Check if file extension is supported
                    if file_path.suffix.lower() in self.config.SUPPORTED_EXTENSIONS:
                        # Check file size
                        if file_path.stat().st_size > self.config.MAX_FILE_SIZE:
                            continue
                            
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            relative_path = file_path.relative_to(repo_path)
                            code_files.append({
                                'path': str(relative_path),
                                'content': content,
                                'language': self.config.SUPPORTED_EXTENSIONS[file_path.suffix.lower()],
                                'size': len(content)
                            })
                            
                            # Limit number of files to prevent overwhelming
                            if len(code_files) >= self.config.MAX_FILES_TO_ANALYZE:
                                break
                                
                        except (UnicodeDecodeError, PermissionError):
                            # Skip files that can't be read
                            continue
                            
        except Exception as e:
            print(f"Error extracting files: {str(e)}")
            
        return code_files
    
    def cleanup(self):
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print("Cleaned up temporary directory")
            except Exception as e:
                print(f"Error cleaning up: {str(e)}")
    
    def get_repository_info(self, repo_url: str) -> Dict:
        """Get basic repository information."""
        try:
            parsed = self.parse_github_url(repo_url)
            api_url = f"https://api.github.com/repos/{parsed['owner']}/{parsed['repo']}"
            
            response = requests.get(api_url)
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'name': repo_data.get('name', ''),
                    'description': repo_data.get('description', ''),
                    'language': repo_data.get('language', ''),
                    'stars': repo_data.get('stargazers_count', 0),
                    'forks': repo_data.get('forks_count', 0),
                    'size': repo_data.get('size', 0)
                }
        except Exception as e:
            print(f"Error getting repository info: {str(e)}")
            
        return {}
