from dataclasses import dataclass
from typing import Optional
import pathlib

@dataclass
class Document:
    id: int
    title: str
    file_name: str
    has_grid_tag: bool
    non_grid_duplicate_id: Optional[int] = None
    file_name_extension: Optional[str] = None
    file_name_length: Optional[int] = None


    def __post_init__(self):
        if self.file_name_extension is None:
            self.file_name_extension = pathlib.Path(self.file_name).suffix.lower()
        if self.file_name_length is None:
            self.file_name_length = len(self.file_name)
