"""标签Schema"""

from pydantic import BaseModel


class TagResponse(BaseModel):
    id: str
    name: str
    category: str

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    tags: list[TagResponse]
