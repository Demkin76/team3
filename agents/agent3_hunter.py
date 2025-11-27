import logging
from collections import defaultdict
from sqlalchemy.orm import Session

from core.config import settings
from db.database import SessionLocal
from db.models import ParsedPrompt, Result, SitesCache
from services.status import update_status
from services.github_search import search_code
from services.fingerprints import file_fingerprint
from utils.github import get_file_content

log = logging.getLogger("agent3")

def _label_for_percent(p: float) -> str:
    if p >= settings.REPO_COPY_THRESHOLD:
        return "copy"
    if p >= settings.REPO_STRONG_THRESHOLD:
        return "strong"
    return "partial"

async def agent3_run(request_id: str):
    db: Session = SessionLocal()
    try:
        parsed = db.get(ParsedPrompt, request_id)
        if not parsed:
            return
        jp = parsed.json_prompt

        update_status(db, request_id, "searching", "agent3", 0.7)

        hits = []
        searched_files = 0
        total_profile_files = jp.get("total_files", 0)

        for repo in jp.get("repos", []):
            for f in repo.get("files", []):
                if searched_files >= settings.SEARCH_FILES_LIMIT:
                    break
                searched_files += 1

                orig_fp = f.get("fingerprint")

                for line in f.get("lines_for_search", []):
                    query = f'"{line}"'
                    try:
                        items = await search_code(query, token=settings.GITHUB_TOKEN, per_page=5)
                    except Exception:
                        items = []

                    for it in items:
                        rep = it.get("repository", {}) or {}
                        full_name = rep.get("full_name")
                        if full_name == f'{repo["owner"]}/{repo["repo"]}':
                            continue

                        fp_match = False
                        try:
                            src_owner = rep.get("owner", {}).get("login")
                            src_repo = rep.get("name")
                            src_path = it.get("path")
                            if src_owner and src_repo and src_path:
                                src_content = await get_file_content(src_owner, src_repo, src_path, token=settings.GITHUB_TOKEN)
                                src_fp = file_fingerprint(src_content)
                                fp_match = (src_fp == orig_fp)
                        except Exception:
                            fp_match = False

                        if not fp_match:
                            continue

                        hits.append({
                            "file_path": f["path"],
                            "source_repo": rep.get("name"),
                            "source_owner": rep.get("owner", {}).get("login"),
                            "source_url": it.get("html_url"),
                            "matched_lines": [line],
                            "confidence": 1.0,
                            "fingerprint_match": True
                        })

        update_status(db, request_id, "ranking", "agent3", 0.9)

        by_repo = defaultdict(set)
        repo_url = {}

        for h in hits:
            key = (h["source_owner"], h["source_repo"])
            by_repo[key].add(h["file_path"])
            if h.get("source_url"):
                repo_url[key] = "/".join(h["source_url"].split("/")[:5])

        repo_stats = []
        for (owner, repo_name), matched_paths in by_repo.items():
            matched_files = len(matched_paths)
            sim_percent = (matched_files / total_profile_files * 100.0) if total_profile_files else 0.0
            repo_stats.append({
                "source_owner": owner,
                "source_repo": repo_name,
                "source_repo_url": repo_url.get((owner, repo_name)) or f"https://github.com/{owner}/{repo_name}",
                "matched_files": matched_files,
                "total_profile_files": total_profile_files,
                "similarity_percent": round(sim_percent, 2),
                "label": _label_for_percent(sim_percent)
            })

        repo_stats.sort(key=lambda x: x["similarity_percent"], reverse=True)

        results = {
            "profile": jp.get("profile_url"),
            "total_files_checked": total_profile_files,
            "hits": hits,
            "repo_stats": repo_stats,
            "explanations": {
                "note": "Only exact file fingerprint matches are counted. Repo similarity is matched_files / total_files_checked."
            }
        }

        db.merge(Result(request_id=request_id, analogs=results))
        db.commit()

        db.add(SitesCache(
            normalized_json_prompt=jp,
            embedding=None,
            analogs=results
        ))
        db.commit()

        update_status(db, request_id, "done", "done", 1.0)

    except Exception as e:
        log.exception("agent3 error: %s", e)
        update_status(db, request_id, "error", "agent3", 1.0, error_message=str(e))
    finally:
        db.close()
