from pydantic import BaseModel


class StudioStat(BaseModel):
    name: str
    count: int
    ratio: float