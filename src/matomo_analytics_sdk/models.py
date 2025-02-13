from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class Config:
    base_url: str
    site_id: str
    token_auth: str
    period: Optional[str] = None
    date: Optional[str] = None
    segment: Optional[str] = None
    filter_limit: str = "100"
    format: str = "json"
    format_metrics: str = "0"
