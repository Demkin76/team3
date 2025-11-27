import re
from typing import Any, Dict, List, Optional
import httpx
from core.config import settings

PROFILE_RE = re.compile(r"github\.com/([^/]+)/?$")

def parse_username(profile_url: str) -> str:
    m = PROFILE_RE.search(profile_url)
    if not m:
        raise ValueError("Invalid GitHub profile URL")
    return m.group(1)

def _headers(token: Optional[str]):
    h = {"Accept": "application/vnd.github+json", "User-Agent": "DoppelHunter/0.4"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

async def gh_get(path: str, token: Optional[str] = None) -> Dict[str, Any]:
    url = settings.GITHUB_API_BASE.rstrip("/") + path
    async with httpx.AsyncClient(timeout=settings.FETCH_TIMEOUT_SEC, headers=_headers(token)) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()

async def list_repos(username: str, token: Optional[str] = None) -> List[Dict[str, Any]]:
    return await gh_get(f"/users/{username}/repos?per_page=100&type=owner&sort=updated", token=token)

async def list_repo_tree(owner: str, repo: str, default_branch: str, token: Optional[str]=None) -> List[Dict[str, Any]]:
    data = await gh_get(f"/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1", token=token)
    return data.get("tree", [])

async def get_file_content(owner: str, repo: str, path: str, token: Optional[str]=None) -> str:
    data = await gh_get(f"/repos/{owner}/{repo}/contents/{path}", token=token)
    if data.get("encoding") == "base64":
        import base64
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    durl = data.get("download_url")
    if not durl:
        return ""
    async with httpx.AsyncClient(timeout=settings.FETCH_TIMEOUT_SEC, headers=_headers(token)) as client:
        r = await client.get(durl)
        r.raise_for_status()
        return r.text
