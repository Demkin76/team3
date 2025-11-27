import logging
from sqlalchemy.orm import Session

from core.config import settings
from db.database import SessionLocal
from db.models import ParsedPrompt, Request
from services.status import update_status
from services.queue import QueueService
from services.fingerprints import file_fingerprint, extract_distinct_lines
from utils.github import parse_username, list_repos, list_repo_tree, get_file_content

log = logging.getLogger("agent1")

async def agent1_run(request_id: str):
    db: Session = SessionLocal()
    try:
        req = db.get(Request, request_id)
        if not req:
            return

        update_status(db, request_id, "parsed", "agent1", 0.2)

        username = parse_username(req.input_value)
        repos = await list_repos(username, token=settings.GITHUB_TOKEN)

        code_exts = tuple(e.strip() for e in settings.CODE_EXTENSIONS.split(",") if e.strip())
        collected = []
        total_files = 0

        for repo in repos:
            if repo.get("fork"):
                continue
            owner = repo["owner"]["login"]
            name = repo["name"]
            branch = repo.get("default_branch", "main")
            tree = await list_repo_tree(owner, name, branch, token=settings.GITHUB_TOKEN)

            files_meta = []
            for node in tree:
                if node.get("type") != "blob":
                    continue
                path = node.get("path","")
                if not path.lower().endswith(code_exts):
                    continue
                size = node.get("size") or 0
                if size > settings.MAX_FILE_BYTES:
                    continue

                try:
                    content = await get_file_content(owner, name, path, token=settings.GITHUB_TOKEN)
                except Exception:
                    continue

                fp = file_fingerprint(content)
                lines = extract_distinct_lines(content, k=settings.SEARCH_LINES_PER_FILE)
                files_meta.append({
                    "path": path,
                    "fingerprint": fp,
                    "lines_for_search": lines,
                    "size": len(content)
                })
                total_files += 1
                if total_files >= settings.MAX_FILES_PER_PROFILE:
                    break

            if files_meta:
                collected.append({
                    "repo": name,
                    "owner": owner,
                    "branch": branch,
                    "files": files_meta,
                    "html_url": repo.get("html_url")
                })

            if total_files >= settings.MAX_FILES_PER_PROFILE:
                break

        json_prompt = {
            "query_id": request_id,
            "profile_url": req.input_value,
            "username": username,
            "repos": collected,
            "total_files": total_files,
            "fingerprints": [f["fingerprint"] for r in collected for f in r["files"]],
        }

        parsed = ParsedPrompt(request_id=request_id, json_prompt=json_prompt)
        db.merge(parsed)
        db.commit()

        QueueService.get().enqueue_agent2(request_id)

    except Exception as e:
        log.exception("agent1 error: %s", e)
        update_status(db, request_id, "error", "agent1", 1.0, error_message=str(e))
    finally:
        db.close()
