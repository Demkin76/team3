import urllib.parse
from typing import Dict, Any, List, Optional
from utils.github import gh_get

async def search_code(query: str, token: Optional[str] = None, per_page: int = 5) -> List[Dict[str, Any]]:
    q = urllib.parse.quote(query)
    data = await gh_get(f"/search/code?q={q}&per_page={per_page}", token=token)
    return data.get("items", [])
