from typing import Optional

from pydantic.dataclasses import dataclass

@dataclass
class Config:
    base_url: str
    site_id: str
    auth_token: str
    period: Optional[str] = None
    date: Optional[str] =  None
    segment: Optional[str] = None
    module: str = "API"
    filter_limit: str = "100"
    format: str = "json"
    format_metrics: str = "0"