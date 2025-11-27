from pydantic import BaseModel, HttpUrl
from typing import Any, Dict, List, Optional, Literal

class SubmitRequest(BaseModel):
    input_type: Literal["url"] = "url"
    input_value: HttpUrl

class SubmitResponse(BaseModel):
    request_id: str
    status: str

class MatchHit(BaseModel):
    file_path: str
    source_repo: str
    source_owner: str
    source_url: str
    matched_lines: List[str]
    confidence: float
    fingerprint_match: bool = True

class RepoCopyStat(BaseModel):
    source_owner: str
    source_repo: str
    source_repo_url: str
    matched_files: int
    total_profile_files: int
    similarity_percent: float
    label: str

class ResultPayload(BaseModel):
    profile: str
    total_files_checked: int
    hits: List[MatchHit]
    repo_stats: List[RepoCopyStat]
    explanations: Optional[Dict[str, Any]] = None

class RequestStatusResponse(BaseModel):
    request_id: str
    status: str
    stage: str
    progress: float
    created_at: str
    results: Optional[ResultPayload] = None
    error_message: Optional[str] = None
