"""
GitHub Auto-Push Service for LexiFlow.

Automatically submits new/updated HTML pages to the GitHub repository
using the GitHub Contents API. Handles city pages, blog posts,
and any other static HTML content.

Designed to be low-maintenance:
- CLI mode: `python3 github_auto_push.py --file path/to/page.html`
- Watch mode: `python3 github_auto_push.py --watch pages/`
- API mode: `POST /api/github/auto-push` (FastAPI endpoint)

Uses the existing IntegrationEngine.push_to_github() for production pushes.
"""

import os
import sys
import json
import time
import base64
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import httpx

logger = logging.getLogger(__name__)


class GitHubAutoPusher:
    """
    Auto-pushes content files to the GitHub repository.
    
    Uses GitHub Contents API for direct file creation/update.
    Supports batch operations and directory watching.
    """
    
    def __init__(self, token: str = "", repo: str = "randomrecipegenerator/LexiFlow", branch: str = "main"):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.repo = repo
        self.branch = branch
        self.api_base = f"https://api.github.com/repos/{repo}/contents"
        self._http: Optional[httpx.Client] = None
    
    def _get_client(self) -> httpx.Client:
        if self._http is None:
            self._http = httpx.Client(
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json",
                },
                timeout=30.0
            )
        return self._http
    
    def _detect_repo_path(self, file_path: str) -> str:
        """Auto-detect the repo path from a local file path."""
        path = Path(file_path)
        parts = path.parts
        for i, p in enumerate(parts):
            if p in ("backend", "cities", "pages", "blog", "tests"):
                return "/".join(parts[i:])
        return path.name
    
    def push_file(self, file_path: str, repo_path: str = "", message: str = "") -> Dict[str, Any]:
        """Push a single file to GitHub."""
        if not repo_path:
            repo_path = self._detect_repo_path(file_path)
        if not message:
            message = f"Auto-push: {repo_path}"
        
        with open(file_path, "rb") as f:
            content = f.read()
        
        client = self._get_client()
        
        # Check if file exists
        get_url = f"{self.api_base}/{repo_path}?ref={self.branch}"
        sha = ""
        try:
            resp = client.get(get_url)
            if resp.status_code == 200:
                sha = resp.json().get("sha", "")
        except Exception:
            pass
        
        data = {
            "message": message,
            "content": base64.b64encode(content).decode(),
            "branch": self.branch,
        }
        if sha:
            data["sha"] = sha
        
        put_url = f"{self.api_base}/{repo_path}"
        resp = client.put(put_url, json=data)
        
        if resp.status_code in (200, 201):
            result = resp.json()
            return {"status": "success", "path": repo_path, "sha": result.get("content", {}).get("sha", "")}
        else:
            return {"status": "error", "path": repo_path, "detail": resp.text[:500]}
    
    def push_files(self, files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Push multiple files. Each entry: {'file_path': str, 'repo_path': str, 'message': str}"""
        results = []
        for f in files:
            result = self.push_file(
                f.get("file_path", ""),
                f.get("repo_path", ""),
                f.get("message", "")
            )
            results.append(result)
        return results
    
    def start_watching(self, directory: str):
        """Watch a directory for new/updated files and push them."""
        handler = FileSystemEventHandler()
        
        def on_modified(event):
            if event.is_directory:
                return
            if event.src_path.endswith((".html", ".py", ".md", ".css", ".js")):
                repo_path = self._detect_repo_path(event.src_path)
                logger.info(f"Detected change: {event.src_path} -> {repo_path}")
                result = self.push_file(event.src_path, repo_path)
                logger.info(f"Push result: {result.get('status')}")
        
        handler.on_modified = on_modified
        handler.on_created = on_modified
        
        observer = Observer()
        observer.schedule(handler, directory, recursive=True)
        observer.start()
        logger.info(f"Watching {directory} for changes...")
        return observer


def main():
    parser = argparse.ArgumentParser(description="GitHub Auto-Push for LexiFlow")
    parser.add_argument("--file", "-f", help="Path to file to push")
    parser.add_argument("--watch", "-w", help="Directory to watch for changes")
    parser.add_argument("--message", "-m", help="Commit message", default="")
    parser.add_argument("--token", "-t", help="GitHub token (or use GITHUB_TOKEN env)")
    args = parser.parse_args()
    
    pusher = GitHubAutoPusher(token=args.token or "")
    
    if args.file:
        result = pusher.push_file(args.file, message=args.message)
        print(json.dumps(result, indent=2))
    elif args.watch:
        print(f"Watching {args.watch}... (Ctrl+C to stop)")
        observer = pusher.start_watching(args.watch)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        parser.print_help()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()