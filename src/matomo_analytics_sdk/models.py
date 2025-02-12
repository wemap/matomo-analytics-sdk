from pydantic import BaseModel


class Config(BaseModel):
    base_url: str
    site_id: str
    auth_token: str
    module: str = "API"
    period: str = "day"
    date: str = "today"
    filter_limit: str = "100"
    format: str = "JSON"
    format_metrics: str = "0"
