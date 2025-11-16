from pathlib import Path

from pydantic import BaseModel, Field
from typing import Annotated

class Config(BaseModel):
    cogs: Annotated[list[str],Field(default_factory=list)]
    admin_role: str
    prefix: str
    token: str
    embed_color: str
    database_path: str

    def write_to_json(self) -> None:
        with open(Path(__file__).parent / 'config.json', 'w') as f:
            f.write(self.to_json())
