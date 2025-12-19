from typing import Optional
from pydantic import BaseModel

class Job(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    date: Optional[str] = None
    link: str
